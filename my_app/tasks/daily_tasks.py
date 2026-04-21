"""Daily scheduled tasks — scheduler validation issues."""

import frappe


def cleanup_old_logs():
    """Bad: no error handling, commit without try."""
    logs = frappe.get_all("Error Log", filters={"creation": ["<", "2024-01-01"]}, pluck="name")
    for log_name in logs:
        frappe.delete_doc("Error Log", log_name)
    frappe.db.commit()


def sync_inventory_data():
    """Good: has try/except wrapping."""
    try:
        items = frappe.get_all("Item", filters={"sync_with_external": 1})
        for item in items:
            frappe.db.set_value("Item", item.name, "last_synced", frappe.utils.now())
        frappe.db.commit()
    except Exception:
        frappe.log_error("Inventory sync failed")
        frappe.db.rollback()


# Note: missing_function_that_does_not_exist is referenced in hooks.py
# but intentionally does NOT exist here — should trigger scheduler-missing-function
