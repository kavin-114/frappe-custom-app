"""Companion to dead_code_showcase.py — proves the import-keeps-alive path.

Imports `imported_in_data_import_module` from the showcase, which is
exactly the signal the dead-code analyzer treats as "alive via name
mention." Without this file, that fixture would be (correctly) flagged
as dead.
"""
from my_app.audit_fixtures.dead_code_showcase import imported_in_data_import_module


def run() -> str:
    return imported_in_data_import_module()
