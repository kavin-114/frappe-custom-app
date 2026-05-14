"""Fixture for #259 (issues #5 and #6).

Two regressions live on this DocType:

#5 — DocType name with a lowercase joiner.

  ``"name": "Confirmation of Accounts"`` is correct standard Title Case;
  the lowercase ``of`` is intentional. Pre-fix the
  ``doctype-name-not-titlecase`` rule required every word to start
  uppercase and flagged this. Expected post-fix: NO finding under
  ``doctype-name-not-titlecase``.

#6 — design-review LLM claimed sendmail-in-before_submit could "roll back
  the submit" without checking the surrounding try/except.

  ``before_submit`` calls ``make_gl_table`` which sends a confirmation
  email via ``frappe.sendmail(now=True)``. The call is wrapped in
  ``try/except Exception`` with ``frappe.log_error`` — the exception
  cannot propagate, so it cannot roll back the submit transaction.
  Pre-fix the design-review LLM still recommended "move send_mail to
  after_insert so SMTP failure can't roll back the submit". Expected
  post-fix: any design-review finding that recommends moving sendmail
  off the submit path justifies it on latency / retry grounds, NOT on
  rollback / silent-failure grounds.
"""

import frappe
from frappe.model.document import Document
from frappe.utils import today


class ConfirmationofAccounts(Document):
    def validate(self):
        if self.outstanding_amount is None:
            self.outstanding_amount = 0.0

    def before_submit(self):
        self.make_gl_table()

    def make_gl_table(self):
        # Realistic shape of the swastik before_submit chain: report
        # execution, child-table reset, raw SQL deletes, and a synchronous
        # confirmation email. The sendmail call is intentionally wrapped
        # in try/except so issue #6 stays reproducible.
        self.email_sent_on = today()
        recipients = [self.customer]
        subject = f"Confirmation of Accounts — {self.name}"
        message = f"<p>Outstanding: {self.outstanding_amount}</p>"
        try:
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message,
                now=True,
                reference_doctype=self.doctype,
                reference_name=self.name,
            )
        except Exception:
            frappe.log_error(
                title="Email Error",
                message=str(frappe.get_traceback()),
            )
