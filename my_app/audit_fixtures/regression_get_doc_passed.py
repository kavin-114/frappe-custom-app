"""Regression fixtures: get-doc-for-field-read MUST NOT fire when the
doc object is passed onward.

The current analyzer (engine/ast_checks.py::get_doc_field_access) flags
get_doc bindings whose only observed usage is attribute reads. It does
not check whether `doc` is passed as an argument to another function,
returned from the function, or stored in a collection — all of which
are legitimate reasons to use get_doc instead of get_value.

Each function below pairs an attribute read with one of those "outward"
uses. None of them should produce a finding once the FP is fixed.

UAT source: customer reported a finding on this exact shape:
    doc = frappe.get_doc("Doctype", name)
    doc.field = value
    doc.save()
    process_doc(doc)   # ← justifies the get_doc; analyzer is blind to it
"""
from __future__ import annotations

import frappe


# Must-not-fire: doc passed as positional argument ------------------------
def read_and_forward(name: str) -> None:
    doc = frappe.get_doc("Customer Support Ticket", name)
    _audit_log(doc.subject)        # attribute read
    _downstream_processor(doc)     # doc passed onward — justifies get_doc


# Must-not-fire: doc passed as keyword argument ---------------------------
def read_and_kwarg(name: str) -> None:
    doc = frappe.get_doc("Customer Support Ticket", name)
    summary = doc.subject          # attribute read
    frappe.enqueue(
        "my_app.audit_fixtures.regression_get_doc_passed._async_consumer",
        doc=doc,                   # justified
        summary=summary,
    )


# Must-not-fire: doc returned from the function ---------------------------
def read_and_return(name: str):
    doc = frappe.get_doc("Customer Support Ticket", name)
    if doc.status_label == "Open":
        return doc                 # caller needs the doc
    return None


# Must-not-fire: doc stored in a collection -------------------------------
def read_and_collect(names: list[str]) -> list:
    results = []
    for n in names:
        doc = frappe.get_doc("Customer Support Ticket", n)
        if doc.priority == 1:
            results.append(doc)    # caller iterates over the docs
    return results


# Must-not-fire: doc passed through a tuple/dict literal ------------------
def read_and_pack(name: str) -> tuple:
    doc = frappe.get_doc("Customer Support Ticket", name)
    label = doc.status_label
    return (label, doc)            # caller unpacks


# Must-not-fire: same pattern but with attribute write before pass --------
# Mirrors the UAT report's literal example: mutate scalar, save (justified
# by hooks), then hand off.
def read_mutate_save_forward(name: str, new_status: str) -> None:
    doc = frappe.get_doc("Customer Support Ticket", name)
    doc.status_label = new_status
    doc.save()                     # save() already exempts it via NEEDS_FULL_DOC
    _downstream_processor(doc)     # this extra hand-off must also be fine


# Downstream consumers (existence + name is enough; bodies don't matter) --
def _audit_log(value) -> None:
    frappe.logger().info(f"audit: {value}")


def _downstream_processor(doc) -> None:
    # Realistic shape: reads several fields the caller couldn't get from
    # frappe.db.get_value in one call.
    payload = {
        "name": doc.name,
        "subject": doc.subject,
        "priority": doc.priority,
        "owner": doc.owner,
    }
    frappe.logger().info(str(payload))


def _async_consumer(doc=None, summary: str = "") -> None:
    if doc:
        doc.first_responded_at = frappe.utils.now_datetime()
        doc.save()
