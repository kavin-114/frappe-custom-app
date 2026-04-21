"""Framework-fitness showcase — deprecated APIs, unsafe direct writes, bad patterns."""
from __future__ import annotations

import frappe


@frappe.whitelist()
def get_customer_via_deprecated_bean(name):
    """Bad: frappe.bean() is deprecated — use frappe.get_doc()."""
    bean = frappe.bean("Customer", name)
    return bean


@frappe.whitelist()
def get_customer_via_deprecated_get_obj(name):
    """Bad: frappe.get_obj() is deprecated — use frappe.get_doc()."""
    obj = frappe.get_obj("Customer", name)
    return obj


@frappe.whitelist()
def validate_order_with_assert(order_id, qty):
    """Bad: assert inside @frappe.whitelist — stripped with python -O."""
    assert qty > 0, "Quantity must be positive"
    assert order_id, "Order ID required"
    return {"valid": True}


def bulk_disable_items(item_codes):
    """Bad: direct SQL UPDATE bypasses lifecycle hooks."""
    frappe.db.sql("UPDATE `tabItem` SET disabled = 1 WHERE item_code IN %s", [tuple(item_codes)])


def insert_log_entry(msg):
    """Bad: direct SQL INSERT bypasses validation."""
    frappe.db.sql("INSERT INTO `tabLog Entry` (message, creation) VALUES (%s, NOW())", [msg])


def delete_old_logs():
    """Bad: direct SQL DELETE bypasses hooks."""
    frappe.db.sql("DELETE FROM `tabLog Entry` WHERE creation < '2024-01-01'")


def bypass_permissions_on_save(item_code):
    """Bad: flags.ignore_permissions = True skips permission checks."""
    doc = frappe.get_doc("Item", item_code)
    doc.flags.ignore_permissions = True
    doc.save()


def check_customer_exists_badly(customer):
    """Bad: uses get_doc just to check existence — expensive."""
    if frappe.get_doc("Customer", customer):
        return True
    return False


def get_item_name_via_get_doc(item_code):
    """Bad: loads full doc just to read .name."""
    return frappe.get_doc("Item", item_code).name
