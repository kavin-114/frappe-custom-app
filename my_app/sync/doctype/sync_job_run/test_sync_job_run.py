# Stub-only test file — fixture for the doctype-stub-tests-only rule.
# After PR #172, the finding should locate this file at the
# `class TestSyncJobRun` line below, not the controller's class line.
from frappe.tests.utils import FrappeTestCase


class TestSyncJobRun(FrappeTestCase):
    pass
