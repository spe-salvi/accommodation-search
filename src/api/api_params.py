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
    #'users': endpoint_course_users,
    'c_quizzes': endpoint_quizzes,
    'n_quizzes': endpoint_quizzes,
    'c_quiz': endpoint_quiz,
    'n_quiz': endpoint_quiz,
    'c_quiz_submissions': endpoint_submissions,
    'n_quiz_submissions': endpoint_submissions,
    'n_quiz_items': endpoint_items,
    'search_urls': search_urls,
    'enrollments': endpoint_enrollments
    }

def get_data(search_type, term_id=None, course_id=None, quiz_id=None, user_id=None):

    logger.info(f"get_data called, search_type={search_type}")

    url_dict = get_urls(term_id, course_id, quiz_id, user_id)
    url = url_dict[search_type][0]
    params = url_dict[search_type][1]
    logger.info(f"[get_data] Fetching data from {url} with params {params}")
    data = retry_request.retry_get(url, params)
    if not data or 'message' in data:
        # logger.error(f"[get_data] Error fetching data: {data['message']}")
        return
    function = function_dict[search_type]
    try:
        if search_type == 'c_quiz':
            logger.info(f"Calling function {function.__name__}")
            function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id, acc_type='classic')
        elif search_type == 'n_quiz':
            logger.info(f"Calling function {function.__name__}")
            function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id, acc_type='new')
        elif search_type in ('c_quiz_submissions', 'n_quiz_submissions'):
            logger.info(f"Calling function {function.__name__}")
            function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id)
        else:
            logger.info(f"Calling function {function.__name__}")
            function(data, term_id=term_id, course_id=course_id, quiz_id=quiz_id, user_id=user_id)
        logger.info(f"[get_data] Finished processing for search_type={search_type}")
        return
    except Exception as e:
        logger.error(f"[get_data] Error in function {function.__name__}: {str(e)}")
        return

def get_urls(term_id=None, course_id=None, quiz_id=None, user_id=None, assignment_id=None):

    url_dict = {
        'term' : [f'{config.API_URL}/v1{config.FUS_ACCOUNT}/terms/{term_id}', {}],
        'courses' : [f'{config.API_URL}/v1{config.FUS_ACCOUNT}/courses', {"enrollment_term_id": term_id} if term_id else {}],
        'course' : [f'{config.API_URL}/v1/courses/{course_id}', {}],
        'course_users' : [f'{config.API_URL}/v1/courses/{course_id}/users', {}],
        #'users' : [f'{config.API_URL}/v1/users/{user_id}', {}],
        'c_quizzes' : [f'{config.API_URL}/v1/courses/{course_id}/quizzes', {}],
        'c_quiz' : [f'{config.API_URL}/v1/courses/{course_id}/quizzes/{quiz_id}', {}],
        'c_quiz_submissions': [f'{config.API_URL}/v1/courses/{course_id}/quizzes/{quiz_id}/submissions', {}],
        'n_quizzes' : [f'{config.API_URL}/quiz/v1/courses/{course_id}/quizzes', {}],
        'n_quiz' : [f'{config.API_URL}/quiz/v1/courses/{course_id}/quizzes/{quiz_id}', {}],
        'n_quiz_submissions': [f'{config.API_URL}/v1/courses/{course_id}/assignments/{quiz_id}/submissions', {}],
        'n_quiz_items': [f'{config.API_URL}/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items', {}],
        'enrollments' : [f'{config.API_URL}/v1/users/{user_id}/enrollments', {"enrollment_term_id": term_id} if term_id else {}],        
    }

    return url_dict

############################################################

def narrow_courses(term_id=None):
    logger.info('Narrowing courses called')
    cache_file = 'course_terms_cache.json'
    cache_expiry = timedelta(days=1)
    term_courses = {}

    # Try loading cache
    if os.path.exists(cache_file):
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - cache_time < cache_expiry:
            try:
                with open(cache_file, 'r') as f:
                    term_courses = json.load(f)
            except json.JSONDecodeError:
                logger.error("Cache corrupted. Fetching fresh data.")
                term_courses = get_data('courses',term_id = term_id)
                # Get term_courses from cache, function returns null
        else:
            logger.error("Cache expired. Fetching fresh data.")
            term_courses = get_data('courses',term_id = term_id)
            # Get term_courses from cache, function returns null
    else:
        logger.error("Cache missing. Fetching fresh data.")
        term_courses = get_data('courses',term_id = term_id)
        # Get term_courses from cache, function returns null

    # Check for missing term in cache
    if term_id:
        term_id = str(term_id)
        if term_id not in term_courses:
            logger.error(f"term_id {term_id} not found in cache; refreshing cache")
            term_courses = get_data('courses',term_id = term_id)
            # Get term_courses from cache, function returns null
            return term_courses.get(term_id, [])
        return term_courses.get(term_id, [])

    # If no term_id, return all courses across all terms
    all_courses = set()
    for courses in term_courses.values():
        all_courses.update(courses)
    return list(all_courses)