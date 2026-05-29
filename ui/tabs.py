"""
Tab components untuk Asset Distribution Tools.
Berisi: TabKonsolidasi, TabSplit, TabAdvancedSplit, TabRekap
"""

import tkinter as tk
from config import THEME, FONTS
from ui.theme import create_frame, create_label, create_button, create_section
from ui.widgets import LogBox, ProgressBar, SheetSelector, FileRow


class TabKonsolidasi(tk.Frame):
    """Tab untuk Konsolidasi Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Konsolidasi tab UI."""
        # Scroll container
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
        
        # Section 1: File Input
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._input_file = tk.StringVar()
        FileRow(file_frame, "File Excel:", "Pilih file Excel untuk dikonsolidasi", 
                self._input_file, self._browse_input).pack(fill="x", pady=(0, 8))
        
        # Section 2: Sheet Selection
        create_section(content, 2, "Pilih Sheet")
        sheet_frame = create_frame(content, THEME["bg"])
        sheet_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        self._sheet_selector = SheetSelector(sheet_frame)
        self._sheet_selector.pack(fill="both", expand=True)
        
        # Section 3: Output
        create_section(content, 3, "Pengaturan Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_file = tk.StringVar()
        FileRow(output_frame, "File Output:", "Lokasi file hasil konsolidasi", 
                self._output_file, self._browse_output).pack(fill="x")
        
        # Section 4: Action
        create_section(content, 4, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Konsolidasi", self._run_consolidation, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        # Progress bar
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        # Log box
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_input(self):
        """Browse input file."""
        self._log.write("Browse input file dipilih", "dim")
    
    def _browse_output(self):
        """Browse output file."""
        self._log.write("Browse output file dipilih", "dim")
    
    def _run_consolidation(self):
        """Run consolidation process."""
        self._log.write("Memulai proses konsolidasi...", "info")
        self._progress.set(0)
        # TODO: Implement consolidation logic
        self._log.write("Konsolidasi selesai!", "success")
        self._progress.set(100)
    
    def _reset(self):
        """Reset form."""
        self._input_file.set("")
        self._output_file.set("")
        self._log.clear()
        self._progress.set(0)
        self._log.write("Form direset", "dim")


class TabSplit(tk.Frame):
    """Tab untuk Split Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Split tab UI."""
        # Scroll container
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
        
        # Section 1: File Input
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._input_file = tk.StringVar()
        FileRow(file_frame, "File Excel:", "Pilih file Excel untuk di-split", 
                self._input_file, self._browse_input).pack(fill="x", pady=(0, 8))
        
        # Section 2: Split Settings
        create_section(content, 2, "Pengaturan Split")
        settings_frame = create_frame(content, THEME["bg"])
        settings_frame.pack(fill="x", padx=16, pady=12)
        
        create_label(settings_frame, "Jumlah file output:", "small", "text").pack(anchor="w")
        self._split_count = tk.StringVar(value="2")
        tk.Entry(settings_frame, textvariable=self._split_count, font=FONTS["body"],
                fg=THEME["text"], bg=THEME["card"], relief="flat", bd=0,
                highlightthickness=1, highlightbackground=THEME["border"],
                width=10).pack(anchor="w", pady=(4, 0))
        
        # Section 3: Output Location
        create_section(content, 3, "Lokasi Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_dir = tk.StringVar()
        FileRow(output_frame, "Folder Output:", "Pilih folder untuk menyimpan file hasil split", 
                self._output_dir, self._browse_output).pack(fill="x")
        
        # Section 4: Action
        create_section(content, 4, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Split", self._run_split, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        # Progress bar
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        # Log box
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_input(self):
        """Browse input file."""
        self._log.write("Browse input file dipilih", "dim")
    
    def _browse_output(self):
        """Browse output directory."""
        self._log.write("Browse output directory dipilih", "dim")
    
    def _run_split(self):
        """Run split process."""
        self._log.write("Memulai proses split...", "info")
        self._progress.set(0)
        # TODO: Implement split logic
        self._log.write("Split selesai!", "success")
        self._progress.set(100)
    
    def _reset(self):
        """Reset form."""
        self._input_file.set("")
        self._output_dir.set("")
        self._split_count.set("2")
        self._log.clear()
        self._progress.set(0)
        self._log.write("Form direset", "dim")


class TabAdvancedSplit(tk.Frame):
    """Tab untuk Advanced Split Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Advanced Split tab UI."""
        # Scroll container
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
        
        # Section 1: File Input
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._input_file = tk.StringVar()
        FileRow(file_frame, "File Excel:", "Pilih file Excel untuk advanced split", 
                self._input_file, self._browse_input).pack(fill="x", pady=(0, 8))
        
        # Section 2: Advanced Settings
        create_section(content, 2, "Pengaturan Lanjutan")
        settings_frame = create_frame(content, THEME["bg"])
        settings_frame.pack(fill="x", padx=16, pady=12)
        
        create_label(settings_frame, "Mode Split:", "small", "text").pack(anchor="w")
        self._split_mode = tk.StringVar(value="by_count")
        
        modes = [("Berdasarkan Jumlah", "by_count"), 
                ("Berdasarkan Kriteria", "by_criteria")]
        for text, val in modes:
            tk.Radiobutton(settings_frame, text=text, variable=self._split_mode, 
                          value=val, font=FONTS["small"], fg=THEME["text"], 
                          bg=THEME["bg"], selectcolor=THEME["accent"],
                          activebackground=THEME["bg"]).pack(anchor="w", pady=2)
        
        # Section 3: Output Location
        create_section(content, 3, "Lokasi Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_dir = tk.StringVar()
        FileRow(output_frame, "Folder Output:", "Pilih folder untuk menyimpan file hasil", 
                self._output_dir, self._browse_output).pack(fill="x")
        
        # Section 4: Action
        create_section(content, 4, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Advanced Split", self._run_advanced_split, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        # Progress bar
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        # Log box
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_input(self):
        """Browse input file."""
        self._log.write("Browse input file dipilih", "dim")
    
    def _browse_output(self):
        """Browse output directory."""
        self._log.write("Browse output directory dipilih", "dim")
    
    def _run_advanced_split(self):
        """Run advanced split process."""
        self._log.write("Memulai proses advanced split...", "info")
        self._progress.set(0)
        # TODO: Implement advanced split logic
        self._log.write("Advanced split selesai!", "success")
        self._progress.set(100)
    
    def _reset(self):
        """Reset form."""
        self._input_file.set("")
        self._output_dir.set("")
        self._split_mode.set("by_count")
        self._log.clear()
        self._progress.set(0)
        self._log.write("Form direset", "dim")


class TabRekap(tk.Frame):
    """Tab untuk Rekap UP3 Assets."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=THEME["bg"])
        self.app = app
        self._build()
    
    def _build(self):
        """Build Rekap tab UI."""
        # Scroll container
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
        
        # Section 1: File Input
        create_section(content, 1, "Pilih File Input")
        file_frame = create_frame(content, THEME["bg"])
        file_frame.pack(fill="x", padx=16, pady=12)
        
        self._input_file = tk.StringVar()
        FileRow(file_frame, "File Excel:", "Pilih file Excel untuk di-rekap", 
                self._input_file, self._browse_input).pack(fill="x", pady=(0, 8))
        
        # Section 2: Rekap Settings
        create_section(content, 2, "Pengaturan Rekap")
        settings_frame = create_frame(content, THEME["bg"])
        settings_frame.pack(fill="x", padx=16, pady=12)
        
        create_label(settings_frame, "Pilih UP3:", "small", "text").pack(anchor="w")
        self._up3_selector = SheetSelector(settings_frame)
        self._up3_selector.pack(fill="both", expand=True, ipady=5)
        
        # Section 3: Output Location
        create_section(content, 3, "Lokasi Output")
        output_frame = create_frame(content, THEME["bg"])
        output_frame.pack(fill="x", padx=16, pady=12)
        
        self._output_file = tk.StringVar()
        FileRow(output_frame, "File Output:", "Lokasi file hasil rekap", 
                self._output_file, self._browse_output).pack(fill="x")
        
        # Section 4: Action
        create_section(content, 4, "Proses")
        action_frame = create_frame(content, THEME["bg"])
        action_frame.pack(fill="x", padx=16, pady=12)
        
        create_button(action_frame, "▶ Mulai Rekap", self._run_recap, 
                     "run", width=40).pack(side="left", padx=(0, 8))
        create_button(action_frame, "⟲ Reset", self._reset, "dim").pack(side="left")
        
        # Progress bar
        self._progress = ProgressBar(content)
        self._progress.pack(fill="x", padx=16, pady=(12, 0))
        
        # Log box
        log_frame = create_frame(content, THEME["bg"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        create_label(log_frame, "📋 Log Aktivitas", "label", "text").pack(anchor="w")
        self._log = LogBox(log_frame)
        self._log.pack(fill="both", expand=True, pady=(4, 0))
    
    def _browse_input(self):
        """Browse input file."""
        self._log.write("Browse input file dipilih", "dim")
    
    def _browse_output(self):
        """Browse output file."""
        self._log.write("Browse output file dipilih", "dim")
    
    def _run_recap(self):
        """Run recap process."""
        self._log.write("Memulai proses rekap UP3...", "info")
        self._progress.set(0)
        # TODO: Implement recap logic
        self._log.write("Rekap selesai!", "success")
        self._progress.set(100)
    
    def _reset(self):
        """Reset form."""
        self._input_file.set("")
        self._output_file.set("")
        self._log.clear()
        self._progress.set(0)
        self._log.write("Form direset", "dim")
