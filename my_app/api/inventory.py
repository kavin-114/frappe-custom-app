"""Inventory API endpoints — intentionally riddled with security issues."""

import frappe
from frappe import _


# === WHITELIST PERMISSION ISSUES ===

@frappe.whitelist()
def get_all_items(filters=None):
    """Bad: uses get_all (bypasses permissions) and no permission check."""
    return frappe.get_all("Item", filters=filters, fields=["name", "item_name", "item_group", "stock_uom"])


@frappe.whitelist()
def delete_item(item_code):
    """Bad: no permission check, destructive operation."""
    frappe.delete_doc("Item", item_code)
    return {"status": "deleted"}


@frappe.whitelist()
def update_item_price(item_code, price_list, rate):
    """Bad: no permission check, modifies pricing data."""
    doc = frappe.get_doc("Item Price", {"item_code": item_code, "price_list": price_list})
    doc.price_list_rate = rate
    doc.save()
    return {"status": "updated", "rate": rate}


@frappe.whitelist()
def bulk_update_stock(entries):
    """Bad: no permission check, bulk stock modification."""
    import json
    if isinstance(entries, str):
        entries = json.loads(entries)
    for entry in entries:
        frappe.db.set_value("Bin", entry["bin"], "actual_qty", entry["qty"])
    frappe.db.commit()
    return {"status": "ok", "count": len(entries)}


@frappe.whitelist()
def get_stock_balance(item_code, warehouse):
    """Good: has permission check."""
    frappe.has_permission("Stock Ledger Entry", throw=True)
    return frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")


@frappe.whitelist()
def get_item_list():
    """Good: simple getter with get_list (respects permissions)."""
    return frappe.get_list("Item", fields=["name", "item_name"], limit=50)


# === ALLOW_GUEST WRITE ISSUES ===

@frappe.whitelist(allow_guest=True)
def guest_submit_inquiry(item_code, quantity, email):
    """Bad: guest endpoint that creates documents."""
    doc = frappe.get_doc({
        "doctype": "Material Request",
        "material_request_type": "Purchase",
        "items": [{"item_code": item_code, "qty": quantity}],
    })
    doc.insert(ignore_permissions=True)
    doc.submit()
    return {"status": "submitted", "name": doc.name}


@frappe.whitelist(allow_guest=True)
def guest_delete_inquiry(name):
    """Bad: guest endpoint that deletes documents."""
    frappe.delete_doc("Material Request", name, ignore_permissions=True)
    return {"status": "deleted"}


@frappe.whitelist(allow_guest=True)
def guest_get_public_items():
    """OK: guest endpoint, read-only."""
    return frappe.get_list("Item", filters={"show_in_website": 1}, fields=["name", "item_name", "image"])
