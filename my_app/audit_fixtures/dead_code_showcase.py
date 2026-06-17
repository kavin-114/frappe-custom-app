"""Audit fixture: dead-code detection on non-whitelisted functions/classes.

The engine's `dead_code_analyzer` emits `unused-function` / `unused-class`
findings (severity info) when a top-level definition is not reachable
from any Frappe entry point AND its bare name is not imported or
mentioned as a string anywhere in the codebase.

Entry-point heuristics (the analyzer treats these as alive):
- `@frappe.whitelist()` decorated functions
- functions referenced from `hooks.py` (doc_events, scheduler_events,
  install/migrate hooks, override_*)
- subclasses of `Document` / `WebsiteGenerator` / `NestedSet` / `TransactionBase`
- functions called from other reachable code
- functions whose bare name appears in a string literal (dynamic dispatch)
- functions whose bare name appears in any `from X import name`

This file pairs each entry-point shape with a "must fire" dead case so
the rule has both positive and negative anchors.
"""
from __future__ import annotations

import frappe


# ============================================================
# MUST FIRE — `unused-function` (severity: info)
# ============================================================

def truly_dead_function():
    """Plain `def`, no whitelist, no caller, no hooks mention, no
    string reference, no import. Must produce `unused-function`."""
    return 1


def another_orphan_helper(x: int) -> int:
    """Second dead helper with args — confirms the rule isn't shape-sensitive."""
    return x * 2


def _private_dead_helper():
    """Leading underscore conveys "private" but is not a reachability signal.
    Must still fire — private + unused is still dead."""
    pass


# ============================================================
# MUST FIRE — `unused-class` (severity: info)
# ============================================================

class OrphanReportBuilder:
    """Plain class, no Document subclass, never instantiated, never imported,
    no method reachable from anywhere. Must produce `unused-class`."""

    def build(self):
        return []


class DeadEnumLike:
    """Module-level constants only — still flagged: the *class* is unused."""
    OPEN = "open"
    CLOSED = "closed"


# ============================================================
# MUST NOT FIRE — alive via whitelist decorator
# ============================================================

@frappe.whitelist()
def whitelisted_alive():
    """Whitelist decorator is an entry point — exempt from dead-code."""
    return {"ok": True}


# ============================================================
# MUST NOT FIRE — alive via direct caller in this file
# ============================================================

def caller_for_helper():
    """Wired in hooks.py scheduler_events — entry point. Reaches
    `_reachable_helper` via the call graph, and keeps the dispatch
    targets below alive via string-mention reachability."""
    # Bare names in string literals are picked up by ReachabilityIndex's
    # _collect_string_mentions, so anything listed here is kept alive
    # even without a direct call.
    _DISPATCH = [
        "my_app.audit_fixtures.dead_code_showcase.dynamic_dispatch_target",
    ]
    _ = _DISPATCH  # silence "unused" linter — the literal is the point
    return _reachable_helper()


def _reachable_helper():
    """Reached from `caller_for_helper`, which itself is reached via the
    transitive chain below. Must NOT fire."""
    return 42


# ============================================================
# MUST NOT FIRE — alive via string-mention (dynamic dispatch)
# ============================================================

# Names below appear as bare strings somewhere in the codebase
# (e.g. frappe.enqueue("...dynamic_dispatch_target"), or hooks.py
# scheduler entries). The analyzer treats string mentions as alive.

def dynamic_dispatch_target():
    """Mentioned as a string in audit_fixtures/dynamic_dispatch.py via
    `frappe.call(\"my_app.audit_fixtures.dead_code_showcase.dynamic_dispatch_target\")`
    in some realistic JS code. Even without that mention here, the bare-name
    match anywhere counts. Kept here to anchor the negative case."""
    pass


# Bare-name string mentions of `truly_dead_function` should NOT appear
# anywhere in the codebase — otherwise the dead-code rule will be
# silenced. The fixture relies on that.


# ============================================================
# MUST NOT FIRE — alive via cross-file import
# ============================================================

def imported_in_data_import_module():
    """This name is `from my_app.audit_fixtures.dead_code_showcase import ...`
    in audit_fixtures/dead_code_showcase_importer.py (see sibling file).
    Importer-side keeps this alive."""
    return "alive via import"


# ============================================================
# MUST NOT FIRE — alive via enqueue-by-reference
# ============================================================

# `frappe.enqueue(fn, ...)` and `frappe.enqueue_doc(dt, name, fn, ...)` hand a
# Python callable to the background worker *by reference* (not a dotted
# string). The worker invokes it later, so the callable is reachable whenever
# the enqueuing code is. Regression for the taskstream Work Item controller,
# where `spawn_recurrence_batch` (enqueued from `after_insert`) was wrongly
# flagged `unused-function`. See `reachability._CALLABLE_ARG_APIS`.

class RecurrenceMaster(frappe.model.document.Document):
    """Document subclass — `after_insert` is a lifecycle entry point.

    Uses the fully-qualified base so this anchor adds no new import line and
    therefore does not shift the line numbers the critical-section golden pins.
    """

    def after_insert(self):
        # Enqueues the worker by reference (bare name), not a dotted string.
        frappe.enqueue(spawn_recurrence_batch_ref, queue="long", timeout=1800)


def spawn_recurrence_batch_ref():
    """Passed by reference to `frappe.enqueue` above; invoked by the worker.
    Must NOT fire `unused-function` — and its transitive helper must stay
    alive too."""
    return _recurrence_window_ref()


def _recurrence_window_ref():
    """Reached only via `spawn_recurrence_batch_ref`, which is itself reachable
    only through the enqueue-by-reference edge. Must NOT fire."""
    return 7


# ============================================================
# MUST NOT FIRE — callee of a soft-alive (string-mentioned) function
# ============================================================

# `provision_dashboard` is alive only because its dotted path is mentioned as
# a string below (a bench command, like the taskstream custom_html_block
# setup). That soft-alive signal now propagates through the call graph, so its
# private helper `_load_asset` — reached only by a direct call — must NOT fire
# `unused-function`. Regression for taskstream `_read` / `_exec_guard`. See
# `reachability.is_soft_reachable_fqn`.

_BENCH_COMMANDS = [
    "my_app.audit_fixtures.dead_code_showcase.provision_dashboard",
]


def provision_dashboard():
    """Alive only via the string mention in `_BENCH_COMMANDS` above; reaches
    `_load_asset` by a direct call."""
    return _load_asset("dashboard.html")


def _load_asset(filename):
    """Reached only from `provision_dashboard` (itself alive only via a string
    mention). Must NOT fire `unused-function`."""
    return filename


# ============================================================
# Transitive chain — reached only because hooks.py mentions
# `caller_for_helper` via a separate entry point. Without that root,
# this whole chain would go dark. Anchors the "transitive caller" path
# of the reachability index.
# ============================================================
