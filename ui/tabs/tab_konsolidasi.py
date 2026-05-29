"""
Tab ① Konsolidasi - Merge multi-file Excel dengan UI baru.
"""

import os
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from ui.tabs.base_tab import BaseTab
from ui.theme import create_frame, create_label, create_button, create_section, THEME, FONTS
from ui.widgets import FileRow
from core import KonsolidasiEngine
from utils import ModuleLogger, get_log_dir
from config.constants import DOWNLOADS


class TabKonsolidasi(BaseTab):
    """Tab untuk proses Konsolidasi."""
    
    def _build(self):
        """Build UI dengan layout scrollable."""
        # Main container dengan scroll
        main_container = create_frame(self, THEME["bg"])
        main_container.pack(fill="both", expand=True)
        
        # Canvas untuk scrolling
        canvas = tk.Canvas(
            main_container,
            bg=THEME["bg"],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(main_container, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame untuk content
        self._scroll_frame = create_frame(canvas, THEME["bg"])
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        
        # Bind scroll
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self._scroll_frame.bind("<Configure>", on_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # Build content
        self._build_content()
    
    def _build_content(self):
        """Build form content."""
        # Header
        hdr = create_frame(self._scroll_frame, THEME["bg2"])
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=THEME["accent"], height=3).pack(fill="x")
        
        ih = create_frame(hdr, THEME["bg2"])
        ih.pack(fill="x", padx=24, pady=12)
        create_label(ih, "① Konsolidasi Multi-File", "title", "text").pack(side="left")
        create_label(ih, "Gabungkan beberapa file Excel menjadi satu output", "subtitle", "muted").pack(
            side="left", padx=20
        )
        
        # Form content
        form_frame = create_frame(self._scroll_frame, THEME["bg"])
        form_frame.pack(fill="x", padx=18, pady=10)
        
        # Section 1: File Input/Output
        create_section(form_frame, 1, "FILE INPUT / OUTPUT")
        
        self._v_master = tk.StringVar()
        FileRow(
            form_frame,
            "Data Master Induk (.xlsx)",
            "Berisi sheet UNIT_MASTER + sheet template per kategori",
            self._v_master,
            lambda: self._browse_file(self._v_master),
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(8, 0))
        
        tk.Frame(form_frame, bg=THEME["border"], height=1).pack(fill="x", padx=18, pady=10)
        
        # Source files list
        sh_row = create_frame(form_frame, THEME["card"])
        sh_row.pack(fill="x", padx=18, pady=(0, 6))
        create_label(sh_row, "File Sumber (multi)", "label", "text").pack(side="left")
        self._cnt_lbl = create_label(sh_row, "0 file", "small", "muted")
        self._cnt_lbl.pack(side="right")
        
        # Listbox
        lb_wrap = create_frame(form_frame, THEME["bg"])
        lb_wrap.pack(fill="both", expand=True, padx=18, pady=(0, 6), ipady=80)
        
        sb = tk.Scrollbar(lb_wrap)
        sb.pack(side="right", fill="y")
        
        self._listbox = tk.Listbox(
            lb_wrap,
            font=FONTS["mono"],
            fg=THEME["text"],
            bg=THEME["card"],
            selectbackground=THEME["border"],
            activestyle="none",
            relief="flat",
            bd=0,
            yscrollcommand=sb.set
        )
        self._listbox.pack(fill="both", expand=True, padx=6, pady=6)
        sb.config(command=self._listbox.yview)
        self._listbox.bind("<Double-Button-1>", lambda e: self._remove_sel())
        self._source_files = []
        
        # Buttons
        br = create_frame(form_frame, THEME["card"])
        br.pack(fill="x", padx=18, pady=(0, 6))
        create_button(br, "+ Tambah", self._add_sources, "dim", small=True).pack(side="left")
        create_button(br, "− Hapus Dipilih", self._remove_sel, "dim", small=True).pack(side="left", padx=5)
        create_button(br, "Hapus Semua", self._clear_sources, "danger", small=True).pack(side="right")
        
        tk.Frame(form_frame, bg=THEME["border"], height=1).pack(fill="x", padx=18, pady=10)
        
        # Output file
        self._v_output = tk.StringVar(value=str(DOWNLOADS / "Konsolidasi.xlsx"))
        FileRow(
            form_frame,
            "File Output (.xlsx / .csv)",
            "Path lengkap untuk menyimpan hasil konsolidasi",
            self._v_output,
            self._browse_output,
            THEME["card"]
        ).pack(fill="x", padx=18, pady=(0, 10))
        
        # Format selection
        fr = create_frame(form_frame, THEME["card"])
        fr.pack(fill="x", padx=18, pady=(0, 10))
        create_label(fr, "Format :", "body", "muted").pack(side="left")
        self._v_fmt = tk.StringVar(value="xlsx")
        for f in ["xlsx", "csv"]:
            tk.Radiobutton(
                fr,
                text=f.upper(),
                variable=self._v_fmt,
                value=f,
                bg=THEME["card"],
                fg=THEME["text"],
                selectcolor=THEME["bg"],
                activebackground=THEME["card"],
                font=FONTS["body"]
            ).pack(side="left", padx=8)
        
        # Section 2: Statistics
        create_section(form_frame, 2, "STATISTIK")
        sr = create_frame(form_frame, THEME["card"])
        sr.pack(fill="x", padx=18, pady=8)
        self._sv_written = self._mini_stat(sr, "SHEET", "—")
        self._sv_skip = self._mini_stat(sr, "DISKIP", "—")
        self._sv_rows = self._mini_stat(sr, "BARIS", "—")
        self._sv_time = self._mini_stat(sr, "DETIK", "—")
        
        # Section 3: Run button + Progress
        create_section(form_frame, 3, "KONTROL")
        rb = create_frame(form_frame, THEME["card"])
        rb.pack(fill="x", padx=18, pady=(8, 6))
        self._run_btn = create_button(rb, "▶  JALANKAN KONSOLIDASI", self._start, "run", width=30)
        self._run_btn.pack(side="left")
        create_button(rb, "🗑 Reset", self._reset_form, "dim", small=True).pack(side="right")
        
        self._make_progress(form_frame)
        
        # Section 4: Log
        create_section(form_frame, 4, "LOG PROSES")
        self._log_box = self._make_log_area(form_frame)
    
    def _add_sources(self):
        """Add source files."""
        added = self._browse_files(self._source_files, self._listbox)
        if added:
            self._cnt_lbl.config(text=f"{len(self._source_files)} file")
        self._log(f"  {added} file ditambahkan", "info")
    
    def _remove_sel(self):
        """Remove selected files."""
        for i in reversed(self._listbox.curselection()):
            self._listbox.delete(i)
            self._source_files.pop(i)
        self._cnt_lbl.config(text=f"{len(self._source_files)} file")
    
    def _clear_sources(self):
        """Clear all source files."""
        self._listbox.delete(0, "end")
        self._source_files.clear()
        self._cnt_lbl.config(text="0 file")
        self._log("File sumber dikosongkan", "dim")
    
    def _browse_output(self):
        """Browse output file."""
        from tkinter import filedialog
        p = filedialog.asksaveasfilename(
            title="Simpan Output Sebagai",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")]
        )
        if p:
            self._v_output.set(p)
    
    def _reset_form(self):
        """Reset form ke default."""
        self._v_master.set("")
        self._v_output.set(str(DOWNLOADS / "Konsolidasi.xlsx"))
        self._clear_sources()
        self._log_box.clear()
    
    def _start(self):
        """Start konsolidasi process."""
        if self._running:
            return
        
        master = self._v_master.get().strip()
        output = self._v_output.get().strip()
        fmt = self._v_fmt.get()
        
        # Validation
        if not master:
            messagebox.showwarning("", "Pilih Data Master Induk")
            return
        if not self._source_files:
            messagebox.showwarning("", "Tambah file sumber")
            return
        if not output:
            messagebox.showwarning("", "Tentukan lokasi output")
            return
        
        self._disable_run(self._run_btn, "⏳ Memproses...")
        self._set_progress(0)
        
        log_dir = self._get_log_dir(output)
        fl = ModuleLogger("KONSOLIDASI", log_dir)
        
        threading.Thread(
            target=self._run,
            args=(master, list(self._source_files), output, fmt, fl),
            daemon=True
        ).start()
    
    def _run(self, master, sources, output, fmt, fl):
        """Run engine in background."""
        try:
            eng = KonsolidasiEngine(self._log, self._set_progress, fl)
            stats = eng.run(master, sources, output, fmt)
            
            def _done():
                self._sv_written.config(text=str(stats["written"]))
                self._sv_skip.config(text=str(stats["skipped"]))
                self._sv_rows.config(text=f"{stats['rows']:,}")
                self._sv_time.config(text=str(stats["elapsed"]))
                self._enable_run(self._run_btn, "▶  JALANKAN KONSOLIDASI")
                self._set_progress(100)
                self._log("─" * 50, "sep")
                self._log(
                    f"✅ SELESAI  ·  {stats['written']} sheet  ·  "
                    f"{stats['rows']:,} baris  ·  {stats['elapsed']}s",
                    "success"
                )
                
                if messagebox.askyesno("Selesai", "Proses berhasil!\nBuka folder output?"):
                    os.startfile(str(Path(output).parent))
            
            self.after(0, _done)
        
        except Exception as e:
            tb = traceback.format_exc()
            def _err():
                self._log(f"✗ ERROR: {e}", "error")
                self._log(tb, "dim")
                self._enable_run(self._run_btn, "▶  JALANKAN KONSOLIDASI")
                messagebox.showerror("Error", str(e))
            self.after(0, _err)