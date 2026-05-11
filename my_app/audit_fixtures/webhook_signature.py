"""Audit fixture: webhook signature verification.

Proposed rule IDs:
- webhook-no-signature-check        (critical) — @frappe.whitelist(allow_guest=True)
  endpoint named *webhook* / *callback* / *notification* that does not verify an
  HMAC signature against a shared secret before acting on the payload.
- webhook-string-compare-signature  (critical) — uses `==` instead of
  `hmac.compare_digest`, exposing the secret to timing-attack recovery.
- webhook-signature-from-payload    (critical) — pulls the signature out of
  the payload itself instead of an immutable transport header.

Counter-example uses hmac.compare_digest against frappe.request.headers.
"""
from __future__ import annotations

import hashlib
import hmac
import json

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def razorpay_webhook() -> dict:
    """webhook-no-signature-check — anyone can POST a "paid" event."""
    payload = json.loads(frappe.request.data)
    if payload.get("event") == "payment.captured":
        # Bad: mutates billing state with zero authentication.
        frappe.db.set_value("Invoice", payload["invoice"], "status", "Paid")
    return {"ok": True}


@frappe.whitelist(allow_guest=True)
def stripe_callback() -> dict:
    """webhook-string-compare-signature — equality op leaks via timing."""
    expected = frappe.conf.get("stripe_webhook_secret", "")
    signature = frappe.request.headers.get("Stripe-Signature", "")
    body = frappe.request.data
    computed = hmac.new(expected.encode(), body, hashlib.sha256).hexdigest()
    if signature != computed:  # Bad: use hmac.compare_digest
        frappe.throw("Bad signature")
    return {"ok": True}


@frappe.whitelist(allow_guest=True)
def github_notification() -> dict:
    """webhook-signature-from-payload — signature taken from attacker input."""
    payload = json.loads(frappe.request.data)
    expected = frappe.conf.get("github_webhook_secret", "")
    # Bad: signature is part of the same JSON the attacker controls.
    claimed = payload.pop("signature", "")
    body = json.dumps(payload).encode()
    computed = hmac.new(expected.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(claimed, computed):
        frappe.throw("Bad signature")
    return {"ok": True}


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def razorpay_webhook_safe() -> dict:
    """Correct shape: HMAC from immutable header + constant-time compare."""
    secret = frappe.conf.get("razorpay_webhook_secret", "")
    if not secret:
        frappe.throw("Webhook secret not configured")
    signature = frappe.request.headers.get("X-Razorpay-Signature", "")
    computed = hmac.new(
        secret.encode(), frappe.request.data, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, computed):
        frappe.throw("Invalid signature")
    payload = json.loads(frappe.request.data)
    if payload.get("event") == "payment.captured":
        frappe.db.set_value("Invoice", payload["invoice"], "status", "Paid")
    return {"ok": True}
