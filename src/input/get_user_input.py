import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import logging
import utils.populate_cache as populate_cache
import utils.dataframe_utils as dataframe_utils
import input.process_input as process_input
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb

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

    # ---- placeholder helper ----
    def add_placeholder(entry, placeholder):
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        try:
            entry.config(foreground="gray")
        except Exception:
            pass  # theme might not support foreground on ttk.Entry

        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                try:
                    entry.config(foreground="black")
                except Exception:
                    pass

        def on_focus_out(e):
            if entry.get().strip() == "":
                entry.insert(0, placeholder)
                try:
                    entry.config(foreground="gray")
                except Exception:
                    pass

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

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

    def generate_report():
        def norm(v):
            return v.strip() if v and v.strip() != "" else None
        try:
            values = {}
            for k,var in entry_vars.items():
                v = var.get().strip()
                values[k] = None if v=="" else v

            # term_name = values.get("Term Name")
            # course_search = values.get("Course (ID / SIS ID / Code)")
            # student_search = values.get("Student (Name / SIS ID / Login)")
            # quiz_name = values.get("Quiz Name")
            # accom_type = accom_type_var.get()
            # quiz_type = quiz_type_var.get()
            # date_filter = date_filter_var.get()

            # term_id = '116'
            # course_id = '11780'#'10348'
            # quiz_id = None #'42742'#'40122'
            # user_id = None#'5961'
            # accom_type = 'time'
            # quiz_type ='both'#'classic'
            # date_filter = 'both'

            term_name = 'Fall 2025'
            course_search = 'MTH-156-OL-A'#'THE-115-OL-A'
            quiz_name = 'Exam #2'#'Decalogue'
            student_search = None#'2635745'
            accom_type = 'all'
            quiz_type = 'both'#'new'
            date_filter = 'both'
            clear_cache = True

            input_data = [term_name, course_search, quiz_name, student_search, accom_type, quiz_type, date_filter]
            logger.info(f"Collected payload: {input_data}")

            normalized_text_input = process_input.normalize_input(input_data)
            logger.info(f"Normalized input: {normalized_text_input}")

            if clear_cache:
                import utils.cache_manager as cache_manager
                logger.info("Clearing all caches")
                cache_manager.clear_all_caches()

            # if clear_cache_var.get():
            #     import utils.cache_manager as cache_manager
            #     logger.info("Clearing all caches")
            #     cache_manager.clear_all_caches()

            logger.info("Calling populate_cache with text input")
            populate_cache.call_populate(
                term_id=normalized_text_input[0], course_ids=normalized_text_input[1],
                quiz_ids=normalized_text_input[2], user_ids=normalized_text_input[3],
                accom_type=normalized_text_input[4]
            )

            logger.info("Building results DataFrame from text input")
            results_df = dataframe_utils.create_df(
                course_ids=normalized_text_input[1], quiz_ids=normalized_text_input[2],
                user_ids=normalized_text_input[3], accom_type=normalized_text_input[4],
                quiz_type=normalized_text_input[5], date_filter=normalized_text_input[6]
            )

            root.destroy()
            print(results_df)
        except Exception as e:
            logger.exception("Error in generate_report: %s", e)

    ttk.Button(bottom_bar, text="Generate Report", command=generate_report).grid(
        row=0, column=0, sticky="ew", padx=(120,120)
    )

    root.mainloop()