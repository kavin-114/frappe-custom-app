// Phase 4 test: js-save-in-refresh + js-recursive-event-trigger
frappe.ui.form.on("Recursive Doc", {
    refresh: function(frm) {
        // Bad: frm.save() inside refresh causes an infinite recursion loop.
        frm.save();

        // Bad: frm.trigger("refresh") re-fires the same handler.
        frm.trigger("refresh");
    },

    onload: function(frm) {
        // Bad: save inside onload hits the same recursion trap.
        cur_frm.save();
    }
});
