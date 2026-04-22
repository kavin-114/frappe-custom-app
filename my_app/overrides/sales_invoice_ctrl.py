"""Custom Sales Invoice controller that extends ERPNext's AccountsController."""

from erpnext.controllers.accounts_controller import AccountsController


# Phase 1 test: core-controller-override (critical, LLM-validated)
# Subclassing AccountsController shadows framework behaviour and silently
# breaks on ERPNext upgrades that add methods or change signatures.
class CustomSalesInvoice(AccountsController):
    def validate(self):
        super().validate()
        # Business logic replacing core accounts controller behaviour.
        self.custom_discount_logic()

    def custom_discount_logic(self):
        pass
