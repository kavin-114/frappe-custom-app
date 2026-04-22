"""Phase 2 test: recursive-save-in-lifecycle (direct + indirect)."""

from frappe.model.document import Document


class RecursiveDoc(Document):
    def validate(self):
        # Direct unguarded recursion: validate -> self.save() re-enters validate.
        self.save()

    def before_save(self):
        # Indirect recursion through a helper method.
        self.recompute_totals()

    def recompute_totals(self):
        self.total = 100
        self.insert()  # unguarded persist from inside before_save
