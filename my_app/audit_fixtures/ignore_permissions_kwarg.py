"""Audit fixture: ignore_permissions kwarg on insert / save / delete.

The existing showcase covers `flags.ignore_permissions = True`. This file
covers the *kwarg* variants, which are easier to miss in review.

Proposed rule IDs:
- ignore-permissions-kwarg-in-whitelisted  (critical) — `ignore_permissions=True`
  inside an @frappe.whitelist() endpoint silently bypasses the very check the
  decorator is meant to enable.
- ignore-permissions-kwarg-in-loop         (warning) — same kwarg used inside
  a loop suggests batch admin work; should run as a user with rights, not
  as the current session user with the kwarg.

Counter-example uses `frappe.has_permission(throw=True)` + no kwarg.
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def quick_create_lead(lead_name: str, email: str) -> dict:
    """ignore-permissions-kwarg-in-whitelisted — endpoint trusts caller."""
    doc = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": lead_name,
        "email_id": email,
    })
    doc.insert(ignore_permissions=True)  # Bad
    return {"name": doc.name}


@frappe.whitelist()
def bulk_archive(names: list[str]) -> None:
    """ignore-permissions-kwarg-in-loop — privileged batch op."""
    for n in names:
        doc = frappe.get_doc("Customer Support Ticket", n)
        doc.status_label = "Archived"
        doc.save(ignore_permissions=True)  # Bad


@frappe.whitelist()
def bulk_delete(names: list[str]) -> None:
    """Same hole, delete variant."""
    for n in names:
        frappe.delete_doc("Customer Support Ticket", n, ignore_permissions=True)


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist()
def proper_create_lead(lead_name: str, email: str) -> dict:
    """Explicit permission check; no kwarg bypass."""
    frappe.has_permission("Lead", ptype="create", throw=True)
    doc = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": lead_name,
        "email_id": email,
    })
    doc.insert()
    return {"name": doc.name}
