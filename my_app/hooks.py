app_name = "my_app"
app_title = "My Custom App"
app_publisher = "Test Company"
app_description = "A test Frappe app with intentional issues for auditing"
app_version = "0.1.0"

# DocType event overrides
doc_events = {
    "Sales Order": {
        "validate": "my_app.overrides.sales_order.validate_sales_order",
        "on_submit": "my_app.overrides.sales_order.on_submit_sales_order",
        "on_update": "my_app.overrides.sales_order.on_update_sales_order",
    },
    "Purchase Order": {
        "validate": "my_app.overrides.purchase_order.validate_purchase_order",
    },
    # Bad: using doc_events for our OWN custom DocType instead of controller methods
    "Custom Lead": {
        "validate": "my_app.crm.hooks.validate_custom_lead",
        "on_update": "my_app.crm.hooks.on_update_custom_lead",
    },
    # Phase 2 test: recursive-doc-event-trigger (lifecycle + doc_events on same DocType)
    "Recursive Doc": {
        "on_update": "my_app.events.recursive_doc_events.on_update",
    },
    # Phase 2 test: core-doc-event-perf-bottleneck (high-traffic DocType + DB in loop)
    "Sales Invoice": {
        "on_submit": "my_app.events.sales_invoice_events.on_submit",
    },
    # Tier-2 fixture: realtime-publish-in-lifecycle on a high-traffic doctype.
    "Item": {
        "validate": "my_app.audit_fixtures.realtime_spam.notify_on_validate",
    },
}

# Full controller override — dangerous
override_doctype_class = {
    "Item": "my_app.overrides.item_controller.CustomItem",
    # Phase 1 test: core-ledger-override (critical)
    "GL Entry": "my_app.overrides.gl_entry.CustomGLEntry",
    # Phase 1 test: core-controller-override (subclasses AccountsController)
    "Sales Invoice": "my_app.overrides.sales_invoice_ctrl.CustomSalesInvoice",
}

# Phase 1 test: hook-permission-query-wrong-sig (target has 2 args, expected 1)
permission_query_conditions = {
    "Sales Invoice": "my_app.permissions.sales_invoice_query",
}

# Phase 1 test: hook-override-whitelisted-missing-target (target doesn't exist)
override_whitelisted_methods = {
    "frappe.desk.reportview.get_list": "my_app.api.missing.custom_get_list",
}

# Phase 1 test: hook-install-migrate-no-error-handling (targets lack try/except)
before_install = "my_app.install_migrate.before_install"
after_migrate = "my_app.install_migrate.after_migrate"

# Scheduler events
scheduler_events = {
    "daily": [
        "my_app.tasks.daily_tasks.cleanup_old_logs",
        "my_app.tasks.daily_tasks.sync_inventory_data",
    ],
    "hourly": [
        "my_app.tasks.hourly_tasks.process_pending_orders",
        # Wired up so the get-doc-in-loop critical escalation fixture
        # (audit_fixtures/save_in_loop_no_events.py) is reachable code,
        # not dead-code-suppressed by the reachability filter.
        "my_app.audit_fixtures.save_in_loop_no_events.cleanup_stuck_runs",
        "my_app.audit_fixtures.save_in_loop_no_events.reset_attempts_on_running_jobs",
        # Heavy filtering on Customer Support Ticket — reachable so the
        # missing-index-on-read-heavy-field rule has live evidence.
        "my_app.audit_fixtures.index_underuse.queue_top_open_tickets",
        "my_app.audit_fixtures.index_underuse.list_high_priority",
        # Tier-2 fixtures — bare-string wiring keeps non-whitelisted bad
        # cases reachable for the auditor; Frappe never actually calls them
        # at runtime because they take args.
        "my_app.audit_fixtures.cache_no_invalidation.get_pricing_for_item",
        "my_app.audit_fixtures.cache_no_invalidation.get_pricing_safe",
    ],
    "cron": {
        "0 */6 * * *": [
            "my_app.tasks.sync_tasks.sync_external_api",
        ],
        "0 0 * * *": [
            "my_app.tasks.daily_tasks.missing_function_that_does_not_exist",
        ],
    },
    "all": [
        "my_app.tasks.queue_processor.process_queue",
    ],
}

# Phase 1 test: hook-fixtures-mismatch — fixture JSON files exist on disk
# (my_app/fixtures/*.json) but the `fixtures = [...]` declaration is missing.
