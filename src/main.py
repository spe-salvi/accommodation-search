import os
import time

# --- delete before any DB import ---
db_path = os.path.join(os.path.dirname(__file__), "db", "data.db")
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted old database at: {db_path}")

# now it's safe to import anything that touches the DB
from db import database
import ui.get_user_input as get_user_input

def main():
    start = time.perf_counter()

    database.initialize_database()
    get_user_input.create_input_form()

    elapsed = (time.perf_counter() - start) / 60
    print(f"Elapsed time: {elapsed:.2f} minutes")

if __name__ == "__main__":
    main()
