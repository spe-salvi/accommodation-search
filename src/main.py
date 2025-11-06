import ui.get_user_input as get_user_input
import time
from config import *
import logging
from db.database import initialize_database

logging.basicConfig(level=logging.INFO)

def main():
    start = time.perf_counter()
    initialize_database()
    get_user_input.create_input_form()

    end = time.perf_counter()
    seconds = end - start
    elapsed = seconds / 60

    print(f'Elapsed time: {elapsed:.2f} minutes')
if __name__ == "__main__":
    main()