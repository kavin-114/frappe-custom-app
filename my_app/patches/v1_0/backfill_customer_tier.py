"""Counter-example patch — idempotent, error-handled, with reload_doc."""

import frappe


def execute() -> None:
    """Good shape: guard existence, reload meta first, contain failures."""
    frappe.reload_doc("Selling", "doctype", "Customer")

    for cust in frappe.get_all("Customer", pluck="name"):
        try:
            current = frappe.db.get_value("Customer", cust, "customer_group")
            if current and not frappe.db.get_value(
                "Customer", cust, "custom_tier"
            ):
                tier = "premium" if current == "VIP" else "standard"
                frappe.db.set_value("Customer", cust, "custom_tier", tier)
        except Exception:
            frappe.log_error(f"Tier backfill skipped for {cust}")
