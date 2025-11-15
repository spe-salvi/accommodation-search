# import os
# import time
# import logging

# # --- Pre-DB cleanup ---
# from db import database  # allows us to close any lingering connection safely

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# db_path = os.path.join(os.path.dirname(__file__), "db", "data.db")

# # Close any active SQLite connection before deleting
# database.close_connection()

# # Attempt deletion safely (OneDrive may briefly lock the file)
# if os.path.exists(db_path):
#     for attempt in range(3):
#         try:
#             os.remove(db_path)
#             print(f"✅ Deleted old database at: {db_path}")
#             break
#         except PermissionError:
#             print(f"⚠️ Database file locked (attempt {attempt + 1}/3). Retrying...")
#             time.sleep(0.5)
#     else:
#         raise RuntimeError(f"❌ Could not delete {db_path} after 3 attempts.")

# # --- Now it's safe to import anything that touches the DB ---
# from db.repositories.course_repo import CourseRepository
# from api.client import get_data


# def main():
#     start = time.perf_counter()

#     database.initialize_database()
#     course_repo = CourseRepository()

#     get_data('c_quizzes', course_id='11780', search_param='Decalogue')
#     get_data("n_quizzes", course_id='11780', search_param='Decalogue')
#     print(course_repo.get_quizzes_for_course('11780'))

#     elapsed = (time.perf_counter() - start) / 60
#     print(f"Elapsed time: {elapsed:.2f} minutes")


# if __name__ == "__main__":
#     main()























import os
import time
import logging


# --- Pre-DB cleanup ---
from db import database  # allows us to close any lingering connection safely

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_path = os.path.join(os.path.dirname(__file__), "db", "data.db")

# Close any active SQLite connection before deleting
database.close_connection()

# Attempt deletion safely (OneDrive may briefly lock the file)
if os.path.exists(db_path):
    for attempt in range(3):
        try:
            os.remove(db_path)
            print(f"✅ Deleted old database at: {db_path}")
            break
        except PermissionError:
            print(f"⚠️ Database file locked (attempt {attempt + 1}/3). Retrying...")
            time.sleep(0.5)
    else:
        raise RuntimeError(f"❌ Could not delete {db_path} after 3 attempts.")

import ui.get_user_input as get_user_input

def main():
    start = time.perf_counter()

    
    database.initialize_database()
    get_user_input.create_input_form()

    elapsed = (time.perf_counter() - start) / 60
    print(f"Elapsed time: {elapsed:.2f} minutes")

if __name__ == "__main__":
    main()
