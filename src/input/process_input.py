import logging
import utils.populate_cache as populate_cache
import utils.dataframe_utils as dataframe_utils
import config.config as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_term_name(term_name: str) -> int | None:
    term_lookup = {}
    for code, name in config.TERMS.items():
        lname = name.lower()
        if lname in term_lookup:
            logger.error(
                f"Duplicate term name detected: '{name}' "
                f"for codes {term_lookup[lname]} and {code}."
            )
        else:
            term_lookup[lname] = code
    return term_lookup.get(term_name.lower())

####
# Search term must be at least 3 characters
####

def process_course_name(course_name):
    #https://<canvas>/api/v1/accounts/:account_id/courses?search_term=<search value> \
    return

def process_course_sis(sis_course):
    #https://<canvas>/api/v1/accounts/:account_id/courses?search_term=<search value> \
    return

def process_course_code(code):
    #https://<canvas>/api/v1/accounts/:account_id/courses?search_term=<search value> \
    return

def process_student_name(student_name):
    #https://<canvas>/api/v1/accounts/self/users?search_term=<search value> \
    return

def process_student_sis(sis_student):
    #https://<canvas>/api/v1/accounts/self/users?search_term=<search value> \
    return

def process_student_login(student_login):
    #https://<canvas>/api/v1/accounts/self/users?search_term=<search value> \
    return

def process_quiz_name(quiz_name):
    #https://<canvas>/api/v1/courses/<course_id>/quizzes?search_term=<search value> \
    return