import api.api_endpoints as api_endpoints
import utils.cache_manager as cache_manager
import pandas as pd
from itertools import product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def fetch_term_df():
    logger.info("Fetching term cache (fetch_term_df).")
    term_cache = cache_manager.load_term_cache()
    logger.info(f"Loaded {len(term_cache)} terms from cache.")
    data = {
        term_id: [term_data.get("name", ""), term_data.get("courses", [])]
        for term_id, term_data in term_cache.items()
    }
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Term Name', 'Course ID Term'])
    df = df.explode("Course ID Term", ignore_index=True)
    return df

# course_cache = {course_id: {'code': ..., 'name': ..., 'term': ..., 'users': [...], 'quizzes': [...]}, ...}
def fetch_course_df():
    logger.info("Fetching course cache (fetch_course_df).")
    course_cache = cache_manager.load_course_cache()
    logger.info(f"Loaded {len(course_cache)} courses from cache.")
    rows = []

    for course_id, course in course_cache.items():
        # logger.info(f"Processing course ID: {course_id}")
        course_code = course.get("code", "")
        course_name = course.get("name", "")
        user_ids = course.get("users", []) or [None]
        quiz_ids = course.get("quizzes", []) or [None]

        for user_id, quiz_id in product(user_ids, quiz_ids):
            logger.debug(f"Adding row for Course ID: {course_id}, User ID: {user_id}, Quiz ID: {quiz_id}")
            rows.append({
                "Course ID Course": course_id,
                "Course Code": course_code,
                "Course Name": course_name,
                "User ID Course": user_id,
                "Quiz ID Course": quiz_id
            })

    df = pd.DataFrame(rows).drop_duplicates()
    # normalize keys
    logging.info(f'{df}')
    df["Course ID Course"] = df["Course ID Course"].astype("string").str.strip()
    df["User ID Course"]   = df["User ID Course"].astype("string").str.strip()
    df["Quiz ID Course"]   = df["Quiz ID Course"].astype("string").str.strip()
    return df

# user_cache = {user_id: {'name': ..., 'sis_id': ..., 'email': ..., 'courses': (...)}, ...}
def fetch_user_df():
    logger.info("Fetching user cache (fetch_user_df).")
    user_cache = cache_manager.load_user_cache()

    data = {
        user_id: [
            user.get("sortable_name", ""),
            user.get("sis_id", ""),
            user.get("email", ""),
            user.get("courses", [])
        ]
        for user_id, user in user_cache.items()
    }
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Sortable Name', 'SIS User ID', 'Email', 'Course ID User'])
    df.index.name = "User ID"
    df = df.reset_index()  # bring User ID into a column
    # ensure list -> explode
    df["Course ID User"] = df["Course ID User"].apply(lambda x: x if isinstance(x, list) else [])
    df = df.explode("Course ID User", ignore_index=True)
    # normalize keys
    df["User ID"]        = df["User ID"].astype("string").str.strip()
    df["Course ID User"] = df["Course ID User"].astype("string").str.strip()
    return df

# quiz_cache = {quiz_id: {'title': ..., 'type': ..., 'course_id': ...}, ...}
def fetch_quiz_df():
    logger.info("Fetching quiz cache (fetch_quiz_df).")
    quiz_cache = api_endpoints.quiz_cache
    data = {
        quiz_id: [
            quiz.get("title", ""),
            quiz.get("type", ""),
            quiz.get("course_id", "")
        ]
        for quiz_id, quiz in quiz_cache.items()
    }
    df = pd.DataFrame.from_dict(
        data,
        orient="index",
        columns=["Title", "Type", "Course ID Quiz"]
    )
    df.index.name = "Quiz ID"
    df = df.reset_index()  # bring Quiz ID into a column
    # normalize key types
    df["Quiz ID"]        = df["Quiz ID"].astype("string").str.strip()
    df["Course ID Quiz"] = df["Course ID Quiz"].astype("string").str.strip()
    return df

# submission_cache = {submission_id: {...}, ...}
def fetch_submission_df():
    logger.info("Fetching submission cache (fetch_submission_df).")
    submission_cache = api_endpoints.submission_cache
    logger.info(f"Loaded submission cache with {len(submission_cache)} users.")

    rows = []
    for user_id, courses in submission_cache.items():
        for course_id, quizzes in courses.items():
            for quiz_id, data in quizzes.items():
                rows.append({
                    "User ID Sub": user_id,
                    "Course ID Sub": course_id,
                    "Quiz ID Sub": quiz_id,
                    "Extra Time": data.get("extra_time", 0),
                    "Extra Attempts": data.get("extra_attempts", 0),
                    "Date": data.get("date", "")
                })

    df = pd.DataFrame(rows)
    # normalize keys
    for c in ["User ID Sub", "Course ID Sub", "Quiz ID Sub"]:
        df[c] = df[c].astype("string").str.strip()
    return df
