"""Audit fixture: get-doc-in-loop critical escalation (PR #172).

`Sync Job Run`'s controller declares no doc events (no validate,
before_save, on_update, etc.). When a loop hydrates the doc just to
mutate scalar fields and call `save()`, save() runs no user code —
every iteration is pure overhead.

The post-processor in pipeline-1 should escalate the loop's
get-doc-in-loop finding to **critical** with a "use frappe.db.set_value"
suggestion. Compare against the Customer Support Ticket case (which has
real validate/before_save) — that one stays warning.
"""
import frappe


def cleanup_stuck_runs() -> None:
    """Critical pattern: scalar mutation + save() on a no-events doc.

    Reproduces the policy_reader/tasks.py case from the UAT report.
    """
    very_old_stuck = frappe.get_all(
        "Sync Job Run",
        filters={"internal_state": "running"},
        fields=["name"],
    )
    for info in very_old_stuck:
        try:
            doc = frappe.get_doc("Sync Job Run", info.name)
            doc.internal_state = "failed"
            doc.error_message = "Heartbeat timed out after 30 minutes."
            doc.save()
        except Exception as e:
            frappe.log_error(str(e))
    # Explicit commit — the explicit-commit-call info rule (PR #172)
    # should fire on this line regardless of try/except wrapping.
    frappe.db.commit()


def reset_attempts_on_running_jobs() -> None:
    """Same shape, different exit field. Should also escalate."""
    for name in frappe.get_all(
        "Sync Job Run", filters={"internal_state": "running"}, pluck="name",
    ):
        doc = frappe.get_doc("Sync Job Run", name)
        doc.attempt_count = 0
        doc.save()


def update_resolved_tickets_with_doc_events(names: list[str]) -> None:
    """Counter-example: same shape but on Customer Support Ticket which
    *does* have a real validate / before_save. Should remain warning,
    not escalate to critical."""
    for n in names:
        doc = frappe.get_doc("Customer Support Ticket", n)
        doc.status_label = "Resolved"
        doc.save()
