// Phase 4 test: js-prefer-frm-call
// frappe.call here targets THIS doctype's own whitelisted method -
// frm.call would be shorter + pass the doc automatically + survive rename.
frappe.ui.form.on("Prefer Frm Call Doc", {
    custom_button: function(frm) {
        frappe.call({
            method: "my_app.doctype.prefer_frm_call_doc.prefer_frm_call_doc.compute_total"
        });
    }
});
