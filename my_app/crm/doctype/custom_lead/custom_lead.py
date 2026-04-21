"""Custom Lead controller — minimal, since hooks are used instead (anti-pattern)."""

import frappe
from frappe.model.document import Document


class CustomLead(Document):
    pass
