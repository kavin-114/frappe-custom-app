# Re-export so hooks.py can reference the function via the shortened
# dotted path (`my_app.tasks.reexported_scheduled_task`). The resolver
# must follow this one hop instead of reporting "missing".
from my_app.tasks.reexport_target import reexported_scheduled_task

__all__ = ["reexported_scheduled_task"]
