// Fixture for #23: frm.call against module-level whitelisted functions.
//
// The three frm.call sites below exercise the resolver's module-level
// fallback added in the post-UAT engine fix:
//   * get_module_helper      → @frappe.whitelist module fn → NO finding
//   * async_module_helper    → @frappe.whitelist async def → NO finding
//   * not_whitelisted_helper → exists but no @frappe.whitelist → still
//                              fires frm-call-not-whitelisted (not
//                              frm-call-unknown-method) because the
//                              fallback finds the function but reports
//                              whitelisted=False.
frappe.ui.form.on("Module Level Callable Doc", {
    refresh: function(frm) {
        frm.call("get_module_helper");
        frm.call("async_module_helper");
        frm.call("not_whitelisted_helper");
    }
});
