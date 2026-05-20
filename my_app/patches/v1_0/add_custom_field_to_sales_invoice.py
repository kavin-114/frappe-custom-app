"""Migration patch — exercises patch-hygiene rules.

Proposed rule IDs:
- patch-not-idempotent         (critical) — patch creates / inserts without
  guarding on existence. A second run (a re-deploy, a failed mid-migration)
  double-inserts or errors out.
- patch-missing-reload-doc     (warning)  — patch modifies a DocType definition
  (custom field, property setter) without calling `frappe.reload_doc(...)`
  first; the in-memory meta is stale and the change applies to the wrong
  schema.
- patch-no-error-handling      (warning)  — bare body with no try/except;
  any row failure aborts the whole migration and leaves the site half-done.
"""

import frappe


def execute() -> None:
    # Bad: no reload_doc — Custom Field meta on Sales Invoice may be stale.
    # Bad: no exists() guard — second run blows up with a duplicate insert.
    # Bad: no try/except — one bad row aborts the migration.
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Sales Invoice",
        "fieldname": "custom_tier",
        "fieldtype": "Data",
        "label": "Tier",
    }).insert()

    # Same patch also backfills — should be in its own patch entry.
    for inv in frappe.get_all("Sales Invoice", pluck="name"):
        frappe.db.set_value("Sales Invoice", inv, "custom_tier", "standard")
    frappe.db.commit()
