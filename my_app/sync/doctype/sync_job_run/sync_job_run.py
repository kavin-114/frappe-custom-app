# No lifecycle hooks (validate / before_save / on_update / ...) — the
# get-doc-in-loop escalator relies on this DocType being event-less to
# promote save-in-loop findings on Sync Job Run to critical.
#
# Whitelisted endpoints are still allowed; they don't run on save() so
# they don't change the escalation outcome. The lone `retry` method
# below also nudges this DocType into the medium-logic bucket so the
# stub-test fixture (test_sync_job_run.py) actually triggers
# doctype-stub-tests-only.
import frappe
from frappe.model.document import Document


class SyncJobRun(Document):
    @frappe.whitelist()
    def retry(self):
        """Manually re-queue this run."""
        frappe.db.set_value("Sync Job Run", self.name, "internal_state", "queued")
