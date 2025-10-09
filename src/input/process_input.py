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
    normalized = ()
    term_name = input_data[0]
    term_code = get_term_code(term_name)
    normalized += (term_code,)

    course_search_term = input_data[1]
    course_ids = process_course_search(term_code, course_search_term)
    normalized += (course_ids,)

    quiz_name = input_data[2]
    quiz_type = input_data[5]
    quiz_ids = process_quiz_search(course_ids, quiz_name, quiz_type)
    normalized += (quiz_ids,)

    student_search_term = input_data[3]
    user_ids = process_student_search(student_search_term)
    normalized += (user_ids,)

    normalized += (input_data[4], input_data[5], input_data[6])
    return normalized
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
    return str(term_lookup.get(norm))


####
# Search term must be at least 3 characters
####

def process_course_search(term_code, course_search_term):
    if not course_search_term:
        return None

    url = f"{config.API_URL}/v1{config.FUS_ACCOUNT}/courses"
    params = {'search_term': course_search_term}
    if term_code:
        params['enrollment_term_id'] = term_code

    data = retry_get(url, params)
    return [str(course.get('id')) for course in data if 'id' in course]


def process_student_search(student_search_term):
    if student_search_term is None:
        return None
    url = f"{config.API_URL}/v1{config.FUS_ACCOUNT}/users?search_term={student_search_term}"
    data = retry_get(url, {})
    user_ids = [str(user.get('id')) for user in data if 'id' in user]
    # logger.info(f"Found user IDs: {user_ids}")
    return user_ids


def process_quiz_search(course_ids, quiz_name, quiz_type):
    if not quiz_name or not course_ids:
        return None

    quiz_ids = []
    quiz_name_norm = quiz_name.strip().lower()

    for course_id in course_ids:
        urls = []
        if quiz_type in ('classic', 'both'):
            urls.append(f"{config.API_URL}/v1/courses/{course_id}/quizzes?search_term={quiz_name}")
        if quiz_type in ('new', 'both'):
            urls.append(f"{config.API_URL}/v1/courses/{course_id}/assignments?search_term={quiz_name}")

        for url in urls:
            data = retry_get(url, {})
            logger.info(data)
            logger.info(f"Found {len(data)} potential matches for {quiz_name!r} in course {course_id}")

            for quiz in data:
                name = quiz.get("name", "").strip().lower()
                submission_types = quiz.get("submission_types", [])

                is_new_quiz = "assignments" in url
                name_match = quiz_name_norm in name

                # Classic: just name match
                # New: must also be an external tool (LTI quiz)
                if name_match and (not is_new_quiz or ("external_tool" in submission_types or "online_quiz" in submission_types)):
                    quiz_ids.append(str(quiz.get("id")))

    # quiz_ids = list({qid for qid in quiz_ids if qid})  # dedupe + remove None
    # logger.info(f"Final filtered quiz IDs: {quiz_ids}")
    return quiz_ids