// Phase 4 test: frm-call-not-whitelisted
frappe.ui.form.on("Frm Call No WL Doc", {
    custom_button: function(frm) {
        frm.call("process_row", {row_name: "abc"});
    }
});
