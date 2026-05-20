"""Audit fixture: cache without invalidation.

Proposed rule IDs:
- cache-set-no-invalidation         (warning) — frappe.cache().set_value
  (or `set`) on a key with no matching `clear_value` / `delete_key` on the
  write path of the underlying data. Reads serve stale data forever.
- cache-set-no-ttl                  (warning) — same call without `expires_in_sec`;
  a Redis flush is the only way to evict.
- cache-in-loop                     (info) — cache.set_value inside a loop
  with a non-namespaced key (`"k"`) overwrites itself every iteration.

Counter-example pairs set_value with clear_value on the writer.
"""
from __future__ import annotations

import frappe


# BAD ----------------------------------------------------------------------
def get_pricing_for_item(item_code: str) -> float:
    """cache-set-no-invalidation + cache-set-no-ttl — value never refreshed."""
    key = f"pricing:{item_code}"
    cached = frappe.cache().get_value(key)
    if cached is not None:
        return cached
    price = frappe.db.get_value("Item Price", {"item_code": item_code}, "price_list_rate") or 0
    frappe.cache().set_value(key, price)  # Bad: no TTL, no write-path invalidation
    return price


@frappe.whitelist()
def update_item_price(item_code: str, rate: float) -> dict:
    """Writer that forgets to clear the cache key set above."""
    frappe.db.set_value(
        "Item Price",
        {"item_code": item_code},
        "price_list_rate",
        rate,
    )
    # Bad: no frappe.cache().delete_value(f"pricing:{item_code}")
    return {"ok": True}


@frappe.whitelist()
def warm_cache(item_codes: list[str]) -> int:
    """cache-in-loop — single key reused for every item."""
    for code in item_codes:
        price = frappe.db.get_value("Item Price", {"item_code": code}, "price_list_rate") or 0
        frappe.cache().set_value("last_price", price)  # Bad: no per-item namespace
    return len(item_codes)


# GOOD counter-example ------------------------------------------------------
def get_pricing_safe(item_code: str) -> float:
    key = f"pricing:{item_code}"
    cached = frappe.cache().get_value(key)
    if cached is not None:
        return cached
    price = frappe.db.get_value("Item Price", {"item_code": item_code}, "price_list_rate") or 0
    frappe.cache().set_value(key, price, expires_in_sec=300)
    return price


@frappe.whitelist()
def update_item_price_safe(item_code: str, rate: float) -> dict:
    frappe.db.set_value(
        "Item Price",
        {"item_code": item_code},
        "price_list_rate",
        rate,
    )
    frappe.cache().delete_value(f"pricing:{item_code}")
    return {"ok": True}
