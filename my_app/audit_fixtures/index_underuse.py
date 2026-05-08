"""Audit fixture: missing-index-on-read-heavy-field rule (PR #173).

`Customer Support Ticket` has `priority` (Int) and `status_label` (Data)
fields without `search_index: 1` set. Both are NOT auto-indexed (Int
and Data fieldtypes), and they're not system columns.

Functions below filter, select, and order_by these fields heavily —
≥5 read sites each, almost no writes. The analyzer should suggest
adding `search_index: 1` to both fields on the doctype JSON.
"""
import frappe


def queue_top_open_tickets() -> list[dict]:
    return frappe.get_all(
        "Customer Support Ticket",
        filters={"status_label": "Open"},
        fields=["name", "subject", "priority"],
        order_by="priority desc, modified asc",
        limit=20,
    )


def list_high_priority() -> list[str]:
    return frappe.get_all(
        "Customer Support Ticket",
        filters={"priority": 1},
        pluck="name",
    )


def list_in_progress() -> list[dict]:
    return frappe.get_all(
        "Customer Support Ticket",
        filters={"status_label": "In Progress"},
        fields=["name", "priority", "status_label"],
    )


def list_resolved_today(today_iso: str) -> list[str]:
    return frappe.get_all(
        "Customer Support Ticket",
        filters={"status_label": "Resolved", "resolved_at": [">=", today_iso]},
        pluck="name",
    )


def is_priority_one_open(name: str) -> bool:
    return bool(frappe.db.exists(
        "Customer Support Ticket",
        {"priority": 1, "status_label": "Open"},
    ))


def count_open() -> int:
    return frappe.db.count("Customer Support Ticket", {"status_label": "Open"})


def status_of(name: str) -> str:
    return frappe.db.get_value("Customer Support Ticket", name, "status_label")


def priority_of(name: str) -> int:
    return frappe.db.get_value("Customer Support Ticket", name, "priority")


def latest_open_for_customer(customer: str) -> dict | None:
    return frappe.db.get_value(
        "Customer Support Ticket",
        {"customer": customer, "status_label": "Open"},
        ["name", "priority", "status_label"],
        as_dict=True,
        order_by="priority desc",
    )


# A handful of writes — kept few so the read/write ratio stays well
# above the 3:1 threshold.
def set_priority(name: str, p: int) -> None:
    frappe.db.set_value("Customer Support Ticket", name, "priority", p)


def mark_in_progress(name: str) -> None:
    frappe.db.set_value("Customer Support Ticket", name, "status_label", "In Progress")
