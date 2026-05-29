"""
Tab ② Split - Split per UP3 dengan UI scrollable.
"""

import os
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import pandas as pd

from ui.tabs.base_tab import BaseTab
from ui.theme import create_frame, create_label, create_button, create_section, THEME, FONTS
from ui.widgets import FileRow, SheetSelector
from core import SplitEngine
from utils import ModuleLogger
from config.constants import DOWNLOADS


class TabSplit(BaseTab):
    """Tab untuk Split per UP3."""
    
    def _build(self):
        """Build UI dengan layout scrollable."""
        # Main container
        main_container = create_frame(self, THEME["bg"])
        main_container.pack(fill="both", expand=True)
        
        # Canvas
        canvas = tk.Canvas(main_container, bg=THEME["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(main_container, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self._scroll_frame = create_frame(canvas, THEME["bg"])
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self._scroll_frame.bind("<Configure>", on_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        self._build_content()
    
    def _build_content(self):
        """Build form content."""
        # Header
        hdr = create_frame(self._scroll_frame, THEME["bg2"])
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=THEME["accent2"], height=3).pack(fill="x")
        
        ih = create_frame(hdr, THEME["bg2"])
        ih.pack(fill="x", padx=24, pady=12)
        create_label(ih, "② Split per UP3", "title", "text").pack(side="left")
        create_label(ih, "Split data berdasarkan mapping UNIT_MASTER → NAME_UP3", "subtitle", "muted").pack(
            side="left", padx=20
        )
        
        form_frame = create_frame(self._scroll_frame, THEME["bg"])
        form_frame.pack(fill="x", padx=18, pady=10)
        
        # Section 1: Configuration
        create_section(form_frame, 1, "KONFIGURASI")
        
        self._v_master = tk.StringVar()
        FileRow(
            form_frame,
            "File UNIT_MASTER",
            "Mapping OWNER_CODE/OWNER_ASET → NAME_UP3",
            self._v_master,
            lambda: (
                self._browse_file(self._v_master),
                self._log(f"Master: {Path(self._v_master.get()).name}", "info")
            ),
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(8, 0))
        
        self._v_data = tk.StringVar()
        FileRow(
            form_frame,
            "File Data Konsolidasi",
            "File yang akan di-split per UP3",
            self._v_data,
            self._load_data_file,
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(8, 0))
        
        self._v_out = tk.StringVar(value=str(DOWNLOADS / "Split_Output"))
        FileRow(
            form_frame,
            "Folder Output",
            "Folder penyimpanan hasil split per UP3",
            self._v_out,
            lambda: self._browse_dir(self._v_out),
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(8, 10))
        
        # Format
        fr = create_frame(form_frame, THEME["card"])
        fr.pack(fill="x", padx=18, pady=(0, 10))
        create_label(fr, "Format :", "body", "muted").pack(side="left")
        self._v_fmt = tk.StringVar(value="xlsx")
        for f in ["xlsx", "csv"]:
            tk.Radiobutton(
                fr, text=f.upper(), variable=self._v_fmt, value=f,
                bg=THEME["card"], fg=THEME["text"],
                selectcolor=THEME["bg"], font=FONTS["body"]
            ).pack(side="left", padx=8)
        
        # Section 2: Statistics
        create_section(form_frame, 2, "STATISTIK")
        sr = create_frame(form_frame, THEME["card"])
        sr.pack(fill="x", padx=18, pady=8)
        self._sv_files = self._mini_stat(sr, "FILE", "—", "accent2")
        self._sv_sheets = self._mini_stat(sr, "SHEETS", "—", "accent2")
        self._sv_rows = self._mini_stat(sr, "BARIS", "—", "accent2")
        self._sv_time = self._mini_stat(sr, "DETIK", "—", "accent2")
        
        # Section 3: Sheet Selector
        create_section(form_frame, 3, "SELECT SHEETS")
        self._sheet_sel = SheetSelector(form_frame)
        self._sheet_sel.pack(fill="both", expand=False, padx=18, pady=8)
        self._sheet_sel.config(height=150)
        
        # Section 4: Control
        create_section(form_frame, 4, "KONTROL")
        rb = create_frame(form_frame, THEME["card"])
        rb.pack(fill="x", padx=18, pady=(8, 6))
        self._run_btn = create_button(rb, "▶  JALANKAN SPLIT", self._start, "run", width=24)
        self._run_btn.pack(side="left")
        
        self._make_progress(form_frame)
        
        # Section 5: Log
        create_section(form_frame, 5, "LOG PROSES")
        self._log_box = self._make_log_area(form_frame)
    
    def _load_data_file(self):
        """Load data file dan populate sheets."""
        self._browse_file(self._v_data)
        p = self._v_data.get()
        
        if p and os.path.exists(p):
            self._log("Membaca sheet dari file data...", "info")
            try:
                xl = pd.ExcelFile(p)
                self._sheet_sel.load(xl.sheet_names)
                self._log(f"  ✓ {len(xl.sheet_names)} sheet ditemukan", "success")
            except Exception as e:
                self._log(f"  ✗ {e}", "error")
    
    def _start(self):
        """Start split process."""
        if self._running:
            return
        
        master = self._v_master.get().strip()
        data = self._v_data.get().strip()
        out_dir = self._v_out.get().strip()
        selected = self._sheet_sel.selected()
        fmt = self._v_fmt.get()
        
        # Validation
        if not master:
            messagebox.showwarning("", "Pilih file UNIT_MASTER")
            return
        if not data:
            messagebox.showwarning("", "Pilih file data")
            return
        if not out_dir:
            messagebox.showwarning("", "Pilih folder output")
            return
        if not selected:
            messagebox.showwarning("", "Pilih minimal 1 sheet")
            return
        
        self._disable_run(self._run_btn, "⏳ Memproses...")
        self._set_progress(0)
        
        fl = ModuleLogger("SPLIT", self._get_log_dir(out_dir))
        threading.Thread(
            target=self._run,
            args=(master, data, out_dir, selected, fmt, fl),
            daemon=True
        ).start()
    
    def _run(self, master, data, out_dir, selected, fmt, fl):
        """Run engine in background."""
        try:
            eng = SplitEngine(self._log, self._set_progress, fl)
            eng.load_master(master)
            stats = eng.run(data, out_dir, selected, fmt)
            
            def _done():
                self._sv_files.config(text=str(stats["total_files"]))
                self._sv_sheets.config(text=str(stats["total_sheets"]))
                self._sv_rows.config(text=f"{stats['total_rows']:,}")
                self._sv_time.config(text=str(stats["elapsed"]))
                self._enable_run(self._run_btn, "▶  JALANKAN SPLIT")
                self._set_progress(100)
                self._log("─" * 50, "sep")
                
                msg = (f"✅ SELESAI\n\n"
                       f"File  : {stats['total_files']}\n"
                       f"Baris : {stats['total_rows']:,}\n"
                       f"Waktu : {stats['elapsed']}s")
                
                if stats.get("unmapped_count", 0):
                    msg += f"\n\n⚠️  {stats['unmapped_count']} unmapped owners"
                
                if messagebox.askyesno("Selesai", msg + "\n\nBuka folder output?"):
                    os.startfile(out_dir)
            
            self.after(0, _done)
        
        except Exception as e:
            tb = traceback.format_exc()
            def _err():
                self._log(f"✗ {e}", "error")
                self._log(tb, "dim")
                self._enable_run(self._run_btn, "▶  JALANKAN SPLIT")
                messagebox.showerror("Error", str(e))
            self.after(0, _err)