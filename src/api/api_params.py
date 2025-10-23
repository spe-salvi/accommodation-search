import config.config as config
from api.api_endpoints import *
import utils.retry_request as retry_request
import logging
import os, json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

function_dict = {
    'term': endpoint_term,
    'courses': endpoint_courses,
    'course': endpoint_course,
    'course_users': endpoint_course_users,
    'users': endpoint_course_users,
    'c_quizzes': endpoint_quizzes,
    'n_quizzes': endpoint_quizzes,
    'c_quiz': endpoint_quiz,
    'n_quiz': endpoint_quiz,
    'c_quiz_submissions': endpoint_submissions,
    'n_quiz_submissions': endpoint_submissions,
    'n_quiz_items': endpoint_items,
    'enrollments': endpoint_enrollments
    }

def get_data(search_type, **kwargs):

    term_id = kwargs.get("term_id",)
    course_id = kwargs.get("course_id",)
    quiz_id = kwargs.get("quiz_id",)
    user_id = kwargs.get("user_id",)
    search_param = kwargs.get("search_param",)

    # logger.info(f"get_data called, search_type={search_type}")

    url_dict = get_urls(term_id, course_id, quiz_id, user_id, search_param)
    url = url_dict[search_type][0]
    params = url_dict[search_type][1]
    # logger.info(f"[get_data] Fetching data from {url} with params {params}")
    data = retry_request.retry_get(url, params)
    if not data or 'message' in data:
        # logger.error(f"[get_data] Error fetching data: {data['message']}")
        return
    function = function_dict[search_type]
    try:
        if search_type == 'c_quiz':
            # logger.info(f"Calling function {function.__name__}")
            ret_vals = function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id, acc_type='classic')
        elif search_type == 'n_quiz':
            # logger.info(f"Calling function {function.__name__}")
            ret_vals = function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id, acc_type='new')
        else:
            # logger.info(f"Calling function {function.__name__}")
            ret_vals = function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id)
        # logger.info(f"[get_data] Finished processing for search_type={search_type}")
        return ret_vals
    except Exception as e:
        logger.error(f"[get_data] Error in function {function.__name__}: {str(e)}")
        return
    
def get_urls(term_id=None, course_id=None, quiz_id=None, user_id=None, search_param=None):

    url_dict = {
        'term' : [f'{config.API_URL}/v1{config.FUS_ACCOUNT}/terms/{term_id}', {}],
        'courses': [f'{config.API_URL}/v1{config.FUS_ACCOUNT}/courses', {**({"search_term": search_param} if search_param else {}), **({"enrollment_term_id": term_id} if term_id else {})}],
        'course' : [f'{config.API_URL}/v1/courses/{course_id}', {}],
        'course_users' : [f'{config.API_URL}/v1/courses/{course_id}/users', {}],
        'users' : [f'{config.API_URL}/v1{config.FUS_ACCOUNT}/users', {"search_term": search_param} if search_param else {}],
        'c_quizzes' : [f'{config.API_URL}/v1/courses/{course_id}/quizzes', {"search_term": search_param} if search_param else {}],
        'c_quiz' : [f'{config.API_URL}/v1/courses/{course_id}/quizzes/{quiz_id}', {}],
        'c_quiz_submissions': [f'{config.API_URL}/v1/courses/{course_id}/quizzes/{quiz_id}/submissions', {}],
        'n_quizzes' : [f'{config.API_URL}/quiz/v1/courses/{course_id}/quizzes', {"search_term": search_param} if search_param else {}],
        'n_quiz' : [f'{config.API_URL}/quiz/v1/courses/{course_id}/quizzes/{quiz_id}', {}],
        'n_quiz_submissions': [f'{config.API_URL}/v1/courses/{course_id}/assignments/{quiz_id}/submissions', {}],
        'n_quiz_items': [f'{config.API_URL}/quiz/v1/courses/{course_id}/quizzes/{quiz_id}/items', {}],
        'enrollments' : [f'{config.API_URL}/v1/users/{user_id}/enrollments', {"enrollment_term_id": term_id} if term_id else {}],        
    }

    return url_dict