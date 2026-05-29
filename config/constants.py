"""
Configuration and theme constants for Asset Distribution Tools.
Centralized settings untuk theme, fonts, dan application parameters.
"""

# ══════════════════════════════════════════════════════════════
#  THEME COLORS (Dark Premium)
# ══════════════════════════════════════════════════════════════

THEME = {
    "bg": "#0D1117",
    "bg2": "#161B22",
    "card": "#1C2433",
    "border": "#2D3748",
    "accent": "#0EA5E9",        # Cyan
    "accent2": "#3B82F6",       # Blue
    "success": "#22C55E",       # Green
    "warning": "#F59E0B",       # Orange
    "danger": "#EF4444",        # Red
    "text": "#E2E8F0",
    "muted": "#6B7280",
    "white": "#FFFFFF",
}

# ══════════════════════════════════════════════════════════════
#  FONTS
# ══════════════════════════════════════════════════════════════

FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 9),
    "label": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 10),
    "mono": ("Consolas", 9),
    "small": ("Segoe UI", 8),
    "big": ("Segoe UI", 13, "bold"),
}

# ══════════════════════════════════════════════════════════════
#  APPLICATION SETTINGS
# ══════════════════════════════════════════════════════════════

APP_TITLE = "Asset Distribution Tools"
APP_VERSION = "2.0"
APP_AUTHOR = "Ophar"
MIN_WIDTH = 1200
MIN_HEIGHT = 700
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 700

# ══════════════════════════════════════════════════════════════
#  PERFORMANCE SETTINGS
# ══════════════════════════════════════════════════════════════

MAX_WORKERS = 4
CHUNK_SIZE = 10000
CACHE_SIZE_MB = 100
FILE_READ_TIMEOUT = 60
PROGRESS_UPDATE_MS = 100

# ══════════════════════════════════════════════════════════════
#  FILE PATTERNS
# ══════════════════════════════════════════════════════════════

EXCEL_EXTENSIONS = (".xlsx", ".xlsm", ".xls")
CSV_EXTENSIONS = (".csv",)
SUPPORTED_FORMATS = EXCEL_EXTENSIONS + CSV_EXTENSIONS

# ══════════════════════════════════════════════════════════════
#  ENGINE COLUMN MAPPINGS
# ══════════════════════════════════════════════════════════════

COLUMNS = {
    "OWNER_CODE": ["OWNER_CODE", "OWNER_KODE"],
    "OWNER_ASET": ["OWNER_ASET", "OWNER_ASSET"],
    "NAME_UP3": ["NAME_UP3", "UP3_NAME"],
    "UNIT_MASTER": "UNIT_MASTER",
    "CONFIG": "CONFIG",
    "SUBCLASS": ["SUBCLASS", "SUBCLASS_CODE"],
    "STATUS": ["STATUS"],
    "END_MEASURE": ["END_MEASURE", "PANJANG", "LENGTH"],
    "KAPASITAS": ["KAPASITAS", "KAPASITAS_TRAFO", "RATED_CAPACITY", "KVA"],
}

from pathlib import Path
HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
LOGS_DIR = "Logs"
