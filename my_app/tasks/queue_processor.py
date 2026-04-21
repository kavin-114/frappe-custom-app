"""Background queue processor."""

import frappe


def process_queue():
    """Bad: no error handling."""
    jobs = frappe.get_all("Custom Queue", filters={"status": "Pending"}, fields=["name", "task_type"])
    for job in jobs:
        doc = frappe.get_doc("Custom Queue", job.name)
        doc.run_method("execute_task")
        frappe.db.set_value("Custom Queue", job.name, "status", "Completed")

    # Direct call → live_nested_loop_query stays reachable
    from my_app.audit_fixtures.reachable import live_nested_loop_query
    live_nested_loop_query([j.name for j in jobs])

    # Dynamic dispatch → live_dynamic_target classified reachable_dynamic
    frappe.call("my_app.audit_fixtures.dynamic_dispatch.live_dynamic_target")
