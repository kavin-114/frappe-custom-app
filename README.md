# Test Frappe App for Auditor Backtesting

A realistic Frappe custom app with **intentional vulnerabilities and anti-patterns** for testing the code auditor.

## Intentional Issues by Category

### Security (6+ issues)
- `@frappe.whitelist()` without permission checks (`api/inventory.py`)
- `frappe.get_all()` in whitelisted functions (bypasses permissions)
- `allow_guest=True` on write endpoints
- SQL injection via f-string, % formatting, .format() (`api/reports.py`)
- Direct pymysql usage (`inventory/stock_manager.py`)

### Performance (8+ issues)
- N+1 queries: `frappe.get_doc()` inside loops (`api/reports.py`, `stock_manager.py`)
- `frappe.db.set_value()` in loops
- Nested loop DB queries
- `frappe.get_doc()` just to read a field (should use `get_value`)
- String concatenation in loop

### Framework Fitness (6+ issues)
- `frappe.db.commit()` without try/except
- `frappe.db.commit()` in lifecycle hooks
- `frappe.db.rollback()` without re-raise
- `frappe.throw()` inside try/except (gets silenced)
- Scheduler events pointing to missing functions
- Scheduled tasks without error handling

### Code Quality (10+ issues)
- Unused imports (`stock_entry.py`)
- Mutable default arguments
- Shadowed builtins (`sum`, `list`)
- Empty except with pass
- Comparison to None with `==`
- Too many function arguments (9 params)
- Global keyword usage
- Return in finally block
- Dead code (unused functions/classes in `utils/helpers.py`)

### ERPNext Conventions (8+ issues)
- Full controller override via `override_doctype_class`
- `frappe.db.commit()` in lifecycle hook overrides
- `doc.save()` inside hook (infinite recursion)
- `frappe.get_doc(same_doctype)` in hook (cascading hooks)
- Unconditional `frappe.throw()` in hook
- Multiple DB queries in validate hook
- Child table direct append (should use `doc.append()`)
- Child table modification while iterating
- Using `doc_events` hooks for custom DocTypes (should use controller)

### Design Patterns (for LLM review)
- God class: `StockManager` handles too many responsibilities
- Missing service layer: business logic in controllers
- Hardcoded values: company name, warehouse
- Monolithic hooks.py with too many overrides

### Best-practice fixtures (`audit_fixtures/`, proposed rules)

These exercise rule IDs that don't ship yet — each file's docstring names
the proposed rule and the expected verdict.

- `save_then_pass_doc.py` — caller saves a doc, then passes it on. Good
  baseline plus three bad variants: post-save `frappe.db.set_value` (stale
  doc), redundant double-save, enqueue with the doc object instead of name.
- `background_jobs.py` — `enqueue(now=True)`, missing `queue=` / `timeout=`,
  HTTP/N+1 work that should be enqueued.
- `jinja_ssti.py` — user input in the template body of `frappe.render_template`;
  `|safe` filter on user data; user HTML inside Print Format.
- `multi_tenant_filter.py` — `get_all` / SQL on company-scoped DocTypes
  (Sales Invoice, GL Entry, Stock Ledger Entry) without a `company=` filter.
- `docstatus_manual_write.py` — `frappe.db.set_value(..., "docstatus", 1/2)`
  bypassing `submit()` / `cancel()`; manual `amended_from` stitching.
- `ignore_permissions_kwarg.py` — `insert/save/delete(ignore_permissions=True)`
  inside whitelisted endpoints and inside loops.
- `path_traversal.py` — `open(user_supplied_path)`, `frappe.get_doc("File", x)`
  without a permission check, `os.system(f"... {user_input}")`.

## Usage

Upload as a zip or point the auditor at this directory to run a full audit.
