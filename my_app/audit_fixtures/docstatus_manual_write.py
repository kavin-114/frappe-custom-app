"""Audit fixture: manual docstatus mutation.

Proposed rule IDs:
- docstatus-manual-write           (critical) — writing `docstatus` via
  frappe.db.set_value / frappe.db.sql bypasses submit() / cancel() and
  therefore skips on_submit / on_cancel hooks AND audit trail entries.
- amended-from-manual-write        (critical) — same hazard for the
  `amended_from` field on submittable DocTypes.

Submit / cancel must always go through doc.submit() / doc.cancel().
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
def force_submit(name: str) -> None:
    """docstatus-manual-write — skips on_submit, GL postings, validations."""
    frappe.db.set_value("Sales Invoice", name, "docstatus", 1)


def force_cancel_via_sql(name: str) -> None:
    """Same hole, raw SQL."""
    frappe.db.sql(
        "UPDATE `tabSales Invoice` SET docstatus = 2 WHERE name = %s",
        [name],
    )


def bulk_force_submit(names: list[str]) -> None:
    """Loop amplifies the blast radius."""
    for n in names:
        frappe.db.set_value("Purchase Order", n, "docstatus", 1)


def stitch_amendment_chain(child: str, parent: str) -> None:
    """amended-from-manual-write — manually points `amended_from`."""
    frappe.db.set_value("Sales Invoice", child, "amended_from", parent)


# GOOD counter-example ------------------------------------------------------
def submit_properly(name: str) -> None:
    """Routes through the ORM — hooks + ledger postings run normally."""
    doc = frappe.get_doc("Sales Invoice", name)
    doc.submit()
