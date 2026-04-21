"""Regression guard: a test_*.py file whose contents would trigger unused-class,
unused-function, and commented-code rules if scanned. The analyzers must
skip test_-prefixed files entirely so none of these produce findings.

This file is intentionally named with the test_ prefix so the matcher and
the dead-code / commented-code analyzers all exclude it.
"""
from __future__ import annotations

# import frappe  — this line would trigger commented-code-line if scanned

import unittest


class TestFixtureClass(unittest.TestCase):
    """Test class never imported — would be flagged unused-class if scanned."""

    def test_nothing(self):
        pass


def helper_function_never_called():
    """Would be flagged unused-function if scanned."""
    return 1
