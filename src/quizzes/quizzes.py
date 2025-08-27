from config.config import *
from api.api_params import get_data
import api.api_endpoints as api_endpoints
from api.api_endpoints import get_cached_submission
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_quiz_time(course_id, quiz_id):
    quiz_cache = api_endpoints.quiz_cache
    print(f'Cache: {quiz_cache}')
    print(f'Quiz ID: {quiz_id}')
    if quiz_cache:
        print(f'Cache: {quiz_cache}')
        print(f'Quiz ID: {quiz_id}')
        if quiz_id not in quiz_cache:
            print('here')
            get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)
    else:
        print('here 2')
        # print(course_id, quiz_id)
        get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)


def is_accommodated(course_id, quiz_id, user_id, accom_type):
    submission_cache = api_endpoints.submission_cache
    uid = str(user_id)

    logging.debug(f"[Cache Check] user_id={uid} ({type(user_id)}), Keys: {list(submission_cache.keys())}")

    quiz_info = get_cached_submission(uid, course_id, quiz_id)

    if not quiz_info:
        get_data('c_quiz_submissions', course_id=course_id, quiz_id=quiz_id)
        quiz_info = get_cached_submission(uid, course_id, quiz_id)

    if not quiz_info:
        get_data('n_quiz_submissions', course_id=course_id, quiz_id=quiz_id)
        quiz_info = get_cached_submission(uid, course_id, quiz_id)

    if not quiz_info:
        return (False, 'NA')

    # Pull values from the cache
    time = quiz_info['extra_time']
    attempts = quiz_info['extra_attempts']
    date_submitted = quiz_info['date']

    # Check accommodation
    if accom_type == 'time':
        quiz_cache = api_endpoints.quiz_cache
        if quiz_id not in quiz_cache:
            get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)
            quiz_cache = api_endpoints.quiz_cache
            if quiz_id not in quiz_cache:
                return (False, 'NA')
        time_limit = quiz_cache[quiz_id]['time_limit']

        if time == (time_limit * 2) and time > 0:
            return (True, date_submitted)

    elif accom_type == 'attempts':
        print(f'Attempts: {attempts}')
        if attempts > 0:
            return (True, date_submitted)

    return (False, 'NA')
