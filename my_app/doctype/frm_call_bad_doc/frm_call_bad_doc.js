// Phase 4 test: frm-call-unknown-method
frappe.ui.form.on("Frm Call Bad Doc", {
    custom_button: function(frm) {
        // Bad: controller has no `do_missing_thing` — runtime failure on click.
        frm.call("do_missing_thing");
    }
});
