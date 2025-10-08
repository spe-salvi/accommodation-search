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

# def create_input_form():
#     root = tk.Tk()
#     root.title("Accommodations Search")
#     root.geometry("600x500")

#     style = ttkb.Style()
#     style.theme_use('pulse')

#     form_frame = ttkb.Frame(root, padding="20")
#     form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

#     ttk.Label(form_frame, text="Term ID:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
#     term_id_var = tk.StringVar()
#     ttk.Entry(form_frame, textvariable=term_id_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

#     ttk.Label(form_frame, text="Course ID:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
#     course_id_var = tk.StringVar()
#     ttk.Entry(form_frame, textvariable=course_id_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

#     ttk.Label(form_frame, text="Quiz ID:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
#     quiz_id_var = tk.StringVar()
#     ttk.Entry(form_frame, textvariable=quiz_id_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

#     ttk.Label(form_frame, text="User ID:").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
#     user_id_var = tk.StringVar()
#     ttk.Entry(form_frame, textvariable=user_id_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

#     radio_frame = ttk.Frame(form_frame)
#     radio_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

#     ttk.Label(radio_frame, text="Accommodation Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=(0, 10))
#     accom_type_var = tk.StringVar(value="all")
#     ttk.Radiobutton(radio_frame, text="Time", variable=accom_type_var, value="time").grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="Attempts", variable=accom_type_var, value="attempts").grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="Split Test", variable=accom_type_var, value="split_test").grid(row=3, column=0, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="Spell Checker", variable=accom_type_var, value="spell_check").grid(row=4, column=0, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="All", variable=accom_type_var, value="all").grid(row=5, column=0, sticky=tk.W)

#     ttk.Label(radio_frame, text="Quiz Type:").grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=(0, 10))
#     quiz_type_var = tk.StringVar(value="both")
#     ttk.Radiobutton(radio_frame, text="Classic", variable=quiz_type_var, value="classic").grid(row=1, column=1, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="New", variable=quiz_type_var, value="new").grid(row=2, column=1, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="Both", variable=quiz_type_var, value="both").grid(row=3, column=1, sticky=tk.W)

#     ttk.Label(radio_frame, text="Date Filter:").grid(row=0, column=2, sticky=tk.W, pady=(0, 10))
#     date_filter_var = tk.StringVar(value="both")
#     ttk.Radiobutton(radio_frame, text="Future", variable=date_filter_var, value="future").grid(row=1, column=2, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="Past", variable=date_filter_var, value="past").grid(row=2, column=2, sticky=tk.W, pady=(0, 8))
#     ttk.Radiobutton(radio_frame, text="Both", variable=date_filter_var, value="both").grid(row=3, column=2, sticky=tk.W)

#     clear_cache_var = tk.BooleanVar(value=False)
#     ttk.Checkbutton(form_frame, text="Clear all caches", variable=clear_cache_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

#     def generate_report():
#         try:
#             # term_id = term_id_var.get()
#             # course_id = course_id_var.get()
#             # quiz_id = quiz_id_var.get()
#             # user_id = user_id_var.get()
#             # accom_type = accom_type_var.get()
#             # quiz_type = quiz_type_var.get()
#             # date_filter = date_filter_var.get()
#             term_id = '115'
#             course_id = '12091'#'10348'
#             quiz_id = '179840'#'40122'
#             user_id = None#'5961'
#             accom_type = 'all'#'time'
#             quiz_type ='both'#'classic'
#             date_filter = 'both'
#             #essay question: course_id: 12091; assignment_id: 179840

#             term_id = None if not term_id else term_id
#             course_id = None if not course_id else course_id
#             quiz_id = None if not quiz_id else quiz_id
#             user_id = None if not user_id else user_id

#             input_data = [term_id, course_id, quiz_id, user_id, accom_type, quiz_type, date_filter]
#             logger.info(f'Original input_data: {input_data}')
#             cleaned_input = process_input(input_data)
#             logger.info(f'Cleaned input_data: {cleaned_input}')
#             if clear_cache_var.get():
#                 import utils.cache_manager as cache_manager
#                 logger.info("Clearing all caches")
#                 cache_manager.clear_all_caches()
#             logger.info("Calling populate_cache")
#             populate_cache.call_populate(term_ids=cleaned_input[0], course_ids=cleaned_input[1],
#                                          quiz_ids=cleaned_input[2], user_ids=cleaned_input[3],
#                                          accom_type=cleaned_input[4])
#             logger.info("Building results DataFrame")
#             logger.info(f'Len cleaned input: {len(cleaned_input)}')
#             logger.info("Creating results DataFrame")
#             results_df = dataframe_utils.create_df(course_ids=cleaned_input[1], quiz_ids=cleaned_input[2], 
#                                                    user_ids=cleaned_input[3], accom_type=cleaned_input[4],
#                                                    quiz_type=cleaned_input[5], date_filter=cleaned_input[6])
#             root.destroy()

#             logger.info("Generated results DataFrame")
#             print(results_df)
#             # current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
#             # report_file_name = f"./reports/accommodations_{current_time}.xlsx"
#             # results_df.to_excel(report_file_name, index=False)
#             # results_df.to_csv(report_file_name.replace('.xlsx', '.csv'), index=False)

