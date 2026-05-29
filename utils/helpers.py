"""
Utility helper functions untuk data processing dan file operations.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd

def clean_filename(name: str, max_len: int = 60) -> str:
    """
    Bersihkan nama file dari karakter invalid.
    
    Args:
        name: Nama file/sheet
        max_len: Max length
    
    Returns:
        Clean filename
    """
    invalid_chars = r'<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    
    name = name.strip()
    return (name[:max_len] if len(name) > max_len else name) or "DATA"


def get_file_size_mb(path: str) -> float:
    """Get file size in megabytes."""
    try:
        return Path(path).stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def safe_float(value: Any) -> float:
    """
    Convert value to float safely.
    Handles None, NaN, strings with commas, etc.
    """
    if value is None:
        return 0.0
    
    try:
        if isinstance(value, (int, float)):
            return float(value)
        
        s = str(value).strip().replace(",", ".")
        if s and s not in ("nan", "", "None"):
            return float(s)
        return 0.0
    except Exception:
        return 0.0


def find_column_index(headers: List[str], candidates: List[str]) -> Optional[int]:
    """
    Find column index by candidates (case-insensitive).
    
    Args:
        headers: List of header names
        candidates: List of possible column names
    
    Returns:
        Column index or None
    """
    h_upper = [str(x).upper().strip() for x in headers]
    
    for candidate in candidates:
        candidate_upper = candidate.upper()
        if candidate_upper in h_upper:
            return h_upper.index(candidate_upper)
    
    return None


def get_timestamp() -> str:
    """Get current timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_log_dir(output_path: str) -> str:
    """Get log directory beside output path."""
    base = Path(output_path).parent if "." in Path(output_path).name else Path(output_path)
    return str(base / "Logs")


def ensure_dir_exists(path: str) -> None:
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)


def read_excel_safe(path: str, sheet_name=None, **kwargs) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Read Excel file safely dengan error handling.
    
    Args:
        path: File path
        sheet_name: Sheet name atau None untuk semua
        **kwargs: Additional pandas read_excel args
    
    Returns:
        Dict of DataFrames atau None
    """
    try:
        if path.lower().endswith(".xlsx"):
            return pd.read_excel(path, sheet_name=sheet_name, dtype=str,
                                engine="openpyxl", **kwargs)
        else:
            return pd.read_excel(path, sheet_name=sheet_name, dtype=str, **kwargs)
    except Exception as e:
        raise ValueError(f"Gagal membaca file: {str(e)}")
