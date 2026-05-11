"""Audit fixture: save-then-pass-doc patterns.

The base shape:
    doc = frappe.get_doc("X", name)
    doc.field = value
    doc.save()
    process_doc(doc)

This is fine when `process_doc` reads from `doc` synchronously. It becomes
a bug under three specific variants — each function below covers one.

Proposed rule IDs (none ship yet; this fixture is the spec):
- save-then-mutate-via-set-value     (critical) — caller saves, callee
  mutates the row via frappe.db.set_value / SQL, leaving `doc` stale.
- redundant-double-save              (warning)  — caller saves, callee
  also calls doc.save(); two validate / before_save runs per logical op.
- enqueue-passes-doc-object          (critical) — doc object pickled into
  a background job. Worker should receive `doc.name` and refetch.

The first function is the GOOD baseline and must NOT be flagged.
"""
from __future__ import annotations

import frappe


# GOOD ---------------------------------------------------------------------
def good_save_then_read(name: str, value: str) -> str:
    """Baseline: caller saves, callee only reads. No rule should fire."""
    doc = frappe.get_doc("Customer Support Ticket", name)
    doc.status_label = value
    doc.save()
    return _send_status_email(doc)  # read-only consumer


def _send_status_email(doc) -> str:
    # Reads doc.subject / doc.customer; never writes.
    return f"emailed {doc.customer} about {doc.subject}"


# BAD #1 — save + db.set_value leaves doc stale ----------------------------
def bad_save_then_set_value(name: str) -> None:
    """save-then-mutate-via-set-value — `doc` is stale after the set_value."""
    doc = frappe.get_doc("Customer Support Ticket", name)
    doc.status_label = "In Progress"
    doc.save()
    # Bad: bypasses the ORM; doc.priority is now divergent from the row.
    frappe.db.set_value("Customer Support Ticket", name, "priority", 1)
    _notify_owner(doc)  # reads doc.priority — wrong value


def bad_save_then_sql_update(name: str) -> None:
    """Same shape via raw SQL."""
    doc = frappe.get_doc("Customer Support Ticket", name)
    doc.status_label = "Resolved"
    doc.save()
    frappe.db.sql(
        "UPDATE `tabCustomer Support Ticket` SET priority = 1 WHERE name = %s",
        [name],
    )
    _notify_owner(doc)


def _notify_owner(doc) -> None:
    # Naive consumer that trusts doc.priority post-save.
    frappe.publish_realtime("ticket_priority", {"name": doc.name, "priority": doc.priority})


# BAD #2 — redundant double save -------------------------------------------
def bad_double_save(name: str) -> None:
    """redundant-double-save — two saves, two hook runs, one logical change."""
    doc = frappe.get_doc("Customer Support Ticket", name)
    doc.status_label = "Resolved"
    doc.save()
    _stamp_resolution(doc)  # mutates + saves again


def _stamp_resolution(doc) -> None:
    # Should be folded into the caller's single save().
    doc.resolved_at = frappe.utils.now_datetime()
    doc.save()


# BAD #3 — passing doc object into a background job ------------------------
def bad_enqueue_passes_doc(name: str) -> None:
    """enqueue-passes-doc-object — worker receives a pickled, soon-stale doc.

    Correct shape: enqueue with `name=name` and let the worker refetch.
    """
    doc = frappe.get_doc("Customer Support Ticket", name)
    doc.status_label = "Resolved"
    doc.save()
    frappe.enqueue(
        "my_app.audit_fixtures.save_then_pass_doc.process_doc_async",
        doc=doc,  # Bad: pickled doc, stale by the time the worker picks it up
        queue="long",
    )


def process_doc_async(doc) -> None:
    # Even if this is a no-op, the call site is what the rule targets.
    doc.first_responded_at = frappe.utils.now_datetime()
    doc.save()
