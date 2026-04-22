"""Install / migrate hooks registered in hooks.py."""

import frappe


# Phase 1 test: hook-install-migrate-no-error-handling
# before_install lacks try/except; a single exception aborts the install
# and leaves the site half-set-up.
def before_install():
    frappe.db.sql("UPDATE `tabDocType` SET custom_flag = 1")
    frappe.db.sql("INSERT INTO `tabCustom Log` (name) VALUES ('installed')")


def after_migrate():
    # Same problem for migrations — any row with bad data aborts the whole migration.
    frappe.db.sql("UPDATE `tabItem` SET stock_uom = 'Unit' WHERE stock_uom IS NULL")
