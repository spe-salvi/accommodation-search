from time import time
from config.config import *
import api.api_endpoints as api_endpoints
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_accommodated(course_id, quiz_id, user_id, accom_type):
    submission_cache = api_endpoints.submission_cache
    uid = str(user_id)

    # logger.info(f"[Cache Check] user_id={uid} ({type(user_id)}), Keys: {list(submission_cache.keys())}")

    quiz_info = get_cached_submission(uid, course_id, quiz_id)

    if quiz_info is None:
        logger.warning(f"No cached submission found for user {uid}, course {course_id}, quiz {quiz_id}")
        return (False, 'NA')
    
    extra_time = quiz_info['extra_time']
    attempts = quiz_info['extra_attempts']
    date_submitted = quiz_info['date']



    # logger.info(f"Quiz info: extra_time={extra_time}, attempts={attempts}, date_submitted={date_submitted}")

    if accom_type == 'time' and extra_time is not None:
        if extra_time > 0:
            return (True, date_submitted)

    elif accom_type == 'attempts' and attempts is not None:
        logger.info(f'Attempts: {attempts}')
        if attempts > 0:
            return (True, date_submitted)

    return (False, 'NA')

def get_cached_submission(user_id, course_id, quiz_id):
    """
    Safely retrieve cached submission data for a specific user, course, and quiz.
    Logs keys if not found for debugging.
    """
    submission_cache = api_endpoints.submission_cache
    # logger.info(f'[get_cached_submission] user_id={user_id}, course_id={course_id}, quiz_id={quiz_id}')
    # logger.info(f'Submission cache [get_cached_submission]:\n{submission_cache}')

    uid = str(user_id)
    cid = str(course_id)
    qid = str(quiz_id)
    if uid not in submission_cache:
        logger.info(f"User ID {uid} not in submission_cache. Keys: {list(submission_cache.keys())}")
        return None
    if cid not in submission_cache[uid]:
        logger.info(f"Course ID {cid} not in cache for user {uid}. Keys: {list(submission_cache[uid].keys())}")
        return None
    if qid not in submission_cache[uid][cid]:
        logger.info(f"Quiz ID {qid} not in cache for user {uid}, course {cid}.")
        return None

    return (
        submission_cache.get(uid, {})
                        .get(course_id, {})
                        .get(quiz_id)
    )