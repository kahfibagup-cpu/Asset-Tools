"""
Reusable UI widgets dengan optimasi performa.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List, Callable, Optional
from ui.theme import create_frame, create_label, create_entry, create_button, THEME, FONTS


class LogBox(tk.Frame):
    """Custom log viewer dengan color tags dan scrolling."""
    
    TAGS = {
        "info": THEME["accent"],
        "success": THEME["success"],
        "warning": THEME["warning"],
        "error": THEME["danger"],
        "dim": THEME["muted"],
        "sep": THEME["border"],
    }
    
    def __init__(self, parent, **kw):
        super().__init__(
            parent,
            bg=THEME["bg2"],
            highlightthickness=1,
            highlightbackground=THEME["border"],
            **kw
        )
        
        # Scrollbar
        sb = tk.Scrollbar(self, bg=THEME["bg2"], troughcolor=THEME["bg"],
                         activebackground=THEME["accent"])
        sb.pack(side="right", fill="y")
        
        # Text widget
        self.txt = tk.Text(
            self,
            font=FONTS["mono"],
            fg=THEME["muted"],
            bg=THEME["card"],
            relief="flat",
            wrap="word",
            state="disabled",
            bd=0,
            yscrollcommand=sb.set,
            padx=10,
            pady=8
        )
        self.txt.pack(fill="both", expand=True)
        sb.config(command=self.txt.yview)
        
        # Configure tags
        for tag, color in self.TAGS.items():
            self.txt.tag_config(tag, foreground=color)
    
    def write(self, msg: str, tag: str = "info") -> None:
        """Write message to log."""
        def _w():
            self.txt.config(state="normal")
            ts = datetime.now().strftime("%H:%M:%S")
            self.txt.insert("end", f"[{ts}]  {msg}\n", tag)
            self.txt.see("end")
            self.txt.config(state="disabled")
        self.after(0, _w)
    
    def clear(self) -> None:
        """Clear all log messages."""
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.config(state="disabled")


class ProgressBar(tk.Frame):
    """Simple progress bar widget."""
    
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=THEME["border"], height=5, **kw)
        self.pack_propagate(False)
        self._fill = tk.Frame(self, bg=THEME["accent2"], height=5)
        self._fill.place(relwidth=0, relheight=1)
    
    def set(self, pct: int) -> None:
        """Set progress percentage (0-100)."""
        self.after(0, lambda: self._fill.place(
            relwidth=min(max(pct, 0), 100) / 100,
            relheight=1
        ))


class SheetSelector(tk.Frame):
    """Reusable sheet selector dengan search dan bulk operations."""
    
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=THEME["bg"], **kw)
        self._vars: dict = {}
        self._all: list = []
        self._build()
    
    def _build(self) -> None:
        """Build UI components."""
        # Control buttons
        ctrl = create_frame(self, THEME["bg"])
        ctrl.pack(fill="x", pady=(0, 4))
        create_button(ctrl, "☑ Semua", self.select_all, "dim", small=True).pack(side="left", padx=(0, 4))
        create_button(ctrl, "☐ Kosong", self.deselect_all, "dim", small=True).pack(side="left")
        
        # Search box
        sf = create_frame(self, THEME["bg"])
        sf.pack(fill="x", pady=(0, 4))
        create_label(sf, "🔍 ", "small", "muted").pack(side="left")
        
        self._sv = tk.StringVar()
        self._sv.trace("w", self._filter)
        tk.Entry(
            sf,
            textvariable=self._sv,
            font=FONTS["small"],
            fg=THEME["text"],
            bg=THEME["card"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            insertbackground=THEME["accent"]
        ).pack(side="left", fill="x", expand=True, ipady=3)
        
        # Canvas + scrollbar for sheet list
        canvas_frame = create_frame(self, THEME["bg"])
        canvas_frame.pack(fill="both", expand=True)
        
        sb = tk.Scrollbar(canvas_frame, bg=THEME["bg2"], troughcolor=THEME["bg"])
        sb.pack(side="right", fill="y")
        
        self._canvas = tk.Canvas(
            canvas_frame,
            bg=THEME["card"],
            highlightthickness=0,
            yscrollcommand=sb.set
        )
        self._canvas.pack(fill="both", expand=True)
        sb.config(command=self._canvas.yview)
        
        self._inner = create_frame(self._canvas, THEME["card"])
        self._win = self._canvas.create_window(0, 0, window=self._inner, anchor="nw")
        
        self._inner.bind("<Configure>", lambda e: (
            self._canvas.configure(scrollregion=self._canvas.bbox("all")),
            self._canvas.itemconfig(self._win, width=e.width)
        ))
        
        self._canvas.bind("<Configure>", lambda e:
            self._canvas.itemconfig(self._win, width=e.width))
        
        self._canvas.bind_all("<MouseWheel>", lambda e:
            self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    
    def load(self, sheets: List[str]) -> None:
        """Load sheet list."""
        for w in self._inner.winfo_children():
            w.destroy()
        self._vars.clear()
        self._all = sheets
        
        for s in sheets:
            v = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(
                self._inner,
                text=s,
                variable=v,
                font=FONTS["small"],
                fg=THEME["text"],
                bg=THEME["card"],
                selectcolor=THEME["card"],
                activebackground=THEME["card"],
                activeforeground=THEME["accent"],
                anchor="w",
                padx=8,
                pady=3,
                cursor="hand2",
                highlightthickness=0,
                relief="flat"
            )
            cb.pack(fill="x")
            self._vars[s] = (v, cb)
        
        self._canvas.yview_moveto(0)
    
    def select_all(self) -> None:
        """Select all sheets."""
        for v, _ in self._vars.values():
            v.set(True)
    
    def deselect_all(self) -> None:
        """Deselect all sheets."""
        for v, _ in self._vars.values():
            v.set(False)
    
    def _filter(self, *_) -> None:
        """Filter sheets by search."""
        q = self._sv.get().lower()
        for s, (v, cb) in self._vars.items():
            if q in s.lower():
                cb.pack(fill="x")
            else:
                cb.pack_forget()
    
    def selected(self) -> List[str]:
        """Get selected sheets."""
        return [s for s, (v, _) in self._vars.items() if v.get()]


class FileRow(tk.Frame):
    """Reusable file selection row dengan browse button."""
    
    def __init__(self, parent, label: str, hint: str, var: tk.StringVar,
                 cmd: Callable, bg=None, **kwargs):
        bg = bg or THEME["bg"]
        super().__init__(parent, bg=bg, **kwargs)
        
        # Label
        create_label(self, label, "label", "text").pack(anchor="w")
        
        # Input row
        row = create_frame(self, bg)
        row.pack(fill="x", pady=(4, 0))
        
        e = create_entry(row, var, mono=True)
        e.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        
        create_button(row, "📂 Browse…", cmd, "dim", small=True).pack(side="right")
        
        # Hint
        if hint:
            create_label(self, hint, "small", "muted").pack(anchor="w", pady=(3, 0))