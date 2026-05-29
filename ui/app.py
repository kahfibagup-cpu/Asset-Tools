"""
Main application window dengan tab management dan theme integration.
"""

import sys
import tkinter as tk
from pathlib import Path

from config import THEME, FONTS, APP_TITLE, APP_VERSION, APP_AUTHOR
from config.constants import MIN_WIDTH, MIN_HEIGHT, DEFAULT_WIDTH, DEFAULT_HEIGHT
from ui.theme import create_frame, create_label, create_button
from ui.tabs import TabKonsolidasi, TabSplit, TabAdvancedSplit, TabRekap
import pandas as pd


class AssetToolsApp(tk.Tk):
    """Main application window."""
    
    TABS = [
        ("① Konsolidasi", TabKonsolidasi, THEME["accent"]),
        ("② Split", TabSplit, THEME["accent2"]),
        ("③ Adv. Split", TabAdvancedSplit, THEME["success"]),
        ("④ Rekap UP3", TabRekap, THEME["warning"]),
    ]
    
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE}  –  by {APP_AUTHOR}  v{APP_VERSION}")
        self.configure(bg=THEME["bg"])
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.resizable(True, True)
        
        # Center window
        w, h = DEFAULT_WIDTH, DEFAULT_HEIGHT
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self._active_tab = 0
        self._tabs_cache = {}
        self._build()
    
    def _build(self):
        """Build main UI."""
        # ──────────────────────────────────────────────────────────
        #  TOP HEADER BAR
        # ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=THEME["bg2"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        
        # Accent line
        tk.Frame(hdr, bg=THEME["accent"], width=5).pack(side="left", fill="y")
        
        # Logo + Title
        lf = create_frame(hdr, THEME["bg2"])
        lf.pack(side="left", padx=16, pady=8)
        
        # Logo circle
        cnv = tk.Canvas(lf, width=34, height=34, bg=THEME["bg2"], highlightthickness=0)
        cnv.pack(side="left")
        cnv.create_oval(2, 2, 32, 32, fill=THEME["accent2"], outline=THEME["accent"], width=2)
        cnv.create_text(17, 17, text="⚡", fill="white", font=("Segoe UI Emoji", 14))
        
        # Title text
        tk.Label(
            lf,
            text=APP_TITLE,
            font=("Segoe UI Semibold", 14, "bold"),
            fg=THEME["text"],
            bg=THEME["bg2"]
        ).pack(side="left", padx=8)
        
        # Version info
        tk.Label(
            hdr,
            text=f"by {APP_AUTHOR}  ·  v{APP_VERSION}",
            font=FONTS["small"],
            fg=THEME["muted"],
            bg=THEME["bg2"]
        ).pack(side="right", padx=20)
        
        # ──────────────────────────────────────────────────────────
        #  ACCENT STRIP
        # ──────────────────────────────────────────────────────────
        tk.Frame(self, bg=THEME["accent2"], height=2).pack(fill="x")
        
        # ──────────────────────────────────────────────────────────
        #  TAB BAR
        # ──────────────────────────────────────────────────────────
        self._tab_bar = tk.Frame(self, bg=THEME["bg2"])
        self._tab_bar.pack(fill="x")
        self._tab_btns = []
        
        for i, (label, _, color) in enumerate(self.TABS):
            btn = tk.Button(
                self._tab_bar,
                text=f"  {label}  ",
                font=("Segoe UI", 10, "bold"),
                fg=THEME["text"] if i == 0 else THEME["muted"],
                bg=color if i == 0 else THEME["card"],
                activebackground=color,
                activeforeground=THEME["white"],
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=10,
                command=lambda idx=i: self._switch_tab(idx)
            )
            btn.pack(side="left")
            self._tab_btns.append((btn, color))
        
        # Separator
        tk.Frame(self._tab_bar, bg=THEME["border"], height=2).pack(fill="x", side="bottom")
        
        # ──────────────────────────────────────────────────────────
        #  CONTENT FRAME
        # ──────────────────────────────────────────────────────────
        self._content = create_frame(self, THEME["bg"])
        self._content.pack(fill="both", expand=True)
        
        # ──────────────────────────────────────────────────────────
        #  STATUS BAR
        # ──────────────────────────────────────────────────────────
        sb = tk.Frame(self, bg=THEME["bg2"], height=26)
        sb.pack(fill="x")
        sb.pack_propagate(False)
        
        # Accent line
        tk.Frame(sb, bg=THEME["accent2"], width=3).pack(side="left", fill="y")
        
        # Status label
        self._status_lbl = tk.Label(
            sb,
            text="Siap",
            font=FONTS["small"],
            fg=THEME["muted"],
            bg=THEME["bg2"]
        )
        self._status_lbl.pack(side="left", padx=12)
        
        # Version info
        tk.Label(
            sb,
            text=f"Python {sys.version.split()[0]}  ·  pandas {pd.__version__}",
            font=FONTS["small"],
            fg=THEME["muted"],
            bg=THEME["bg2"]
        ).pack(side="right", padx=12)
        
        # Load first tab
        self._switch_tab(0)
    
    def _switch_tab(self, idx: int):
        """Switch to tab by index."""
        self._active_tab = idx
        
        # Hide previous content
        for w in self._content.winfo_children():
            w.pack_forget()
        
        # Update tab button styles
        for i, (btn, color) in enumerate(self._tab_btns):
            if i == idx:
                btn.config(bg=color, fg=THEME["white"])
            else:
                btn.config(bg=THEME["card"], fg=THEME["muted"])
        
        # Build tab if not cached
        if idx not in self._tabs_cache:
            _, TabClass, _ = self.TABS[idx]
            frame = TabClass(self._content, self)
            self._tabs_cache[idx] = frame
        
        # Show tab
        self._tabs_cache[idx].pack(fill="both", expand=True)
        
        # Update status
        self._status_lbl.config(text=f"Tab aktif: {self.TABS[idx][0]}")


def run_app():
    """Run application."""
    app = AssetToolsApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()