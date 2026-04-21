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
}

# Full controller override — dangerous
override_doctype_class = {
    "Item": "my_app.overrides.item_controller.CustomItem",
}

# Scheduler events
scheduler_events = {
    "daily": [
        "my_app.tasks.daily_tasks.cleanup_old_logs",
        "my_app.tasks.daily_tasks.sync_inventory_data",
    ],
    "hourly": [
        "my_app.tasks.hourly_tasks.process_pending_orders",
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

# Fixtures
fixtures = ["Custom Field", "Property Setter"]
