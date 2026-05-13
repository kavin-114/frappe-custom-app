"""Fixture for #24: ``db-update-all`` info-severity rule.

``frappe.db.update_all`` bypasses validation, doc_events, and audit-trail
hooks. The new rule surfaces every call site at info severity with a
"did you mean this?" message — bulk updates are sometimes the right
call, sometimes a controller-method-with-hooks would be safer. The
analyser does not try to judge which; it just flags the call so a
reviewer can confirm.

Expected:
  * Three ``db-update-all`` info findings (one per call site below).
  * No critical / warning findings emitted by this file (other rules
    may still fire, but those are orthogonal).
"""

from __future__ import annotations

import frappe


def mark_stale_items_inactive() -> None:
    """Bulk-flip a status flag across thousands of rows.

    ``update_all`` is appropriate here because we're flipping a denormalised
    flag, not changing core item state — no doc_events would meaningfully
    fire. The info finding nudges the reviewer to confirm that judgment.
    """
    frappe.db.update_all(
        "Item",
        {"is_stale": 1},
        filters={"last_seen_at": ("<", frappe.utils.add_days(None, -180))},
    )


def reset_sync_pending_for_all_customers() -> None:
    """Anti-pattern: bulk update bypasses on_update Customer hooks that
    cascade to linked Sales Orders. Info finding catches this so a
    reviewer notices the hook surface."""
    frappe.db.update_all("Customer", {"sync_pending": 0})


def zero_out_balance_via_update_all() -> None:
    """Worse anti-pattern: bulk-clearing a financially-significant field
    skips both the GL postings and the validation that prevents writing
    a draft Sales Invoice with cleared balances. The info rule itself
    won't block this, but flagging it surfaces for human review."""
    frappe.db.update_all(
        "Sales Invoice",
        {"outstanding_amount": 0},
        filters={"status": "Paid", "outstanding_amount": (">", 0)},
    )
