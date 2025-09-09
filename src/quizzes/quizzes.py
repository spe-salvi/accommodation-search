from config.config import *
import api.api_endpoints as api_endpoints
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_accommodated(course_id, quiz_id, user_id, accom_type):
    submission_cache = api_endpoints.submission_cache
    uid = str(user_id)

    logging.debug(f"[Cache Check] user_id={uid} ({type(user_id)}), Keys: {list(submission_cache.keys())}")

    quiz_info = get_cached_submission(uid, course_id, quiz_id)

    time = quiz_info['extra_time']
    attempts = quiz_info['extra_attempts']
    date_submitted = quiz_info['date']

    if accom_type == 'time':
        quiz_cache = api_endpoints.quiz_cache
        time_limit = quiz_cache[quiz_id]['time_limit']

        if time == (time_limit * 2) and time > 0:
            return (True, date_submitted)

    elif accom_type == 'attempts':
        print(f'Attempts: {attempts}')
        if attempts > 0:
            return (True, date_submitted)

    return (False, 'NA')

def get_cached_submission(user_id, course_id, quiz_id):
    """
    Safely retrieve cached submission data for a specific user, course, and quiz.
    Logs keys if not found for debugging.
    """
    submission_cache = api_endpoints.submission_cache

    uid = str(user_id)
    if uid not in submission_cache:
        logging.debug(f"User ID {uid} not in submission_cache. Keys: {list(submission_cache.keys())}")
        return None
    if course_id not in submission_cache[uid]:
        logging.debug(f"Course ID {course_id} not in cache for user {uid}. Keys: {list(submission_cache[uid].keys())}")
        return None
    if quiz_id not in submission_cache[uid][course_id]:
        logging.debug(f"Quiz ID {quiz_id} not in cache for user {uid}, course {course_id}.")
        return None

    uid = str(user_id)
    return (
        submission_cache.get(uid, {})
                        .get(course_id, {})
                        .get(quiz_id)
    )