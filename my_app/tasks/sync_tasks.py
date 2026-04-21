"""External sync tasks."""

import frappe
import requests


def sync_external_api():
    """Bad: no error handling, commit without try."""
    response = requests.get("https://api.example.com/inventory")
    data = response.json()
    for item in data.get("items", []):
        frappe.db.set_value("Item", item["code"], "custom_external_qty", item["qty"])
    frappe.db.commit()
