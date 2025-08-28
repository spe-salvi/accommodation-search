import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import logging
import utils.resolvers as resolvers
import utils.dataframe_utils as dataframe_utils
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_input_form():
    root = tk.Tk()
    root.title("Accommodations Search")
    root.geometry("600x500")

    style = ttkb.Style()
    style.theme_use('pulse')

    form_frame = ttkb.Frame(root, padding="20")
    form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(form_frame, text="Term ID:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
    term_id_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=term_id_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

    ttk.Label(form_frame, text="Course ID:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
    course_id_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=course_id_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

    ttk.Label(form_frame, text="Quiz ID:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
    quiz_id_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=quiz_id_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

    ttk.Label(form_frame, text="User ID:").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
    user_id_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=user_id_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

    radio_frame = ttk.Frame(form_frame)
    radio_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

    ttk.Label(radio_frame, text="Accommodation Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=(0, 10))
    accom_type_var = tk.StringVar(value="both")
    ttk.Radiobutton(radio_frame, text="Time", variable=accom_type_var, value="time").grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
    ttk.Radiobutton(radio_frame, text="Attempts", variable=accom_type_var, value="attempts").grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
    ttk.Radiobutton(radio_frame, text="Both", variable=accom_type_var, value="both").grid(row=3, column=0, sticky=tk.W)

    ttk.Label(radio_frame, text="Quiz Type:").grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=(0, 10))
    quiz_type_var = tk.StringVar(value="both")
    ttk.Radiobutton(radio_frame, text="Classic", variable=quiz_type_var, value="classic").grid(row=1, column=1, sticky=tk.W, pady=(0, 8))
    ttk.Radiobutton(radio_frame, text="New", variable=quiz_type_var, value="new").grid(row=2, column=1, sticky=tk.W, pady=(0, 8))
    ttk.Radiobutton(radio_frame, text="Both", variable=quiz_type_var, value="both").grid(row=3, column=1, sticky=tk.W)

    ttk.Label(radio_frame, text="Date Filter:").grid(row=0, column=2, sticky=tk.W, pady=(0, 10))
    date_filter_var = tk.StringVar(value="both")
    ttk.Radiobutton(radio_frame, text="Future", variable=date_filter_var, value="future").grid(row=1, column=2, sticky=tk.W, pady=(0, 8))
    ttk.Radiobutton(radio_frame, text="Past", variable=date_filter_var, value="past").grid(row=2, column=2, sticky=tk.W, pady=(0, 8))
    ttk.Radiobutton(radio_frame, text="Both", variable=date_filter_var, value="both").grid(row=3, column=2, sticky=tk.W)

    clear_cache_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(form_frame, text="Clear all caches", variable=clear_cache_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

    def generate_report():
        try:
            # term_id = term_id_var.get()
            # course_id = course_id_var.get()
            # quiz_id = quiz_id_var.get()
            # user_id = user_id_var.get()
            # accom_type = accom_type_var.get()
            # quiz_type = quiz_type_var.get()
            # date_filter = date_filter_var.get()
            term_id = '115'
            course_id = '10348'
            quiz_id = '40122'
            user_id = '5961'
            accom_type = 'time'
            quiz_type ='classic'
            date_filter = 'both'

            term_id = None if not term_id else term_id
            course_id = None if not course_id else course_id
            quiz_id = None if not quiz_id else quiz_id
            user_id = None if not user_id else user_id


            input_data = [term_id, course_id, quiz_id, user_id, accom_type, quiz_type, date_filter]
            logger.info(f'Original input_data: {input_data}')
            cleaned_input = process_input(input_data)
            logger.info(f'Cleaned input_data: {cleaned_input}')
            if clear_cache_var.get():
                import utils.cache_manager as cache_manager
                logger.info("Clearing all caches")
                cache_manager.clear_all_caches()
            logger.info("Calling resolve_search_params")
            resolvers.resolve_search_params(cleaned_input)
            logger.info("Creating results DataFrame")
            results_df = dataframe_utils.create_df()
            root.destroy()

            logger.info("Generated results DataFrame")
            print(results_df)
            # current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            # report_file_name = f"./reports/accommodations_{current_time}.xlsx"
            # results_df.to_excel(report_file_name, index=False)
            # results_df.to_csv(report_file_name.replace('.xlsx', '.csv'), index=False)

            return
        except Exception as e:
            logger.error(f"Error in generate_report: {e}")

    ttk.Button(form_frame, text="Generate Report", command=generate_report).grid(row=5, column=0, columnspan=2, pady=(20, 0))

    form_frame.columnconfigure(1, weight=1)
    radio_frame.columnconfigure(0, weight=1)
    radio_frame.columnconfigure(1, weight=1)
    radio_frame.columnconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()

def process_input(input_data):

    if type(input_data[0]) != list and input_data[0] is not None:
        terms = [input_data[0]]
    elif type(input_data[0]) == list:
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
    if input_data[6] != None:
        date_filter = input_data[6]
    else: date_filter = None
    return (terms, course_ids, quiz_ids, user_ids, accom_type, date_filter)