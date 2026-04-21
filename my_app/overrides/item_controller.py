"""Full Item controller override — dangerous pattern."""

import frappe
from frappe import _
from erpnext.stock.doctype.item.item import Item


class CustomItem(Item):
    """Bad: full controller override via override_doctype_class.
    This replaces the entire Item controller — silently breaks when
    ERPNext upgrades add new methods to the base Item class.
    """

    def validate(self):
        super().validate()
        self.custom_validation()

    def custom_validation(self):
        if not self.item_group:
            frappe.throw(_("Item Group is required"))
        # Bad: get_doc in lifecycle hook
        if self.item_group:
            group_doc = frappe.get_doc("Item Group", self.item_group)
            if not group_doc.is_group:
                self.custom_leaf_group = 1

    def before_save(self):
        super().before_save()
        # Bad: commit in lifecycle hook
        frappe.db.commit()

    def on_update(self):
        super().on_update()
        # Bad: get_doc for same DocType in hook
        item = frappe.get_doc("Item", self.name)
        item.add_comment("Info", "Item updated via custom controller")
