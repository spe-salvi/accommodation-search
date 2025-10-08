import api.api_endpoints as api_endpoints
import utils.cache_manager as cache_manager
import pandas as pd
from itertools import product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def fetch_term_df():
    # logger.info("Fetching term cache (fetch_term_df).")
    term_cache = cache_manager.load_term_cache()
    # logger.info(f"Loaded {len(term_cache)} terms from cache.")
    data = {
        term_id: [term_data.get("name", ""), term_data.get("courses", [])]
        for term_id, term_data in term_cache.items()
    }
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Term Name', 'Course ID Term'])
    df = df.explode("Course ID Term", ignore_index=True)
    return df

# course_cache = {course_id: {'code': ..., 'name': ..., 'term': ..., 'users': [...], 'quizzes': [...]}, ...}
def fetch_course_df():
    course_cache = cache_manager.load_course_cache()
    quiz_cache   = api_endpoints.quiz_cache  # load global quiz cache
    rows = []

    for course_id, course in course_cache.items():
        course_code = course.get("code", "")
        course_name = course.get("name", "")
        user_ids = course.get("users", []) or [None]

        # Only include quizzes that exist in the global quiz cache
        course_quizzes = course.get("quizzes", []) or []
        quiz_ids = [q for q in course_quizzes if q in quiz_cache]

        for user_id, quiz_id in product(user_ids, quiz_ids):
            logger.info(f"Adding row for Course ID Course: {course_id}, User ID: {user_id}, Quiz ID: {quiz_id}")
            rows.append({
                "Course ID Course": course_id,
                "Course Code": course_code,
                "Course Name": course_name,
                "User ID Course": user_id,
                "Quiz ID Course": quiz_id
            })

    if not rows:
        logger.warning(f"No rows found for courses. Returning empty DataFrame with expected columns.")
        return pd.DataFrame(columns=[
            "Course ID Course",
            "Course Code",
            "Course Name",
            "User ID Course",
            "Quiz ID Course"
        ])

    df = pd.DataFrame(rows).drop_duplicates()
    df["Course ID Course"] = df["Course ID Course"].astype("string").str.strip()
    df["User ID Course"]   = df["User ID Course"].astype("string").str.strip()
    df["Quiz ID Course"]   = df["Quiz ID Course"].astype("string").str.strip()
    return df

# user_cache = {user_id: {'name': ..., 'sis_id': ..., 'email': ..., 'courses': (...)}, ...}
def fetch_user_df():
    # logger.info("Fetching user cache (fetch_user_df).")
    user_cache = cache_manager.load_user_cache()
    # logger.info(f'Loaded {len(user_cache)} users from cache.')

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
    # logger.info("Fetching quiz cache (fetch_quiz_df).")
    quiz_cache = api_endpoints.quiz_cache
    logger.info(f'Loaded {len(quiz_cache)} quizzes from cache.')
    
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

def fetch_submission_df():
    # logger.info("Fetching submission cache (fetch_submission_df).")
    submission_cache = api_endpoints.submission_cache or {}
    # logger.info(f"Loaded submission cache with {len(submission_cache)} users.")
    # logger.info(f"Submission cache: {submission_cache}")

    rows = []
    for user_id, courses in submission_cache.items():
        if not isinstance(courses, dict):
            logger.warning(f"User {user_id} has non-dict courses: {courses}")
            continue

        for course_id, quizzes in courses.items():
            if not isinstance(quizzes, dict):
                logger.warning(f" Course {course_id} has non-dict quizzes: {quizzes}")
                continue

            for quiz_id, data in quizzes.items():
                if not isinstance(data, dict):
                    logger.warning(f"  Quiz {quiz_id} has non-dict data: {data}")
                    continue

                rows.append({
                    "User ID Sub": user_id,
                    "Course ID Sub": course_id,
                    "Quiz ID Sub": quiz_id,
                    "Extra Time": data.get("extra_time", 0),
                    "Extra Attempts": data.get("extra_attempts", 0),
                    "Date": data.get("date", "")
                })

    df = pd.DataFrame(rows, columns=[
        "User ID Sub", "Course ID Sub", "Quiz ID Sub",
        "Extra Time", "Extra Attempts", "Date"
    ])

    if not df.empty:
        df["Course ID Sub"] = df["Course ID Sub"].astype(str)
        df["Quiz ID Sub"]   = df["Quiz ID Sub"].astype(str)
        df["User ID Sub"]   = df["User ID Sub"].astype(str)
    # logger.info(f'Final submission df before normalization:\n{df}')
    return df

def fetch_question_df():
    # logger.info("Fetching question cache (fetch_question_df).")
    question_cache = cache_manager.load_question_cache()

    rows = [
        {
            "Course ID Ques": course_id,
            "Quiz ID Ques": quiz_id,
            "Item ID Ques": item_id,
            "Spell Check": data.get("spell_check", False)
        }
        for course_id, quizzes in question_cache.items()
        if isinstance(quizzes, dict)
        for quiz_id, items in quizzes.items()
        if isinstance(items, dict)
        for item_id, data in items.items()
        if isinstance(data, dict)
    ]

    df = pd.DataFrame(rows)
    if df.empty:
        logger.warning("fetch_question_df: No valid question data found.")
        return df

    # Cast columns dynamically
    for col in ["Course ID Ques", "Quiz ID Ques", "Item ID Ques", "Spell Check"]:
        df[col] = df[col].astype(str)

    return df

def fetch_quiz_title(course_id, quiz_id):
    """
    Returns the title of a quiz given course_id and quiz_id.
    Uses cached quiz DataFrame.
    """
    quiz_df = fetch_quiz_df()
    row = quiz_df[
        (quiz_df['Course ID Quiz'] == str(course_id)) & 
        (quiz_df['Quiz ID'] == str(quiz_id))
    ]
    if not row.empty:
        return row.iloc[0]['Title']
    return None

def fetch_user_sortable_name(user_id):
    """
    Returns the sortable name of a user given user_id.
    Uses cached user DataFrame.
    """
    user_df = fetch_user_df()
    row = user_df[user_df['User ID'] == str(user_id)]
    if not row.empty:
        return row.iloc[0]['Sortable Name']
    return None