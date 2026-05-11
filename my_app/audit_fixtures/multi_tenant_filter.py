"""Audit fixture: multi-tenant filter omission.

Proposed rule IDs:
- missing-company-filter           (warning) — get_all / get_list / db.sql
  on a company-scoped DocType (Sales Invoice, Purchase Order, GL Entry,
  Stock Ledger Entry, Payment Entry, etc.) without a `company=` filter
  in code that runs per-tenant.
- cross-company-aggregate-in-loop  (warning) — same omission inside a
  scheduler / lifecycle hook (amplified blast radius).

The "company" surface list comes from ERPNext seed data; the analyzer
should consult specs/data/erpnext_surface.yml for the canonical set.
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def list_unpaid_invoices() -> list[dict]:
    """missing-company-filter — Sales Invoice is company-scoped."""
    return frappe.get_all(
        "Sales Invoice",
        filters={"status": "Unpaid"},
        fields=["name", "customer", "outstanding_amount"],
    )


@frappe.whitelist()
def sum_gl_for_account(account: str) -> float:
    """Same hole, raw SQL variant."""
    rows = frappe.db.sql(
        "SELECT SUM(debit) FROM `tabGL Entry` WHERE account = %s",
        [account],
    )
    return float(rows[0][0] or 0)


def daily_stock_summary() -> None:
    """cross-company-aggregate-in-loop — runs in the scheduler."""
    entries = frappe.get_all(
        "Stock Ledger Entry",
        filters={"is_cancelled": 0},
        fields=["item_code", "actual_qty"],
    )
    for e in entries:
        frappe.db.set_value("Item", e.item_code, "custom_last_movement", frappe.utils.now())


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist()
def list_unpaid_invoices_for_company(company: str) -> list[dict]:
    """Explicit company filter — must NOT fire."""
    return frappe.get_all(
        "Sales Invoice",
        filters={"status": "Unpaid", "company": company},
        fields=["name", "customer", "outstanding_amount"],
    )