#             return
#         except Exception as e:
#             logger.error(f"Error in generate_report: {e}")

#     ttk.Button(form_frame, text="Generate Report", command=generate_report).grid(row=5, column=0, columnspan=2, pady=(20, 0))

#     form_frame.columnconfigure(1, weight=1)
#     radio_frame.columnconfigure(0, weight=1)
#     radio_frame.columnconfigure(1, weight=1)
#     radio_frame.columnconfigure(2, weight=1)
#     root.columnconfigure(0, weight=1)
#     root.rowconfigure(0, weight=1)

#     root.mainloop()

def process_code_input(input_data):
    if type(input_data[0]) != list and input_data[0] is not None:
        terms = input_data[0]
    else: terms = None
    if type(input_data[1]) != list and input_data[1] is not None:
        course_ids = [input_data[1]]
    elif type(input_data[1]) == list:
        course_ids = input_data[1]
    else: course_ids = None
    if type(input_data[2]) != list and input_data[2] is not None:
        quiz_ids = [input_data[2]]
    elif type(input_data[2]) == list:
        quiz_ids = input_data[2]
    else: quiz_ids = None
    if type(input_data[3]) != list and input_data[3] is not None:
        user_ids = [input_data[3]]
    elif type(input_data[3]) == list:
        user_ids = input_data[3]
    else: user_ids = None
    if input_data[4] != None:
        accom_type = input_data[4]
    else: accom_type = None
    if input_data[5] != None:
        quiz_type = input_data[5]
    else: quiz_type = None
    if input_data[6] != None:
        date_filter = input_data[6]
    else: date_filter = None
    return (terms, course_ids, quiz_ids, user_ids, accom_type, quiz_type, date_filter)





##########################################################################################


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
        entry.config(foreground="gray")

        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground="black")

        def on_focus_out(e):
            if entry.get().strip() == "":
                entry.insert(0, placeholder)
                entry.config(foreground="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ---- fields ----
    field_info = [
        ("Term Name", "Fall 2025"),
        ("Course Name", "Philosophy of the Human Person"),
        ("Course SIS ID", "202510-PHL-113-A"),
        ("Course Code", "PHL-113-A"),
        ("Student Name", "John Smith"),
        ("Student SIS ID", "2109876"),
        ("Student Login ID", "jsmith"),
        ("Quiz Name", "Final Exam"),
    ]

    entry_vars = {}
    for i, (label_key, placeholder) in enumerate(field_info):
        ttk.Label(inner, text=f"{label_key}:").grid(row=i, column=0, sticky="w", pady=(6, 8), padx=(2,8))
        var = tk.StringVar()
        entry = ttk.Entry(inner, textvariable=var)
        entry.grid(row=i, column=1, sticky="ew", pady=(6, 8))
        add_placeholder(entry, placeholder)
        entry_vars[label_key] = (var, placeholder)

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
            for k,(var,ph) in entry_vars.items():
                v = var.get().strip()
                values[k] = None if v=="" or v==ph else v

            # Map UI names -> process_input positions
            # term_id   = values.get("Term Name")        # slot 0
            # course_id = values.get("Course SIS ID")    # slot 1
            # quiz_id   = values.get("Quiz Name")        # slot 2
            # user_id   = values.get("Student SIS ID")   # slot 3
            # accom_type= accom_type_var.get()           # slot 4
            # quiz_type = quiz_type_var.get()            # slot 5
            # date_filter = date_filter_var.get()        # slot 6
            # term_id = '116'
            # course_id = '12091'#'10348'
            # quiz_id = '179840'#'40122'
            # user_id = None#'5961'
            # accom_type = 'all'#'time'
            # quiz_type ='both'#'classic'
            # date_filter = 'both'

            term_id = 'Fall 2025'
            course_id = 'MTH-156-OL-A'
            quiz_id = 'Exam #2'
            user_id = None
            accom_type = 'all'
            quiz_type ='new'
            date_filter = 'both'

            input_data = [term_id, course_id, quiz_id, user_id, accom_type, quiz_type, date_filter]
            logger.info(f"Collected payload: {input_data}")

            cleaned_input = process_code_input(input_data)
            normalized_text_input = process_input.normalize_input(input_data)
            logger.info(f"Cleaned input: {cleaned_input}")
            logger.info(f"Normalized input: {normalized_text_input}")

            if clear_cache_var.get():
                import utils.cache_manager as cache_manager
                logger.info("Clearing all caches")
                cache_manager.clear_all_caches()

            # logger.info("Calling populate_cache with code input")
            # populate_cache.call_populate(
            #     term_ids=cleaned_input[0], course_ids=cleaned_input[1],
            #     quiz_ids=cleaned_input[2], user_ids=cleaned_input[3],
            #     accom_type=cleaned_input[4]
            # )

            # logger.info("Building results DataFrame from code input")
            # results_df = dataframe_utils.create_df(
            #     course_ids=cleaned_input[1], quiz_ids=cleaned_input[2],
            #     user_ids=cleaned_input[3], accom_type=cleaned_input[4],
            #     quiz_type=cleaned_input[5], date_filter=cleaned_input[6]
            # )

            logger.info("Calling populate_cache with text input")
            populate_cache.call_populate(
                term_ids=normalized_text_input[0], course_ids=normalized_text_input[1],
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
