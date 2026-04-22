"""Phase 3 translation test cases."""

import frappe
from frappe import _


def greet_user(name):
    # Phase 3 test: translate-fstring-in-underscore
    # f-string inside _() breaks Frappe's extractor; string never ends up in .po.
    return _(f"Hello {name}")


def announce_status(status):
    # Same rule via the frappe._() access path.
    return frappe._(f"Status: {status}")


def warn_user():
    # Phase 3 test: translate-missing-on-user-text
    frappe.msgprint("Customer is missing required fields")


def abort_workflow():
    # Same rule, throw variant.
    frappe.throw("Credit limit exceeded")


def already_translated():
    # Should NOT fire (proper _() usage).
    frappe.msgprint(_("All good"))
