"""Stock Entry controller — child table anti-patterns, code quality issues."""

import frappe
import json
import os
import sys
import re
import csv
from frappe import _
from frappe.model.document import Document


class StockEntry(Document):
    def validate(self):
        self.validate_items()
        self.calculate_totals()

    def validate_items(self):
        """Bad: child table anti-patterns."""
        # Bad: direct list append with dict instead of doc.append()
        if not self.items:
            self.items.append(dict(
                item_code="DEFAULT-ITEM",
                qty=0,
                basic_rate=0,
            ))

        # Bad: modifying child table while iterating
        for row in self.items:
            if row.qty == 0:
                self.items.remove(row)

        # Bad: delete by index
        if len(self.items) > 100:
            del self.items[100]

    def calculate_totals(self):
        """Bad: shadowed builtins, unnecessary imports above."""
        # Bad: shadowing built-in 'sum'
        sum = 0
        list = []
        for row in self.items:
            sum += row.qty * (row.basic_rate or 0)
            list.append(row.item_code)

        self.total_amount = sum

    def on_submit(self):
        """Bad: frappe.throw inside try/except with broad catch."""
        try:
            self.update_stock_ledger()
            frappe.throw(_("This is a validation message"))
        except Exception:
            pass  # Bad: empty except with pass

    def update_stock_ledger(self):
        """Bad: direct SQL in Document subclass."""
        frappe.db.sql("""
            UPDATE `tabBin`
            SET actual_qty = actual_qty + %s
            WHERE item_code = %s AND warehouse = %s
        """, (self.total_amount, self.items[0].item_code if self.items else "", self.warehouse))

    def get_item_details(self, item_code):
        """Bad: assert for validation in whitelisted context."""
        assert item_code, "Item code is required"
        return frappe.get_doc("Item", item_code)

    def bulk_add_items(self, items_data=[]):
        """Bad: mutable default argument."""
        for item in items_data:
            self.items.append({"item_code": item["code"], "qty": item["qty"]})
