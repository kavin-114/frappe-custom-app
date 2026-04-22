// Phase 4 tests for generic client-side JS patterns.

// --- js-db-call-in-loop -----------------------------------------------------
function refresh_stock_uoms(items) {
    // Bad: N+1 round-trip for every item.
    for (var i = 0; i < items.length; i++) {
        frappe.db.get_value("Item", items[i].item_code, "stock_uom");
    }
}

function invite_all(user_list) {
    // Bad: same pattern via forEach HOF.
    user_list.forEach(function(u) {
        frappe.call({method: "my_app.api.invite.send", args: {email: u.email}});
    });
}

// --- frappe-call-unknown-method --------------------------------------------
function load_missing() {
    // Bad: resolves into my_app/api/reports.py but function does not exist.
    frappe.call({method: "my_app.api.reports.fetch_nonexistent"});
}

// --- frappe-call-not-whitelisted -------------------------------------------
function load_unwhitelisted() {
    // Bad: resolves to my_app/api/reports.py::_internal_helper (no @whitelist).
    frappe.call({method: "my_app.api.reports.internal_helper"});
}
