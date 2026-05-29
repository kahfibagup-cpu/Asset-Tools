"""
Base engine class dengan common functionality dan error handling.
"""

import gc
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any
from utils import ModuleLogger


class BaseEngine(ABC):
    """Base class untuk semua engines dengan common functionality."""
    
    def __init__(
        self,
        log_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        file_logger: Optional[ModuleLogger] = None
    ):
        """
        Args:
            log_callback: Callback untuk UI logging
            progress_callback: Callback untuk progress updates (0-100)
            file_logger: ModuleLogger instance
        """
        self._log = log_callback or print
        self._prog = progress_callback or (lambda x: None)
        self._fl = file_logger
        self._start_time = 0
    
    def _flog(self, msg: str, level: str = "info") -> None:
        """Log ke file logger."""
        if self._fl:
            getattr(self._fl, level, self._fl.info)(msg)
    
    def _log_ui(self, msg: str, tag: str = "info") -> None:
        """Log ke UI callback."""
        self._log(msg, tag)
    
    def _update_progress(self, percentage: int) -> None:
        """Update progress bar (0-100)."""
        self._prog(min(max(percentage, 0), 100))
    
    def _start_timer(self) -> None:
        """Start execution timer."""
        self._start_time = time.perf_counter()
    
    def _get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return round(time.perf_counter() - self._start_time, 2)
    
    def _cleanup_memory(self) -> None:
        """Force garbage collection."""
        gc.collect()
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run engine. Implementasi di subclass."""
        pass