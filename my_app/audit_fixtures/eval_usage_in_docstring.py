"""Audit fixture: eval()/exec() named in a docstring must NOT be flagged.

Admin-labelled false positive 4a236d16 — the former ``\\beval\\s*\\(`` /
``\\bexec\\s*\\(`` regex rules matched the text ``.eval()`` / ``exec(``
sitting inside a docstring. The matcher skipped ``#`` comment lines but not
string content, so prose that merely mentions the builtins produced critical
findings. eval-usage / exec-usage are now AST-based and only match a bare
``eval(...)`` / ``exec(...)`` builtin call.

Expected rule output for this file:
- ``eval-usage``: NO finding (the only ``eval`` token is docstring prose).
- ``exec-usage``: NO finding (the only ``exec`` token is docstring prose).

Reachable via ``@frappe.whitelist()``.
"""

import frappe


@frappe.whitelist()
def store_session_meta(session_uuid, job_id, error=None):
    """Persist session metadata, merging into any existing meta blob.

    Filters None values so callers can pass ``error=None`` without nuking a
    real error already in meta. Falls back to the legacy non-atomic
    read-modify-write on any backend that rejects ``.eval()`` (FakeCache in
    tests, exotic Redis variants), and never calls ``exec(...)`` on the
    payload. Best-effort, never raises.
    """
    frappe.only_for("System Manager")
    if not session_uuid or not job_id:
        return
    payload = {"job_id": job_id}
    if error is not None:
        payload["error"] = error
    frappe.cache().hset("session_meta", session_uuid, payload)
