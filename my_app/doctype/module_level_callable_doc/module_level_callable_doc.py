"""Fixture for #23: frm.call module-level whitelisted function (no FP).

The DocType controller class itself defines no methods, but the .py file
exposes a module-level @frappe.whitelist() function. Frappe accepts both
forms for frm.call("name") — class method OR module function. Pre-fix the
resolver only walked the class chain and emitted a spurious
``frm-call-unknown-method`` critical against `get_variable_pay_freq_details`
in the customer app this case is modelled on.

Expected:
  * NO ``frm-call-unknown-method`` finding for ``get_module_helper``
  * NO ``frm-call-not-whitelisted`` finding (the @frappe.whitelist
    decorator is detected via the module-level fallback)

See backend/tests/test_frm_call_validation.py for the matching regression
tests.
"""

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ModuleLevelCallableDoc(Document):
    pass


@frappe.whitelist()
def get_module_helper(payload: str | None = None) -> dict:
    """Whitelisted module-level helper invoked via frm.call("get_module_helper").

    The resolver's pre-fix behaviour reported this as undefined because it
    only inspected the controller class body. Post-fix it falls back to
    top-level FunctionDef / AsyncFunctionDef nodes.
    """
    return {"echo": payload or "default"}


@frappe.whitelist()
async def async_module_helper() -> dict:
    """Confirms the async-def variant also resolves (resolver checks both
    ``ast.FunctionDef`` and ``ast.AsyncFunctionDef``)."""
    return {"ok": True}


def not_whitelisted_helper(payload: str) -> dict:
    """Module-level but NOT whitelisted — `frm.call("not_whitelisted_helper")`
    should still fire ``frm-call-not-whitelisted`` even though the
    fallback found the function. Used by the negative .js case below."""
    return {"echo": payload}
