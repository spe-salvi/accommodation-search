import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import logging
from controller.report_generator import generate_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_input_form_merged():
    root = tk.Tk()
    root.title("Accommodations Search (Names & SIS IDs)")
    root.geometry("800x600")
    root.resizable(False, False)

    style = ttkb.Style()
    style.theme_use('pulse')

    # --- layout ---
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")

    canvas = tk.Canvas(main_frame, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    main_frame.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)

    inner = ttk.Frame(canvas, padding=16)
    frame_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_config(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner.bind("<Configure>", _on_inner_config)

    def _on_canvas_config(event):
        canvas.itemconfig(frame_id, width=event.width)
    canvas.bind("<Configure>", _on_canvas_config)

    # ---- fields: simplified (one combined field for course & one for student) ----
    field_info = [
        "Term Name",
        "Course (Name / SIS ID / Code)",
        "Student (Name / SIS ID / Login)",
        "Quiz Name",
    ]

    entry_vars = {}
    entry_widgets = {}

    for i, label_key in enumerate(field_info):
        ttk.Label(inner, text=f"{label_key}:").grid(
            row=i, column=0, sticky="e", pady=(6, 8), padx=(2,8)
        )
        var = tk.StringVar()
        entry = ttk.Entry(inner, textvariable=var)
        entry.grid(row=i, column=1, sticky="ew", pady=(6, 8))
        entry_vars[label_key] = (var)
        entry_widgets[label_key] = entry

    inner.columnconfigure(1, weight=1)

    # ---- radio groups ----
    radio_frame = ttk.Frame(inner)
    radio_frame.grid(row=len(field_info), column=0, columnspan=2, sticky="ew", pady=(10, 6))

    ttk.Label(radio_frame, text="Accommodation Type:").grid(row=0, column=0, sticky="w", padx=(0, 12))
    accom_type_var = tk.StringVar(value="all")
    for i, (txt, val) in enumerate([("Time","time"),("Attempts","attempts"),
                                    ("Split Test","split_test"),("Spell Checker","spell_check"),("All","all")], start=1):
        ttk.Radiobutton(radio_frame, text=txt, variable=accom_type_var, value=val).grid(row=i, column=0, sticky="w", pady=3)

    ttk.Label(radio_frame, text="Quiz Type:").grid(row=0, column=1, sticky="w", padx=(12, 12))
    quiz_type_var = tk.StringVar(value="both")
    for i, (txt, val) in enumerate([("Classic","classic"),("New","new"),("Both","both")], start=1):
        ttk.Radiobutton(radio_frame, text=txt, variable=quiz_type_var, value=val).grid(row=i, column=1, sticky="w", pady=3)

    ttk.Label(radio_frame, text="Date Filter:").grid(row=0, column=2, sticky="w", padx=(12, 0))
    date_filter_var = tk.StringVar(value="both")
    for i, (txt, val) in enumerate([("Future","future"),("Past","past"),("Both","both")], start=1):
        ttk.Radiobutton(radio_frame, text=txt, variable=date_filter_var, value=val).grid(row=i, column=2, sticky="w", pady=3)

    for c in range(3):
        radio_frame.columnconfigure(c, weight=1)

    clear_cache_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(inner, text="Clear all caches", variable=clear_cache_var).grid(
        row=len(field_info)+1, column=0, columnspan=2, sticky="w", pady=(10,4)
    )

    # ---- bottom bar ----
    bottom_bar = ttk.Frame(root, padding=10)
    bottom_bar.grid(row=1, column=0, sticky="ew")
    bottom_bar.columnconfigure(0, weight=1)

    generate_report(entry_vars)
    root.destroy()

    ttk.Button(bottom_bar, text="Generate Report", command=generate_report).grid(
        row=0, column=0, sticky="ew", padx=(120,120)
    )

    root.mainloop()