import input.get_user_input as get_user_input
import time
from config.config import *

def main():
    start = time.perf_counter()
    
    # get_user_input.create_input_form()
    get_user_input.create_input_form_merged()

    end = time.perf_counter()
    seconds = end - start
    elapsed = seconds / 60

    print(f'Elapsed time: {elapsed:.2f} minutes')
if __name__ == "__main__":
    main()