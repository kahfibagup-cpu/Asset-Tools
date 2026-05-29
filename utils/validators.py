"""
Input validation functions untuk mencegah errors di awal.
"""

import os
from pathlib import Path
from typing import Tuple, List

def validate_file_exists(path: str, file_type: str = "File") -> Tuple[bool, str]:
    """
    Validate if file exists.
    
    Returns:
        (is_valid, error_message)
    """
    if not path or not path.strip():
        return False, f"{file_type} tidak boleh kosong"
    
    if not os.path.exists(path):
        return False, f"{file_type} tidak ditemukan: {path}"
    
    return True, ""


def validate_directory_exists(path: str) -> Tuple[bool, str]:
    """Validate if directory exists."""
    if not path or not path.strip():
        return False, "Folder tidak boleh kosong"
    
    if not os.path.isdir(path):
        return False, f"Folder tidak valid: {path}"
    
    return True, ""


def validate_multiple_files(files: List[str]) -> Tuple[bool, str]:
    """Validate multiple files."""
    if not files:
        return False, "Minimal 1 file harus dipilih"
    
    invalid = [f for f in files if not os.path.exists(f)]
    if invalid:
        return False, f"File tidak ditemukan: {', '.join(invalid[:3])}"
    
    return True, ""


def validate_sheet_selected(sheets: List[str]) -> Tuple[bool, str]:
    """Validate sheet selection."""
    if not sheets:
        return False, "Minimal 1 sheet harus dipilih"
    
    return True, ""


def validate_output_path(path: str) -> Tuple[bool, str]:
    """Validate output path writable."""
    try:
        parent = Path(path).parent
        parent.mkdir(parents=True, exist_ok=True)
        return True, ""
    except Exception as e:
        return False, f"Tidak bisa menulis ke folder output: {str(e)}"
