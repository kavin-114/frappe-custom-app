"""Audit fixture: multi-line f-string SQL injection (prod UAT 2026-05-25).

Reproduces the reported false negative — a ``frappe.db.sql()`` whose f-string
query opens on the line *after* the opening paren. The former line-anchored
regex matcher only matched when ``frappe.db.sql(`` and the ``f"`` sat on the
same line, so multi-line f-string injections went unreported while
single-line ones (see ``my_app/api/reports.py``) were caught. The rule is now
AST-based and matches the call regardless of how the query wraps across lines.

Expected rule output for this file:
- ``sql-injection-fstring``: critical finding on the ``frappe.db.sql(`` call
  line in ``overdue_cheque_count`` (multi-line implicitly-concatenated
  f-string query).
- ``sql-injection-fstring``: NO finding for ``parameterized_cheque_count`` —
  a ``%s`` placeholder with a separate values arg is the safe form.

Both functions are reachable purely via ``@frappe.whitelist()``.
"""

import frappe


@frappe.whitelist()
def overdue_cheque_count(user_cond, dept_cond):
    """Bad: multi-line f-string SQL — caller-supplied conditions are
    interpolated straight into the query string."""
    frappe.has_permission("Cheque Request", throw=True)
    return frappe.db.sql(
        f"SELECT COUNT(*) FROM `tabCheque Request` "
        f"WHERE cheque_date < %s AND status IN ('Pending Pre-Approval','Pre-Approved','Prepared','Pending Signature') "
        f"{user_cond} {dept_cond}",
        (frappe.utils.nowdate(),),
    )


@frappe.whitelist()
def parameterized_cheque_count(status):
    """Good: %s placeholder bound by a separate values arg — must NOT be
    flagged as sql-injection-fstring."""
    frappe.has_permission("Cheque Request", throw=True)
    return frappe.db.sql(
        "SELECT COUNT(*) FROM `tabCheque Request` WHERE status = %s",
        (status,),
    )
