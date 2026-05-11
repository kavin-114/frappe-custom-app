"""Audit fixture: background-job hygiene.

Proposed rule IDs:
- enqueue-now-true              (critical, info-with-justification)
  `frappe.enqueue(..., now=True)` runs synchronously inside the request.
  Defeats the point of enqueue() and blocks the worker that imported it.
- enqueue-missing-queue         (warning)
  Default queue is "default" with a 300s timeout. Long jobs need queue="long".
- enqueue-missing-timeout       (warning)
  No `timeout=` means a stuck external call eats the worker for 5 minutes.
- sync-work-should-enqueue      (warning)
  HTTP-touching, file-touching, or >Nx loop work executed in-request.

Counter-example at the bottom — must NOT fire.
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def regenerate_report(report_name: str) -> dict:
    """sync-work-should-enqueue — heavy DB walk + external POST in-request."""
    invoices = frappe.get_all(
        "Sales Invoice", filters={"status": "Unpaid"}, pluck="name"
    )
    summary = []
    for n in invoices:
        # Bad: per-row external call inside an HTTP request handler.
        resp = _fetch_payment_status(n)
        summary.append({"invoice": n, "status": resp.get("status")})
    return {"count": len(summary), "rows": summary}


def _fetch_payment_status(invoice: str) -> dict:
    import requests  # imported here to keep top-of-file clean
    return requests.post("https://payments.example.com/status", json={"id": invoice}).json()


@frappe.whitelist()
def trigger_export(report: str) -> dict:
    """enqueue-now-true — defeats the purpose of enqueue."""
    frappe.enqueue(
        "my_app.audit_fixtures.background_jobs.export_worker",
        report=report,
        now=True,  # Bad: synchronous; blocks the request, no isolation
    )
    return {"ok": True}


@frappe.whitelist()
def trigger_resync(group: str) -> dict:
    """enqueue-missing-queue + enqueue-missing-timeout — defaults bite."""
    frappe.enqueue(
        "my_app.audit_fixtures.background_jobs.resync_worker",
        group=group,
        # Bad: no queue= -> short queue, 300s cap; no timeout= -> 300s
    )
    return {"ok": True}


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist()
def trigger_resync_good(group: str) -> dict:
    """Correct shape: explicit long queue, explicit timeout."""
    frappe.enqueue(
        "my_app.audit_fixtures.background_jobs.resync_worker",
        group=group,
        queue="long",
        timeout=1800,
    )
    return {"ok": True}


# Workers (just need to exist; rules fire on the call site) ----------------
def export_worker(report: str) -> None:
    pass


def resync_worker(group: str) -> None:
    pass
