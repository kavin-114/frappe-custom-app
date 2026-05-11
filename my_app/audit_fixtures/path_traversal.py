"""Audit fixture: file-path traversal on user input.

Proposed rule IDs:
- path-traversal-user-input        (critical) — open()/read_text()/etc.
  with a path component taken from request input, without normalisation
  through frappe.utils.get_files_path() or pathlib.Path.is_relative_to.
- frappe-get-file-no-permission    (critical) — frappe.get_file / read
  on a File DocType name without a permission check.
- subprocess-shell-true-user-input (critical) — os.system / Popen(shell=True)
  with user-supplied path arguments (command injection cousin).

Counter-example uses get_files_path() + Path.is_relative_to.
"""
from __future__ import annotations

import os
from pathlib import Path

import frappe


# BAD ----------------------------------------------------------------------
@frappe.whitelist()
def read_uploaded(filename: str) -> str:
    """path-traversal-user-input — filename can contain '../../etc/passwd'."""
    with open(f"/home/frappe/uploads/{filename}", "r") as f:  # Bad
        return f.read()


@frappe.whitelist()
def serve_attachment(file_doc_name: str) -> bytes:
    """frappe-get-file-no-permission — no has_permission check."""
    fdoc = frappe.get_doc("File", file_doc_name)
    return fdoc.get_content()  # may belong to another tenant


@frappe.whitelist()
def archive_folder(folder: str) -> int:
    """subprocess-shell-true-user-input — folder lands in a shell string."""
    return os.system(f"tar -czf /tmp/out.tar.gz {folder}")  # Bad


# GOOD counter-example ------------------------------------------------------
@frappe.whitelist()
def read_uploaded_safe(filename: str) -> str:
    """Path is normalised and bounded to the site's files dir."""
    root = Path(frappe.utils.get_files_path())
    candidate = (root / filename).resolve()
    if not candidate.is_relative_to(root.resolve()):
        frappe.throw("Invalid filename")
    frappe.has_permission("File", throw=True)
    return candidate.read_text()
