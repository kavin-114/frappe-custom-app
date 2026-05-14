"""Fixture for #259: Frappe link-query callbacks should NOT be flagged as
``whitelist-no-permission-check`` critical.

`frm.set_query` on the client side dispatches to a whitelisted server
function with the canonical positional signature
``(doctype, txt, searchfield, start, page_len, filters)``. Frappe's
link-query plumbing applies the caller's read scope when invoking these,
so the explicit ``frappe.has_permission`` / ``frappe.only_for`` check
the rule normally requires is redundant — even when the body uses raw
``frappe.db.sql``.

Expected rule output for this file:
- ``whitelist-no-permission-check``: NO finding for either function below.

These functions are reachable purely by virtue of the ``@frappe.whitelist()``
decorator (every whitelisted function is an entry point for the
reachability filter), so no hooks.py registration is needed.
"""

import frappe


@frappe.whitelist()
def material_class_for_item(doctype, txt, searchfield, start, page_len, filters):
    """Canonical 6-arg link-query callback returning DocType names by parent.

    Mirrors the swastik audit's ``get_item_discipline`` shape: raw
    ``frappe.db.sql`` filtered by a client-supplied parent name. Should
    be silent under ``whitelist-no-permission-check``.
    """
    return frappe.db.sql(
        "select parent from `tabMaterial Classes` where material_class = %s",
        filters.get("material_class") if filters else None,
    )


@frappe.whitelist()
def item_by_group(doctype, txt, searchfield, start, page_len, filters, **kw):
    """Same signature with a trailing ``**kwargs`` — the more permissive
    variant some teams write to absorb future Frappe param additions.
    Also recognised by the link-query signature check."""
    return frappe.db.sql(
        "select name from `tabItem` where item_group = %s and name like %s",
        ((filters or {}).get("item_group"), f"%{txt}%"),
    )
