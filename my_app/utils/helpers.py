"""Utility helpers — includes dead code and misc issues."""

import frappe
from frappe import _


def format_currency(amount, currency="INR"):
    """Used by other modules — should NOT be flagged as dead code."""
    return frappe.format_value(amount, {"fieldtype": "Currency", "options": currency})


def get_company_settings(company):
    """Used by other modules."""
    return frappe.db.get_value("Company", company, ["default_currency", "country"], as_dict=True)


def completely_unused_helper():
    """Dead code: never called anywhere."""
    return "this function is never used"


def another_unused_function(data):
    """Dead code: never referenced."""
    result = []
    for item in data:
        result.append(item)
    return result


class ObsoleteReportGenerator:
    """Dead code: class never referenced anywhere."""

    def __init__(self):
        self.data = []

    def generate(self):
        return self.data


class ActiveFormatter:
    """Used by other modules — should NOT be flagged."""

    def format(self, value):
        return str(value)


def deprecated_sync_method():
    """Dead code: was replaced by sync_tasks.py but never removed."""
    pass


@frappe.whitelist()
def api_format_currency(amount, currency="INR"):
    """Whitelisted — should NOT be flagged as dead code."""
    return format_currency(amount, currency)
