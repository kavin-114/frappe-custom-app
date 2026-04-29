"""Frappe-default scaffold: empty test class beside heavy_untested_invoice.

This is exactly what `bench new-doctype` writes — infrastructure with zero
assertions. Triggers the new doctype-stub-tests-only rule (warning, heavy).
"""
from frappe.tests.utils import FrappeTestCase


class TestHeavyUntestedInvoice(FrappeTestCase):
    pass
