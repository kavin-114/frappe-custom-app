"""Audit fixture: realtime publication misuse.

Proposed rule IDs:
- realtime-publish-in-loop          (warning) — frappe.publish_realtime
  inside an unbounded loop floods the Redis pub/sub channel and the
  client's websocket connection. Use one summary event after the loop.
- realtime-publish-in-lifecycle     (warning) — same call inside a
  validate / before_save / on_update hook runs on every doc save.
- realtime-publish-user-payload     (info) — publishing user-controlled
  payload to a broadcast room (`user=None`); leaks data cross-tenant.

Counter-example sends one event after the loop, scoped to one user.
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def bulk_import_with_progress(rows: list[dict]) -> int:
    """realtime-publish-in-loop — one event per row, easily 10k+ per import."""
    for row in rows:
        frappe.get_doc({"doctype": "Item", **row}).insert()
        frappe.publish_realtime(  # Bad: one publish per iteration
            "import_progress",
            {"name": row.get("item_code")},
        )
    return len(rows)


def notify_on_validate(doc, method=None) -> None:
    """realtime-publish-in-lifecycle — fires on every save of every doc."""
    frappe.publish_realtime(
        "doc_validated",
        {"doctype": doc.doctype, "name": doc.name},
    )


@frappe.whitelist()
def broadcast_announcement(message: str) -> dict:
    """realtime-publish-user-payload — user message to a global room."""
    frappe.publish_realtime(
        "announcement",
        {"text": message},
        user=None,  # Bad: broadcast to all sessions including other tenants
    )
    return {"ok": True}


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist()
def bulk_import_with_summary(rows: list[dict]) -> int:
    """One event at the end, scoped to the calling user."""
    inserted = 0
    for row in rows:
        frappe.get_doc({"doctype": "Item", **row}).insert()
        inserted += 1
    frappe.publish_realtime(
        "import_complete",
        {"count": inserted},
        user=frappe.session.user,
    )
    return inserted
