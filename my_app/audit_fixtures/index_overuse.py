"""Audit fixture: over-indexed-write-heavy-field rule (PR #173).

`Sync Job Run` declares `search_index: 1` on `internal_state`,
`attempt_count`, and `last_heartbeat_at` (see sync_job_run.json).

Functions in this file write those columns repeatedly via
`frappe.db.set_value` and `frappe.db.update`. Nothing reads them from
Python code. The analyzer should flag each as
`over-indexed-write-heavy-field` (warning) on the JSON file with a
suggestion to remove the index.
"""
import frappe


def mark_attempt_started(name: str) -> None:
    """One write-only update per call."""
    frappe.db.set_value("Sync Job Run", name, "internal_state", "running")
    frappe.db.set_value(
        "Sync Job Run",
        name,
        {"attempt_count": 1, "last_heartbeat_at": frappe.utils.now_datetime()},
    )


def heartbeat(name: str) -> None:
    frappe.db.set_value("Sync Job Run", name, "last_heartbeat_at", frappe.utils.now_datetime())
    frappe.db.set_value("Sync Job Run", name, "attempt_count", 2)
    frappe.db.set_value("Sync Job Run", name, "internal_state", "still-running")


def bump_attempts_bulk(group_id: str) -> None:
    frappe.db.update("Sync Job Run", {"job_name": group_id}, {"attempt_count": 3})
    frappe.db.update("Sync Job Run", {"job_name": group_id}, {"internal_state": "queued"})


def mark_success(name: str) -> None:
    frappe.db.set_value("Sync Job Run", name, "internal_state", "ok")
    frappe.db.set_value("Sync Job Run", name, "attempt_count", 0)


def mark_failed(name: str, msg: str) -> None:
    frappe.db.set_value(
        "Sync Job Run",
        name,
        {"internal_state": "failed", "attempt_count": 999},
    )


def reset_all() -> None:
    frappe.db.update("Sync Job Run", {"job_name": "%"}, {"internal_state": "fresh"})
