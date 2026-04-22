"""Report API endpoints — SQL injection and performance issues."""

import frappe
from frappe import _


@frappe.whitelist()
def get_sales_report(company, from_date, to_date):
    """Bad: SQL injection via f-string, no permission check."""
    return frappe.db.sql(f"""
        SELECT customer, SUM(grand_total) as total
        FROM `tabSales Order`
        WHERE company = '{company}'
        AND transaction_date BETWEEN '{from_date}' AND '{to_date}'
        GROUP BY customer
        ORDER BY total DESC
    """, as_dict=True)


@frappe.whitelist()
def get_stock_report(warehouse, item_group=None):
    """Bad: SQL injection via % formatting, no permission check."""
    query = "SELECT item_code, actual_qty FROM `tabBin` WHERE warehouse = '%s'" % warehouse
    if item_group:
        query += " AND item_code IN (SELECT name FROM `tabItem` WHERE item_group = '%s')" % item_group
    return frappe.db.sql(query, as_dict=True)


@frappe.whitelist()
def get_custom_report(doctype, fields, filters):
    """Bad: SQL injection via .format(), no permission check, uses get_all."""
    query = "SELECT {} FROM `tab{}`".format(fields, doctype)
    if filters:
        query += " WHERE {}".format(filters)
    return frappe.db.sql(query, as_dict=True)


@frappe.whitelist()
def get_aging_report(company):
    """Bad: uses get_all (bypasses permissions), N+1 query in loop."""
    invoices = frappe.get_all("Sales Invoice",
        filters={"company": company, "outstanding_amount": [">", 0]},
        fields=["name", "customer", "outstanding_amount", "posting_date"]
    )
    result = []
    for inv in invoices:
        # Bad: N+1 — fetching full doc inside loop
        doc = frappe.get_doc("Sales Invoice", inv.name)
        customer_doc = frappe.get_doc("Customer", inv.customer)
        result.append({
            "invoice": inv.name,
            "customer": inv.customer,
            "customer_group": customer_doc.customer_group,
            "outstanding": inv.outstanding_amount,
            "credit_limit": customer_doc.credit_limit,
        })
    return result


def internal_helper():
    """Phase 4 test: frappe-call-not-whitelisted
    Defined at module scope but without @frappe.whitelist(). JS calls to this
    path get 'Not permitted' at runtime."""
    return {"internal": True}
