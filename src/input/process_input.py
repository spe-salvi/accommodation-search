import logging
import utils.populate_cache as populate_cache
import utils.dataframe_utils as dataframe_utils
from utils.retry_request import retry_get
import config.config as config
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# input_data = [term_id, course_id, quiz_id, user_id, accom_type, quiz_type, date_filter]
def normalize_input(input_data: list) -> list:
    normalized = []
    term_name = input_data[0]
    term_code = get_term_code(term_name)
    normalized.append(term_code)

    course_search_term = input_data[1]
    course_id = process_course_search(course_search_term)
    normalized.append(course_id)

    quiz_name = input_data[2]
    quiz_id = process_quiz_name(quiz_name)
    normalized.append(quiz_id)

    user_name = input_data[3]
    user_id = process_student_name(user_name)
    normalized.append(user_id)

    normalized.append(input_data[4:])
# Normalize dictionary into a helper lookup
def build_term_lookup():
    lookup = {}
    for code, full in config.TERMS.items():
        season, year = full.split()
        year = int(year)

        # Accept full year (2024) and short year (24)
        year_variants = {str(year), str(year % 100)}

        # Accept full season and first two letters
        season_variants = {season.lower(), season[:2].lower()}

        for s in season_variants:
            for y in year_variants:
                lookup[f"{s} {y}"] = code
    return lookup

def get_term_code(user_input: str) -> int | None:
    norm = user_input.strip().lower()
    # Squash multiple spaces
    norm = re.sub(r"\s+", " ", norm)
    term_lookup = build_term_lookup()
    return term_lookup.get(norm)


####
# Search term must be at least 3 characters
####

def process_course_search(course_search_term):
    #https://<canvas>/api/v1/accounts/:account_id/courses?search_term=<search value> \
    url = f"{config.API_URL}/v1{config.FUS_ACCOUNT}/courses?search_term={course_search_term}"
    data = retry_get(url, {})

    course_ids = [course.get('id', '') for course in data]
    return course_ids

def process_student_name(student_name):
    #https://<canvas>/api/v1/accounts/self/users?search_term=<search value> \
    return

def process_student_sis(sis_student):
    #https://<canvas>/api/v1/accounts/self/users?search_term=<search value> \
    return

def process_student_login(student_login):
    #https://<canvas>/api/v1/accounts/self/users?search_term=<search value> \
    return

def process_quiz_search(course_ids, quiz_name):
    #https://<canvas>/api/v1/courses/<course_id>/quizzes?search_term=<search value> \
    return