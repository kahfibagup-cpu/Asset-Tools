"""
Base tab class dengan common functionality.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Callable, Optional
from pathlib import Path
from ui.widgets import LogBox, ProgressBar, FileRow
from ui.theme import create_frame, create_label, create_button, THEME, FONTS
from utils import get_log_dir


class BaseTab(tk.Frame):
    """Base class untuk semua tabs."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._running = False
        self._build()
    
    def _build(self) -> None:
        """Build tab UI. Override di subclass."""
        pass
    
    def _make_log_area(self, parent) -> LogBox:
        """Create log area dengan buttons."""
        from ui.theme import create_section
        create_section(parent, "LOG", "LOG PROSES")
        
        lb = LogBox(parent)
        lb.pack(fill="both", expand=True, padx=18, pady=(8, 12))
        self._log_box = lb
        
        row = create_frame(parent, THEME["bg"])
        row.pack(fill="x", padx=18, pady=(0, 8))
        create_button(row, "🗑 Bersihkan Log", lb.clear, "dim", small=True).pack(side="right")
        
        return lb
    
    def _log(self, msg: str, tag: str = "info") -> None:
        """Log message to UI."""
        if hasattr(self, "_log_box"):
            self._log_box.write(msg, tag)
    
    def _make_progress(self, parent) -> ProgressBar:
        """Create progress bar."""
        pb = ProgressBar(parent)
        pb.pack(fill="x", padx=18, pady=(0, 4))
        self._pb = pb
        return pb
    
    def _set_progress(self, v: int) -> None:
        """Update progress."""
        if hasattr(self, "_pb"):
            self._pb.set(v)
    
    def _browse_file(
        self,
        var: tk.StringVar,
        title: str = "Pilih File",
        ftypes: List[tuple] = None
    ) -> Optional[str]:
        """Browse single file."""
        if ftypes is None:
            ftypes = [("Excel", "*.xlsx *.xlsm")]
        
        p = filedialog.askopenfilename(title=title, filetypes=ftypes)
        if p:
            var.set(p)
        return p
    
    def _browse_files(
        self,
        var_list: List[str],
        listbox: tk.Listbox
    ) -> int:
        """Browse multiple files."""
        paths = filedialog.askopenfilenames(
            title="Pilih File Sumber",
            filetypes=[("Excel", "*.xlsx *.xlsm")]
        )
        added = 0
        for p in paths:
            if p not in var_list:
                var_list.append(p)
                listbox.insert("end", f"  {Path(p).name}")
                added += 1
        return added
    
    def _browse_dir(self, var: tk.StringVar) -> None:
        """Browse directory."""
        p = filedialog.askdirectory()
        if p:
            var.set(p)
    
    def _disable_run(self, btn: tk.Button, text: str = "⏳ Memproses...") -> None:
        """Disable run button."""
        self._running = True
        btn.config(state="disabled", text=text)
    
    def _enable_run(self, btn: tk.Button, text: str) -> None:
        """Enable run button."""
        self._running = False
        btn.config(state="normal", text=text)
    
    def _get_log_dir(self, out_path: str) -> str:
        """Get log directory."""
        return get_log_dir(out_path)
    
    def _mini_stat(self, parent, label: str, value: str, color: str = "accent"):
        """Create mini stat widget."""
        f = create_frame(parent, THEME["card"])
        f.pack(side="left", fill="both", expand=True, padx=3, pady=4)
        
        v = tk.Label(f, text=value, font=FONTS["big"], fg=THEME[color], bg=THEME["card"])
        v.pack()
        
        create_label(f, label, "small", "muted").pack()
        return v