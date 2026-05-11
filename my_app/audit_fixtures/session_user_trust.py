"""Audit fixture: trusting frappe.session.user for authorisation.

Proposed rule IDs:
- session-user-admin-string-check   (warning) — `if frappe.session.user == "Administrator"`
  is brittle: Administrator can be renamed via site config, and the check
  skips the actual permission system.
- session-user-allowlist-check      (warning) — hard-coded email allowlist
  for privileged ops. Use a Role, not a list of strings.
- session-user-in-filter            (info) — applying `owner = session.user`
  to filter results without a permission check; works by luck, not design.

Use `frappe.has_permission(...)` or `"Role Name" in frappe.get_roles()`.
"""
from __future__ import annotations

import frappe

# Bad: module-level allowlist used for privilege escalation decisions.
_ADMIN_EMAILS = ["admin@example.com", "owner@example.com"]


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def reset_all_passwords() -> dict:
    """session-user-admin-string-check — string comparison instead of role."""
    if frappe.session.user != "Administrator":  # Bad
        frappe.throw("Admin only")
    frappe.db.sql("UPDATE `tabUser` SET reset_password_key = NULL")
    return {"ok": True}


@frappe.whitelist()
def delete_user(target: str) -> dict:
    """session-user-allowlist-check — hard-coded email list."""
    if frappe.session.user not in _ADMIN_EMAILS:  # Bad
        frappe.throw("Not authorised")
    frappe.delete_doc("User", target, ignore_permissions=True)
    return {"ok": True}


@frappe.whitelist()
def my_unpaid_invoices() -> list[dict]:
    """session-user-in-filter — looks safe but bypasses the perm system.

    A user without "Sales Invoice" read permission can still call this and
    get back their own rows.
    """
    return frappe.get_all(
        "Sales Invoice",
        filters={"owner": frappe.session.user, "status": "Unpaid"},
        fields=["name", "outstanding_amount"],
    )


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist()
def reset_all_passwords_safe() -> dict:
    """Role-based check + permission system."""
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Not authorised")
    frappe.has_permission("User", ptype="write", throw=True)
    frappe.db.sql("UPDATE `tabUser` SET reset_password_key = NULL")
    return {"ok": True}
