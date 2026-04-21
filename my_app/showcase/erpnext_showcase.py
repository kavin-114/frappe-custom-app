"""ERPNext conventions showcase — deprecated or anti-pattern usage."""
from __future__ import annotations

import frappe


HARDCODED_COMPANY_A = "Acme Manufacturing Pvt Ltd"
HARDCODED_COMPANY_B = "Global Services Inc"


def run_hardcoded_company_report():
    """Bad: hardcoded company names make the app unusable for other tenants."""
    company = "Acme Manufacturing Pvt Ltd"
    return frappe.db.get_value("Company", company, "default_currency")


def restrict_to_hardcoded_role(user):
    """Bad: hardcoded role name instead of permission check."""
    if not frappe.has_role("System Manager"):
        frappe.throw("Access denied")
    if "HR Manager" not in frappe.get_roles(user):
        frappe.throw("HR access denied")
    return True


def debug_query_with_errprint(doc_name):
    """Bad: frappe.errprint() used in production code."""
    frappe.errprint(f"Processing doc: {doc_name}")
    return doc_name


def bad_client_call_in_server():
    """Bad: frappe.client.* is a web-facing API, should not be used server-side."""
    frappe.client.get_list("Item", filters={"disabled": 0})


def query_child_table_directly(parent):
    """Bad: direct SQL on child table — use doc.get("child_field")."""
    return frappe.db.sql(
        "SELECT item_code, qty FROM `tabSales Order Item` WHERE parent = %s",
        [parent],
        as_dict=True,
    )


def scheduler_with_msgprint():
    """Bad: msgprint in scheduler context — nobody sees it."""
    items = frappe.get_all("Item", filters={"disabled": 0})
    for item in items:
        frappe.msgprint(f"Processing {item.name} in daily scheduler")


def enqueue_with_msgprint():
    """Bad: msgprint inside a function that gets enqueued as background."""
    enqueue_result = frappe.msgprint("Background job dispatched")
    frappe.enqueue("my_app.showcase.erpnext_showcase.actual_worker")


def actual_worker():
    pass
