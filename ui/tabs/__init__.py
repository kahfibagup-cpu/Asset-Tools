"""
Tab components untuk Asset Distribution Tools.
Berisi: TabKonsolidasi, TabSplit, TabAdvancedSplit, TabRekap
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from config import THEME, FONTS
from ui.theme import create_frame, create_label, create_button, create_section
from ui.widgets import LogBox, ProgressBar, SheetSelector, FileRow
from core.konsolidasi_engine import KonsolidasiEngine
from core.split_engine import SplitEngine
from core.advanced_split_engine import AdvancedSplitEngine
from core.rekap_engine import RekapEngine
from utils import ModuleLogger


class TabKonsolidasi(tk.Frame):
    """Tab untuk Konsolidasi Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Konsolidasi tab UI."""
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)
        
        content = create_frame(canvas, THEME["bg"])
        window = canvas.create_window(0, 0, window=content, anchor="nw")
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window, width=e.width)
        
        content.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._master_file = tk.StringVar()
        FileRow(file_frame, "File Master (UNIT_MASTER):", "File Excel dengan sheet UNIT_MASTER", 
                self._master_file, self._browse_master).pack(fill="x", pady=(0, 8))
        
        self._source_files = tk.StringVar()
        FileRow(file_frame, "File Source:", "File(s) Excel untuk dikonsolidasi", 
                self._source_files, self._browse_sources).pack(fill="x")
        
        create_section(content, 2, "Pilih Sheet")
        sheet_frame = create_frame(content, THEME["bg"])
        sheet_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        self._sheet_selector = SheetSelector(sheet_frame)
        self._sheet_selector.pack(fill="both", expand=True)
        
        create_section(content, 3, "Pengaturan Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_file = tk.StringVar()
        FileRow(output_frame, "File Output:", "Lokasi file hasil konsolidasi", 
                self._output_file, self._browse_output).pack(fill="x")
        
        create_section(content, 4, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Konsolidasi", self._run_consolidation, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_master(self):
        file = filedialog.askopenfilename(
            title="Pilih File Master (UNIT_MASTER)",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if file:
            self._master_file.set(file)
            self._log.write(f"Master dipilih: {Path(file).name}", "info")
    
    def _browse_sources(self):
        files = filedialog.askopenfilenames(
            title="Pilih File Source",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if files:
            self._source_files.set(";".join(files))
            self._log.write(f"{len(files)} file source dipilih", "info")
    
    def _browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Simpan File Output",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
        )
        if file:
            self._output_file.set(file)
    
    def _run_consolidation(self):
        """Run consolidation in background thread."""
        if not self._master_file.get():
            messagebox.showerror("Error", "Pilih file Master terlebih dahulu!")
            return
        if not self._source_files.get():
            messagebox.showerror("Error", "Pilih file Source terlebih dahulu!")
            return
        if not self._output_file.get():
            messagebox.showerror("Error", "Tentukan file Output terlebih dahulu!")
            return
        
        self._log.clear()
        self._log.write("Konsolidasi dimulai...", "info")
        
        def worker():
            try:
                engine = KonsolidasiEngine(
                    log_callback=self._log.write,
                    progress_callback=self._progress.set
                )
                
                source_files = [f.strip() for f in self._source_files.get().split(";")]
                stats = engine.run(
                    master_path=self._master_file.get(),
                    source_paths=source_files,
                    output_path=self._output_file.get()
                )
                
                msg = f"✓ Selesai! {stats['total_sheets']} sheet, {stats['total_rows']:,} baris dalam {stats['elapsed']}s"
                self._log.write(msg, "success")
                messagebox.showinfo("Sukses", msg)
            except Exception as e:
                self._log.write(f"✗ Error: {str(e)}", "error")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _reset(self):
        self._master_file.set("")
        self._source_files.set("")
        self._output_file.set("")
        self._log.clear()
        self._progress.set(0)


class TabSplit(tk.Frame):
    """Tab untuk Split Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Split tab UI."""
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)
        
        content = create_frame(canvas, THEME["bg"])
        window = canvas.create_window(0, 0, window=content, anchor="nw")
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window, width=e.width)
        
        content.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._master_file = tk.StringVar()
        FileRow(file_frame, "File Master (UNIT_MASTER):", "File Excel dengan mapping UP3", 
                self._master_file, self._browse_master).pack(fill="x", pady=(0, 8))
        
        self._data_file = tk.StringVar()
        FileRow(file_frame, "File Data:", "File Excel untuk di-split per UP3", 
                self._data_file, self._browse_data).pack(fill="x")
        
        create_section(content, 2, "Pilih Sheet")
        sheet_frame = create_frame(content, THEME["bg"])
        sheet_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        self._sheet_selector = SheetSelector(sheet_frame)
        self._sheet_selector.pack(fill="both", expand=True)
        
        create_section(content, 3, "Lokasi Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_dir = tk.StringVar()
        
        output_row = create_frame(output_frame, THEME["bg"])
        output_row.pack(fill="x", pady=(4, 0))
        
        entry = tk.Entry(output_row, textvariable=self._output_dir, font=FONTS["body"],
                fg=THEME["text"], bg=THEME["card"], relief="flat", bd=0,
                highlightthickness=1, highlightbackground=THEME["border"],
                insertbackground=THEME["accent"])
        entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        
        create_button(output_row, "📂 Browse…", self._browse_output_dir, "dim", small=True).pack(side="right")
        
        create_section(content, 4, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Split", self._run_split, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_master(self):
        file = filedialog.askopenfilename(
            title="Pilih File Master",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file:
            self._master_file.set(file)
            self._log.write(f"Master dipilih: {Path(file).name}", "info")
    
    def _browse_data(self):
        file = filedialog.askopenfilename(
            title="Pilih File Data",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file:
            self._data_file.set(file)
            self._log.write(f"Data file dipilih: {Path(file).name}", "info")
    
    def _browse_output_dir(self):
        dir = filedialog.askdirectory(title="Pilih Folder Output")
        if dir:
            self._output_dir.set(dir)
            self._log.write(f"Output dir: {Path(dir).name}", "info")
    
    def _run_split(self):
        if not self._master_file.get():
            messagebox.showerror("Error", "Pilih file Master!")
            return
        if not self._data_file.get():
            messagebox.showerror("Error", "Pilih file Data!")
            return
        if not self._output_dir.get():
            messagebox.showerror("Error", "Tentukan folder Output!")
            return
        
        self._log.clear()
        self._log.write("Split dimulai...", "info")
        
        def worker():
            try:
                engine = SplitEngine(
                    log_callback=self._log.write,
                    progress_callback=self._progress.set
                )
                
                engine.load_master(self._master_file.get())
                stats = engine.run(
                    data_path=self._data_file.get(),
                    output_dir=self._output_dir.get(),
                    selected_sheets=self._sheet_selector.selected()
                )
                
                msg = f"✓ Selesai! {stats['total_files']} file, {stats['total_rows']:,} baris dalam {stats['elapsed']}s"
                self._log.write(msg, "success")
                messagebox.showinfo("Sukses", msg)
            except Exception as e:
                self._log.write(f"✗ Error: {str(e)}", "error")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _reset(self):
        self._master_file.set("")
        self._data_file.set("")
        self._output_dir.set("")
        self._log.clear()
        self._progress.set(0)


class TabAdvancedSplit(tk.Frame):
    """Tab untuk Advanced Split Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Advanced Split tab UI."""
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)
        
        content = create_frame(canvas, THEME["bg"])
        window = canvas.create_window(0, 0, window=content, anchor="nw")
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window, width=e.width)
        
        content.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._data_file = tk.StringVar()
        FileRow(file_frame, "File Data:", "File Excel untuk di-split", 
                self._data_file, self._browse_data).pack(fill="x")
        
        create_section(content, 2, "Pengaturan Lanjutan")
        settings_frame = create_frame(content, THEME["bg"])
        settings_frame.pack(fill="x", padx=16, pady=12)
        
        create_label(settings_frame, "Pilih Kolom Split:", "small", "text").pack(anchor="w")
        self._split_col = tk.StringVar(value="")
        
        col_row = create_frame(settings_frame, THEME["bg"])
        col_row.pack(fill="x", pady=(4, 0))
        tk.Entry(col_row, textvariable=self._split_col, font=FONTS["body"],
                fg=THEME["text"], bg=THEME["card"], relief="flat", bd=0,
                highlightthickness=1, highlightbackground=THEME["border"],
                insertbackground=THEME["accent"]).pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        create_button(col_row, "📋 Pilih...", self._select_column, "dim", small=True).pack(side="right")
        
        create_section(content, 3, "Pilih Sheet")
        sheet_frame = create_frame(content, THEME["bg"])
        sheet_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        self._sheet_selector = SheetSelector(sheet_frame)
        self._sheet_selector.pack(fill="both", expand=True)
        
        create_section(content, 4, "Lokasi Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_dir = tk.StringVar()
        
        output_row = create_frame(output_frame, THEME["bg"])
        output_row.pack(fill="x", pady=(4, 0))
        
        entry = tk.Entry(output_row, textvariable=self._output_dir, font=FONTS["body"],
                fg=THEME["text"], bg=THEME["card"], relief="flat", bd=0,
                highlightthickness=1, highlightbackground=THEME["border"],
                insertbackground=THEME["accent"])
        entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))
        
        create_button(output_row, "📂 Browse…", self._browse_output_dir, "dim", small=True).pack(side="right")
        
        create_section(content, 5, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Advanced Split", self._run_advanced_split, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_data(self):
        file = filedialog.askopenfilename(
            title="Pilih File Data",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file:
            self._data_file.set(file)
            self._log.write(f"Data file dipilih: {Path(file).name}", "info")
    
    def _select_column(self):
        if not self._data_file.get():
            messagebox.showerror("Error", "Pilih file Data terlebih dahulu!")
            return
        
        try:
            engine = AdvancedSplitEngine()
            cols = engine.get_columns(self._data_file.get(), 0)
            
            if not cols:
                messagebox.showerror("Error", "Tidak ada kolom ditemukan!")
                return
            
            top = tk.Toplevel(self)
            top.title("Pilih Kolom")
            top.geometry("300x400")
            
            frame = create_frame(top, THEME["bg"])
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            create_label(frame, "Pilih kolom untuk split:", "label", "text").pack(anchor="w", pady=(0, 8))
            
            listbox = tk.Listbox(frame, font=FONTS["body"], fg=THEME["text"], 
                               bg=THEME["card"], relief="flat", bd=0, highlightthickness=1,
                               highlightbackground=THEME["border"])
            listbox.pack(fill="both", expand=True, ipady=5)
            
            for col in cols:
                listbox.insert(tk.END, col)
            
            def select():
                sel = listbox.curselection()
                if sel:
                    self._split_col.set(cols[sel[0]])
                    self._log.write(f"Kolom dipilih: {cols[sel[0]]}", "info")
                    top.destroy()
            
            btn_frame = create_frame(frame, THEME["bg"])
            btn_frame.pack(fill="x", pady=(8, 0))
            
            create_button(btn_frame, "✓ OK", select, "run", small=True).pack(side="left", padx=(0, 4))
            create_button(btn_frame, "✕ Batal", top.destroy, "dim", small=True).pack(side="left")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _browse_output_dir(self):
        dir = filedialog.askdirectory(title="Pilih Folder Output")
        if dir:
            self._output_dir.set(dir)
            self._log.write(f"Output dir: {Path(dir).name}", "info")
    
    def _run_advanced_split(self):
        if not self._data_file.get():
            messagebox.showerror("Error", "Pilih file Data!")
            return
        if not self._split_col.get():
            messagebox.showerror("Error", "Pilih kolom untuk split!")
            return
        if not self._output_dir.get():
            messagebox.showerror("Error", "Tentukan folder Output!")
            return
        
        self._log.clear()
        self._log.write("Advanced Split dimulai...", "info")
        
        def worker():
            try:
                engine = AdvancedSplitEngine(
                    log_callback=self._log.write,
                    progress_callback=self._progress.set
                )
                
                stats = engine.run(
                    data_path=self._data_file.get(),
                    output_dir=self._output_dir.get(),
                    split_col=self._split_col.get(),
                    selected_sheets=self._sheet_selector.selected()
                )
                
                msg = f"✓ Selesai! {stats['total_files']} file, {stats['total_rows']:,} baris dalam {stats['elapsed']}s"
                self._log.write(msg, "success")
                messagebox.showinfo("Sukses", msg)
            except Exception as e:
                self._log.write(f"✗ Error: {str(e)}", "error")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _reset(self):
        self._data_file.set("")
        self._split_col.set("")
        self._output_dir.set("")
        self._log.clear()
        self._progress.set(0)


class TabRekap(tk.Frame):
    """Tab untuk Rekap UP3 Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Rekap tab UI."""
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)
        
        content = create_frame(canvas, THEME["bg"])
        window = canvas.create_window(0, 0, window=content, anchor="nw")
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window, width=e.width)
        
        content.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        
        create_section(content, 1, "Pilih Template & Data")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._template_file = tk.StringVar()
        FileRow(file_frame, "File Template:", "File template Excel dengan CONFIG dan UNIT_MASTER", 
                self._template_file, self._browse_template).pack(fill="x", pady=(0, 8))
        
        self._master_file = tk.StringVar()
        FileRow(file_frame, "File Master Data:", "File Excel dengan data master", 
                self._master_file, self._browse_master).pack(fill="x")
        
        create_section(content, 2, "Pilih Sheet")
        sheet_frame = create_frame(content, THEME["bg"])
        sheet_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        self._sheet_selector = SheetSelector(sheet_frame)
        self._sheet_selector.pack(fill="both", expand=True)
        
        create_section(content, 3, "Pengaturan Output")
        settings_frame = create_frame(content, THEME["bg"])
        settings_frame.pack(fill="x", padx=16, pady=12)
        
        self._uid = tk.StringVar()
        FileRow(settings_frame, "UID/Kode Unit:", "Kode unit untuk rekap (opsional)", 
                self._uid, None).pack(fill="x", pady=(0, 8))
        
        create_label(settings_frame, "Mode Filter:", "small", "text").pack(anchor="w")
        self._filter_mode = tk.StringVar(value="0")
        
        for text, val in [("Semua data", "0"), ("Hanya yang ada data", "1")]:
            tk.Radiobutton(settings_frame, text=text, variable=self._filter_mode,
                          value=val, font=FONTS["small"], fg=THEME["text"], 
                          bg=THEME["bg"], selectcolor=THEME["accent"],
                          activebackground=THEME["bg"]).pack(anchor="w", pady=2)
        
        create_section(content, 4, "Lokasi Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_rekap = tk.StringVar()
        FileRow(output_frame, "File Rekap Output:", "Lokasi file rekap hasil", 
                self._output_rekap, self._browse_output_rekap).pack(fill="x", pady=(0, 8))
        
        self._output_log = tk.StringVar()
        FileRow(output_frame, "File Log Output:", "Lokasi file log (opsional)", 
                self._output_log, self._browse_output_log).pack(fill="x")
        
        create_section(content, 5, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Rekap", self._run_recap, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_template(self):
        file = filedialog.askopenfilename(
            title="Pilih File Template",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file:
            self._template_file.set(file)
            self._log.write(f"Template dipilih: {Path(file).name}", "info")
    
    def _browse_master(self):
        file = filedialog.askopenfilename(
            title="Pilih File Master Data",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file:
            self._master_file.set(file)
            self._log.write(f"Master data dipilih: {Path(file).name}", "info")
    
    def _browse_output_rekap(self):
        file = filedialog.asksaveasfilename(
            title="Simpan File Rekap",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file:
            self._output_rekap.set(file)
    
    def _browse_output_log(self):
        file = filedialog.asksaveasfilename(
            title="Simpan File Log",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file:
            self._output_log.set(file)
    
    def _run_recap(self):
        if not self._template_file.get():
            messagebox.showerror("Error", "Pilih file Template!")
            return
        if not self._master_file.get():
            messagebox.showerror("Error", "Pilih file Master Data!")
            return
        if not self._output_rekap.get():
            messagebox.showerror("Error", "Tentukan file Output Rekap!")
            return
        
        self._log.clear()
        self._log.write("Rekap dimulai...", "info")
        
        def worker():
            try:
                engine = RekapEngine(
                    log_callback=self._log.write,
                    progress_callback=self._progress.set
                )
                
                stats = engine.run(
                    template_path=self._template_file.get(),
                    master_path=self._master_file.get(),
                    uid=self._uid.get(),
                    filter_mode=int(self._filter_mode.get()),
                    out_rekap=self._output_rekap.get(),
                    out_log=self._output_log.get(),
                    selected_sheets=self._sheet_selector.selected() or None
                )
                
                msg = f"✓ Selesai! {stats['owners']} owner dalam {stats['elapsed']}s"
                if stats['not_found'] > 0:
                    msg += f"\n⚠ {stats['not_found']} baris tidak terpetakan (lihat log)"
                
                self._log.write(msg, "success")
                messagebox.showinfo("Sukses", msg)
            except Exception as e:
                self._log.write(f"✗ Error: {str(e)}", "error")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _reset(self):
        self._template_file.set("")
        self._master_file.set("")
        self._uid.set("")
        self._output_rekap.set("")
        self._output_log.set("")
        self._filter_mode.set("0")
        self._log.clear()
        self._progress.set(0)


__all__ = [
    'TabKonsolidasi',
    'TabSplit',
    'TabAdvancedSplit',
    'TabRekap'
]
