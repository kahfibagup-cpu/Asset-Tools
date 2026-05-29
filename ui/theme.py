"""
UI Theme dan styling utilities.
"""

import tkinter as tk
from config import THEME, FONTS


def create_frame(parent, bg=None, **kwargs):
    """Create styled frame."""
    bg = bg or THEME["bg"]
    return tk.Frame(parent, bg=bg, **kwargs)


def create_label(parent, text, font="body", color="text", **kwargs):
    """Create styled label."""
    bg = parent.cget("bg") if hasattr(parent, "cget") else THEME["bg"]
    return tk.Label(
        parent,
        text=text,
        font=FONTS[font],
        fg=THEME[color],
        bg=bg,
        **kwargs
    )


def create_button(parent, text, cmd, style="normal", small=False, width=None):
    """Create styled button with hover effects."""
    styles = {
        "normal": (THEME["card"], THEME["text"], THEME["border"]),
        "run": (THEME["accent2"], THEME["white"], THEME["accent"]),
        "danger": (THEME["card"], THEME["danger"], THEME["border"]),
        "dim": (THEME["bg2"], THEME["muted"], THEME["border"]),
    }
    bg, fg, hv = styles.get(style, styles["normal"])
    pady = 3 if small else 7
    fnt = FONTS["small"] if small else ("Segoe UI", 9, "bold")
    
    kw = dict(
        text=text,
        command=cmd,
        font=fnt,
        fg=fg,
        bg=bg,
        activebackground=hv,
        activeforeground=fg,
        relief="flat",
        cursor="hand2",
        padx=10,
        pady=pady,
        bd=0,
        highlightthickness=1,
        highlightbackground=THEME["border"]
    )
    if width:
        kw["width"] = width
    
    btn = tk.Button(parent, **kw)
    btn.bind("<Enter>", lambda e: btn.config(bg=hv))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def create_entry(parent, var, wide=True, mono=False, **kwargs):
    """Create styled entry widget."""
    fnt = FONTS["mono"] if mono else FONTS["body"]
    w = 60 if wide else 30
    return tk.Entry(
        parent,
        textvariable=var,
        font=fnt,
        fg=THEME["text"],
        bg=THEME["card"],
        insertbackground=THEME["accent"],
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
        **kwargs
    )


def create_section(parent, num, title):
    """Create section header with accent bar."""
    f = create_frame(parent, THEME["bg2"])
    f.pack(fill="x")
    
    tk.Frame(f, bg=THEME["accent"], width=4).pack(side="left", fill="y")
    
    num_text = f" {num:02d} " if isinstance(num, int) else f" {num} "
    create_label(f, num_text, "small", "muted").pack(side="left", padx=(8, 4), pady=10)
    create_label(f, title, "label", "text").pack(side="left", pady=10)
    tk.Label(f, text="●", font=("Segoe UI", 8), fg=THEME["accent"], bg=THEME["bg2"]).pack(side="right", padx=14)
    
    tk.Frame(parent, bg=THEME["border"], height=1).pack(fill="x")