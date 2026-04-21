"""Stock management — performance issues, code quality issues."""

import frappe
import pymysql
from frappe import _
from frappe.model.document import Document


# Bad: global mutable state
global_cache = {}
COMPANY = "My Company"  # Bad: hardcoded company name


class StockManager:
    """Bad: God class — handles too many responsibilities."""

    def __init__(self, company=None):
        self.company = company or COMPANY
        self.errors = []
        self.log = []

    def reorder_items(self, warehouse=None):
        """Bad: get_doc in loop (N+1 query), set_value in loop."""
        items = frappe.get_all("Item",
            filters={"is_stock_item": 1},
            fields=["name", "item_code", "reorder_level"]
        )
        for item in items:
            # Bad: N+1 query
            doc = frappe.get_doc("Item", item.name)
            bin_qty = frappe.db.get_value("Bin",
                {"item_code": item.name, "warehouse": warehouse or self.company + " - WH"},
                "actual_qty"
            ) or 0

            if bin_qty < (doc.reorder_level or 0):
                # Bad: set_value in loop
                frappe.db.set_value("Item", item.name, "custom_needs_reorder", 1)
                self.log.append(f"Reorder needed: {item.name}")

    def update_stock_ledger(self, entries):
        """Bad: commit without try, direct SQL, nested loop query."""
        for entry in entries:
            # Bad: nested loop with DB query
            for warehouse in entry.get("warehouses", []):
                current = frappe.db.get_value("Bin",
                    {"item_code": entry["item_code"], "warehouse": warehouse},
                    "actual_qty"
                )
                new_qty = (current or 0) + entry.get("qty", 0)
                frappe.db.set_value("Bin",
                    {"item_code": entry["item_code"], "warehouse": warehouse},
                    "actual_qty", new_qty
                )

        # Bad: commit without try/except
        frappe.db.commit()

    def sync_external_stock(self, api_url):
        """Bad: uses pymysql directly, string concat in loop."""
        # Bad: direct database driver
        conn = pymysql.connect(host="localhost", user="root", database="frappe")
        cursor = conn.cursor()

        items = frappe.get_all("Item", fields=["name"])
        report = ""
        for item in items:
            # Bad: string concatenation in loop
            report += f"Item: {item.name}, Status: synced\n"

        cursor.close()
        conn.close()
        return report

    def get_valuation_report(self, company):
        """Bad: get_doc only for field access (should use get_value)."""
        items = frappe.get_all("Item", filters={"is_stock_item": 1}, fields=["name"])
        result = []
        for item in items:
            # Bad: loads full doc just to read a field
            doc = frappe.get_doc("Item", item.name)
            valuation_rate = doc.valuation_rate
            result.append({"item": item.name, "rate": valuation_rate})
        return result

    def cleanup_bins(self, warehouse):
        """Bad: too many arguments helper, assert for validation."""
        self._do_cleanup(warehouse, True, False, "all", 0, None, True, "strict", 30)

    def _do_cleanup(self, warehouse, force, dry_run, mode, threshold,
                    callback, verbose, strategy, batch_size):
        """Bad: too many parameters (9)."""
        bins = frappe.get_all("Bin", filters={"warehouse": warehouse})
        for bin in bins:
            if bin.get("actual_qty", 0) == 0:
                frappe.delete_doc("Bin", bin.name)

    def generate_report(self, filters):
        """Bad: comparison to None."""
        items = frappe.get_all("Item", filters=filters, fields=["name", "item_group"])
        for item in items:
            if item.item_group == None:
                item["item_group"] = "Uncategorized"
            if item.get("valuation_rate") != None:
                item["has_valuation"] = True
        return items

    def import_items(self, data):
        """Bad: mutable default would be caught, return in finally."""
        try:
            for row in data:
                doc = frappe.get_doc({"doctype": "Item", **row})
                doc.insert()
        except Exception:
            frappe.log_error("Import failed")
        finally:
            # Bad: return in finally swallows exceptions
            return {"status": "done"}

    def process_with_globals(self, items):
        """Bad: global keyword usage."""
        global global_cache
        global_cache = {}
        for item in items:
            global_cache[item["name"]] = item


def sync_from_raw_db(host, database):
    """Bad: pymysql direct usage."""
    conn = pymysql.connect(host=host, database=database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    return cursor.fetchall()
