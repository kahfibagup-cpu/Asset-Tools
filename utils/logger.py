"""
Advanced logging system dengan file per modul dan color tags.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

class ModuleLogger:
    """Logger khusus per modul dengan file output terpisah."""
    
    def __init__(self, name: str, log_dir: str):
        """
        Args:
            name: Nama modul (KONSOLIDASI, SPLIT, etc)
            log_dir: Direktori untuk menyimpan log files
        """
        self.name = name
        os.makedirs(log_dir, exist_ok=True)
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(log_dir, f"LOG_{name}_{ts}.txt")
        
        self.logger = logging.getLogger(f"{name}_{ts}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to prevent duplicates
        self.logger.handlers.clear()
        
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.log_path = log_path
    
    def info(self, msg: str) -> None:
        """Log info message."""
        self.logger.info(msg)
    
    def success(self, msg: str) -> None:
        """Log success message."""
        self.logger.info(f"✓ {msg}")
    
    def warning(self, msg: str) -> None:
        """Log warning message."""
        self.logger.warning(f"⚠ {msg}")
    
    def error(self, msg: str) -> None:
        """Log error message."""
        self.logger.error(f"✗ {msg}")
    
    def debug(self, msg: str) -> None:
        """Log debug message."""
        self.logger.debug(msg)
