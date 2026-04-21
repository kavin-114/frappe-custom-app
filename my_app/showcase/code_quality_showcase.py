"""Code quality showcase — bare except, print, wildcard imports."""
from __future__ import annotations

from frappe.utils import *  # Bad: star import

import frappe


def loud_debug(item_code):
    """Bad: print() used for logging instead of frappe.log_error()."""
    print("DEBUG: processing", item_code)
    print("Item:", frappe.get_doc("Item", item_code).name)
    return item_code


def swallow_everything():
    """Bad: bare except clause hides errors."""
    try:
        return frappe.db.get_value("Item", "NONEXISTENT", "name")
    except:
        return None


def bare_except_in_loop(items):
    """Bad: bare except inside loop silently skips failures."""
    results = []
    for it in items:
        try:
            results.append(frappe.get_doc("Item", it).name)
        except:
            continue
    return results
