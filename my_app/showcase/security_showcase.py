"""Security issues showcase — covers eval/exec, inline SQL injection, XSS."""
from __future__ import annotations

import frappe

# Bad: hardcoded creds (fixture values are obviously fake — lowercase names match the rule)
api_key = "PLACEHOLDER-fake-api-key-for-auditor-fixture-do-not-use"
password = "PLACEHOLDER-fake-password-for-auditor-fixture"
token = "PLACEHOLDER-fake-token-for-auditor-fixture"


@frappe.whitelist()
def eval_expression(formula):
    """Bad: eval() on user input — remote code execution."""
    result = eval(formula)
    return {"result": result}


@frappe.whitelist()
def exec_script(script):
    """Bad: exec() on user input — remote code execution."""
    local_ns = {}
    exec(script, {}, local_ns)
    return local_ns


@frappe.whitelist()
def search_items_by_percent(item_group, limit):
    """Bad: SQL injection via inline % formatting in frappe.db.sql."""
    return frappe.db.sql("SELECT name FROM `tabItem` WHERE item_group = '%s' LIMIT %d" % (item_group, limit), as_dict=True)


@frappe.whitelist()
def search_items_by_format(doctype, filter_expr):
    """Bad: SQL injection via inline .format() in frappe.db.sql."""
    return frappe.db.sql("SELECT name FROM `tab{}` WHERE {}".format(doctype, filter_expr), as_dict=True)


@frappe.whitelist()
def show_user_message(user_supplied):
    """Bad: XSS — unsanitised f-string into msgprint."""
    frappe.msgprint(f"<b>Hello, {user_supplied}</b>")


def render_unsafe_template():
    """Bad: Jinja |safe filter in Python string."""
    return "{{ user_input | safe }}"
