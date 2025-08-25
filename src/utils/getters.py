import api.api_endpoints as api_endpoints
import utils.cache_manager as cache_manager
import pandas as pd
from itertools import product
# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def get_term_df():
    term_cache = cache_manager.load_term_cache()
    data = {
        term_id: [term_data.get("name", ""), term_data.get("courses", [])]
        for term_id, term_data in term_cache.items()
    }
    return pd.DataFrame.from_dict(data, orient='index', columns=['Term Name', 'Course IDs'])

# course_cache = {course_id: {'code': ..., 'name': ..., 'term': ..., 'users': [...], 'quizzes': [...]}, ...}
def get_course_df():
    course_cache = cache_manager.load_course_cache()
    rows = []

    for course_id, course in course_cache.items():
        course_code = course.get("code", "")
        course_name = course.get("name", "")
        user_ids = course.get("users", []) or [None]
        quiz_ids = course.get("quizzes", []) or [None]

        for user_id, quiz_id in product(user_ids, quiz_ids):
            rows.append({
                "Course ID": course_id,
                "Course Code": course_code,
                "Course Name": course_name,
                "User ID": user_id,
                "Quiz ID": quiz_id
            })

    return pd.DataFrame(rows)

# user_cache = {user_id: {'name': ..., 'sis_id': ..., 'email': ..., 'courses': (...)}, ...}
def get_user_df():
    user_cache = cache_manager.load_user_cache()
    data = {
        user_id: [
            user.get("name", ""),
            user.get("sis_id", ""),
            user.get("email", ""),
            user.get("courses", [])
        ]
        for user_id, user in user_cache.items()
    }
    return pd.DataFrame.from_dict(data, orient='index', columns=['Sortable Name', 'SIS User ID', 'Email', 'Course IDs'])

# quiz_cache = {quiz_id: {'title': ..., 'type': ..., 'course_id': ...}, ...}
def get_quiz_df():
    quiz_cache = api_endpoints.quiz_cache
    data = {
        quiz_id: [
            quiz.get("title", ""),
            quiz.get("type", ""),
            quiz.get("course_id", "")
        ]
        for quiz_id, quiz in quiz_cache.items()
    }
    return pd.DataFrame.from_dict(data, orient='index', columns=['Title', 'Type', 'Course ID'])

# submission_cache = {submission_id: {...}, ...}
def get_submission_df():
    submission_cache = api_endpoints.submission_cache

    flattened_rows = []
    for user_id, courses in submission_cache.items():
        for course_id, quizzes in courses.items():
            for quiz_id, data in quizzes.items():
                flattened_rows.append({
                    "User ID": user_id,
                    "Course ID": course_id,
                    "Quiz ID": quiz_id,
                    "Extra Time": data.get("extra_time", 0),
                    "Extra Attempts": data.get("extra_attempts", 0),
                    "Date": data.get("date", "")
                })

    return pd.DataFrame(flattened_rows)
