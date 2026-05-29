"""
Tab ④ Rekap UP3 - Generate summary report dengan UI scrollable.
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
from core import RekapEngine
from utils import ModuleLogger
from config.constants import DOWNLOADS


class TabRekap(BaseTab):
    """Tab untuk Rekap UP3."""
    
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
        tk.Frame(hdr, bg=THEME["warning"], height=3).pack(fill="x")
        
        ih = create_frame(hdr, THEME["bg2"])
        ih.pack(fill="x", padx=24, pady=12)
        create_label(ih, "④ Rekap UP3", "title", "text").pack(side="left")
        create_label(ih, "Rekap Asset Distribusi per Owner Asset", "subtitle", "muted").pack(
            side="left", padx=20
        )
        
        form_frame = create_frame(self._scroll_frame, THEME["bg"])
        form_frame.pack(fill="x", padx=18, pady=10)
        
        # Section 1: File Input
        create_section(form_frame, 1, "FILE INPUT")
        
        self._v_template = tk.StringVar()
        FileRow(
            form_frame,
            "File Template/Config (Rekap.xlsx)",
            "Berisi sheet CONFIG + UNIT_MASTER + sheet {{UP3}} template",
            self._v_template,
            lambda: self._browse_file(self._v_template),
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(8, 0))
        
        self._v_master = tk.StringVar()
        FileRow(
            form_frame,
            "File Master Data",
            "Data asset yang akan direkap (multi-sheet supported)",
            self._v_master,
            self._load_master_file,
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(8, 10))
        
        # Section 2: Settings
        create_section(form_frame, 2, "PENGATURAN")
        opt = create_frame(form_frame, THEME["card"])
        opt.pack(fill="x", padx=18, pady=8)
        
        # UID
        uid_r = create_frame(opt, THEME["card"])
        uid_r.pack(fill="x", pady=(0, 8))
        create_label(uid_r, "UID (opsional) :", "body", "muted").pack(side="left")
        self._v_uid = tk.StringVar(value="JAWA TIMUR")
        from ui.theme import create_entry
        create_entry(uid_r, self._v_uid, wide=False).pack(side="left", padx=8, ipady=4)
        
        # Filter mode
        fm_r = create_frame(opt, THEME["card"])
        fm_r.pack(fill="x", pady=(8, 0))
        create_label(fm_r, "Mode Filter :", "body", "muted").pack(anchor="w")
        
        self._v_filter = tk.IntVar(value=2)
        
        m1 = create_frame(opt, THEME["card"])
        m1.pack(fill="x", pady=(4, 2))
        tk.Radiobutton(
            m1,
            text="Mode 1 — Hapus row kosong (ringkas)",
            variable=self._v_filter,
            value=1,
            bg=THEME["card"],
            fg=THEME["text"],
            selectcolor=THEME["bg"],
            font=FONTS["body"],
            activebackground=THEME["card"]
        ).pack(anchor="w")
        create_label(
            m1,
            "  Menghapus baris yang tidak ada datanya dari output",
            "small",
            "muted"
        ).pack(anchor="w")
        
        m2 = create_frame(opt, THEME["card"])
        m2.pack(fill="x", pady=(2, 0))
        tk.Radiobutton(
            m2,
            text="Mode 2 — Ikuti template sepenuhnya (semua baris tampil)",
            variable=self._v_filter,
            value=2,
            bg=THEME["card"],
            fg=THEME["text"],
            selectcolor=THEME["bg"],
            font=FONTS["body"],
            activebackground=THEME["card"]
        ).pack(anchor="w")
        create_label(
            m2,
            "  Semua baris template dipertahankan, kosong jika tidak ada data",
            "small",
            "muted"
        ).pack(anchor="w")
        
        # Section 3: Output
        create_section(form_frame, 3, "OUTPUT")
        out_frame = create_frame(form_frame, THEME["card"])
        out_frame.pack(fill="x", padx=18, pady=8)
        
        self._v_outdir = tk.StringVar(value=str(DOWNLOADS / "Rekap"))
        FileRow(
            out_frame,
            "Folder Output",
            "",
            self._v_outdir,
            lambda: self._browse_dir(self._v_outdir),
            THEME["card"]
        ).pack(fill="x", padx=0, pady=(0, 8))
        
        fn_row = create_frame(out_frame, THEME["card"])
        fn_row.pack(fill="x", pady=(0, 6))
        create_label(fn_row, "Nama File Rekap :", "body", "muted").pack(side="left")
        self._v_fname = tk.StringVar(value="REKAP_ASSET_DISTRIBUSI.xlsx")
        from ui.theme import create_entry
        create_entry(fn_row, self._v_fname, wide=False).pack(side="left", padx=8, ipady=4)
        
        fn2_row = create_frame(out_frame, THEME["card"])
        fn2_row.pack(fill="x", pady=(0, 0))
        create_label(fn2_row, "Nama File Log :", "body", "muted").pack(side="left")
        self._v_logname = tk.StringVar(value="LOG_SUBCLASS_NOT_FOUND.xlsx")
        create_entry(fn2_row, self._v_logname, wide=False).pack(side="left", padx=8, ipady=4)
        
        # Section 4: Control
        create_section(form_frame, 4, "KONTROL")
        rb = create_frame(form_frame, THEME["card"])
        rb.pack(fill="x", padx=18, pady=(8, 6))
        self._run_btn = create_button(rb, "▶  REKAP REPORT", self._start, "run", width=22)
        self._run_btn.pack(side="left")
        create_button(rb, "🗑 Reset", self._reset_form, "dim", small=True).pack(side="right")
        
        self._make_progress(form_frame)
        
        # Section 5: Sheet Selector
        create_section(form_frame, 5, "SELECT SHEETS (Master Data)")
        self._sheet_sel = SheetSelector(form_frame)
        self._sheet_sel.pack(fill="both", expand=False, padx=18, pady=8)
        self._sheet_sel.config(height=150)
        
        # Section 6: Log
        create_section(form_frame, 6, "LOG PROSES")
        self._log_box = self._make_log_area(form_frame)
    
    def _load_master_file(self):
        """Load master file dan populate sheets."""
        self._browse_file(self._v_master)
        p = self._v_master.get()
        
        if p and os.path.exists(p):
            try:
                xl = pd.ExcelFile(p)
                self._sheet_sel.load(xl.sheet_names)
                self._log(f"  ✓ {len(xl.sheet_names)} sheet dimuat", "success")
            except Exception as e:
                self._log(f"  ✗ {e}", "error")
    
    def _reset_form(self):
        """Reset form."""
        self._v_template.set("")
        self._v_master.set("")
        self._log_box.clear()
        self._log("Form direset", "dim")
    
    def _start(self):
        """Start rekap process."""
        if self._running:
            return
        
        tpl = self._v_template.get().strip()
        master = self._v_master.get().strip()
        uid = self._v_uid.get().strip()
        fmode = self._v_filter.get()
        out_dir = self._v_outdir.get().strip()
        fname = self._v_fname.get().strip()
        logname = self._v_logname.get().strip()
        selected = self._sheet_sel.selected()
        
        # Validation
        errors = []
        if not tpl:
            errors.append("Pilih file Template/Config (Rekap.xlsx)")
        elif not os.path.exists(tpl):
            errors.append(f"File template tidak ada: {tpl}")
        
        if not master:
            errors.append("Pilih file Master Data")
        elif not os.path.exists(master):
            errors.append(f"File master tidak ada: {master}")
        
        if not out_dir:
            errors.append("Pilih folder output")
        
        if errors:
            messagebox.showerror("Validasi", "\n".join(errors))
            return
        
        os.makedirs(out_dir, exist_ok=True)
        out_rekap = os.path.join(out_dir, fname)
        out_log = os.path.join(out_dir, "Logs", logname)
        
        self._disable_run(self._run_btn, "⏳ Memproses...")
        self._set_progress(0)
        
        fl = ModuleLogger("REKAP", os.path.join(out_dir, "Logs"))
        threading.Thread(
            target=self._run,
            args=(tpl, master, uid, fmode, out_rekap, out_log, selected, fl),
            daemon=True
        ).start()
    
    def _run(self, tpl, master, uid, fmode, out_rekap, out_log, selected, fl):
        """Run engine in background."""
        try:
            eng = RekapEngine(self._log, self._set_progress, fl)
            stats = eng.run(tpl, master, uid, fmode, out_rekap, out_log, selected)
            
            def _done():
                self._enable_run(self._run_btn, "▶  REKAP REPORT")
                self._set_progress(100)
                self._log("─" * 50, "sep")
                
                msg = (f"✅ SELESAI\n\n"
                       f"Owner  : {stats['owners']}\n"
                       f"Waktu  : {stats['elapsed']}s\n"
                       f"File   : {Path(out_rekap).name}")
                
                if stats["not_found"]:
                    msg += f"\n\n⚠️  {stats['not_found']} baris SUBCLASS tidak ditemukan"
                    msg += f"\n    Lihat: {Path(out_log).name}"
                
                if messagebox.askyesno("Selesai", msg + "\n\nBuka folder output?"):
                    os.startfile(Path(out_rekap).parent)
            
            self.after(0, _done)
        
        except Exception as e:
            tb = traceback.format_exc()
            def _err():
                self._log(f"✗ {e}", "error")
                self._log(tb, "dim")
                self._enable_run(self._run_btn, "▶  REKAP REPORT")
                messagebox.showerror("Error", str(e))
            self.after(0, _err)