"""doc_events handler for Recursive Doc (Phase 2 test)."""


def on_update(doc, method):
    """Arbitrary handler - just needs to exist so the doc_event binding
    exists for the same DocType that has a lifecycle->save path. Triggers
    recursive-doc-event-trigger."""
    doc.custom_flag = 1
