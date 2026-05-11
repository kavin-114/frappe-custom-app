"""Audit fixture: Jinja SSTI surface.

Proposed rule IDs:
- jinja-user-controlled-template   (critical) — user input flows into the
  *template body* of frappe.render_template / Letter Head / Print Format.
  Permits arbitrary attribute access, including Python builtins.
- jinja-safe-filter-on-user-data   (critical) — `{{ user_input | safe }}`
  in any Jinja string disables HTML escaping for attacker-controlled text.
- print-format-user-html           (warning)  — user-supplied HTML rendered
  into a Print Format / Letter Head without sanitisation.

A clean counter-example is included so the rule has a negative case.
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def render_user_template(template: str, name: str) -> str:
    """jinja-user-controlled-template — template body is attacker input."""
    ctx = {"customer": frappe.get_doc("Customer", name)}
    return frappe.render_template(template, ctx)  # Bad: SSTI


@frappe.whitelist()
def render_with_safe_filter(message: str) -> str:
    """jinja-safe-filter-on-user-data — `|safe` lets <script> through."""
    return frappe.render_template(
        "<div class='banner'>{{ msg | safe }}</div>",
        {"msg": message},
    )


@frappe.whitelist()
def issue_invoice_print(name: str, user_note: str) -> str:
    """print-format-user-html — user HTML lands inside a Print Format."""
    return frappe.get_print(
        "Sales Invoice",
        name,
        print_format="Standard",
        letterhead=None,
        no_letterhead=False,
        # Bad: user_note is HTML-concatenated into the rendered output
        style=f"<style>{user_note}</style>",
    )


# GOOD counter-example ------------------------------------------------------
def render_fixed_template(name: str) -> str:
    """Template body is a hard-coded literal; only the context is dynamic."""
    return frappe.render_template(
        "<p>Hello {{ customer.customer_name }}</p>",
        {"customer": frappe.get_doc("Customer", name)},
    )
