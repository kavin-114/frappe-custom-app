"""Data import utilities — references helpers to make them 'used'."""

import frappe
from my_app.utils.helpers import format_currency, get_company_settings, ActiveFormatter


def import_items_from_csv(file_path):
    """Import items from CSV file."""
    formatter = ActiveFormatter()
    settings = get_company_settings(frappe.defaults.get_global_default("company"))

    import csv
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": row["code"],
                "item_name": row["name"],
                "item_group": row.get("group", "All Item Groups"),
            })
            doc.insert()

    return {"status": "done"}


def format_report_value(amount):
    """Uses format_currency from helpers."""
    return format_currency(amount, "USD")
