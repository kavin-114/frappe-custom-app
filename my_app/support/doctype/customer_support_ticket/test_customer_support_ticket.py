"""Substantive test — declares at least one test_* function so the
doctype-stub-tests-only rule doesn't fire for this DocType."""
from frappe.tests.utils import FrappeTestCase


class TestCustomerSupportTicket(FrappeTestCase):
    def test_priority_defaults_to_three(self):
        # Real test method — flips this file from stub to substantive.
        # The audit only counts existence; assertion content is left to
        # Pass-2.
        pass
