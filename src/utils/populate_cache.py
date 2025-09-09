from utils.cache_manager import *
from api.api_params import get_data
import logging
import utils.cache_manager as cache_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_populate(term_ids=None, course_ids=None, quiz_ids=None, user_ids=None):
    logger.info("Starting cache population process")
    
    populate_term_cache(term_ids)

    # Normalize inputs
    if not course_ids and not user_ids:
        course_ids = get_courses_from_terms(term_ids)

    if not course_ids and user_ids:
        # Case: Users but no courses
        course_ids = get_courses_from_users(user_ids)

    # Standard pipeline
    populate_course_cache(course_ids)
    populate_user_cache(term_ids, course_ids, user_ids)
    populate_quiz_cache(course_ids, quiz_ids)
    populate_submissions_cache(course_ids, quiz_ids)

def populate_term_cache(term_ids, course_ids=None):
    logger.info("Populating term cache")

    if term_ids:
        for tid in term_ids:
            get_data('term', term_id=tid)
            if not course_ids:
                get_data('courses', term_id=tid)
    else:
        logger.error("No term IDs provided for populating term cache")


def populate_course_cache(course_ids):
    logger.info("Populating course cache")

    if course_ids:
        for cid in course_ids:
            get_data('course', course_id=cid)
            get_data('c_quizzes', course_id=cid)
            get_data('n_quizzes', course_id=cid)
            get_data('course_users', course_id=cid)

    course_cache = cache_manager.load_course_cache()
    logger.info(f"Loaded {len(course_cache)} courses from cache.")

def populate_user_cache(term_ids, course_ids, user_ids):
    logger.info("Populating user cache")
    term_ids = term_ids if term_ids else None #all_term_ids
    course_ids = course_ids if course_ids else None #all_course_ids
    user_ids = user_ids if user_ids else None #all_user_ids

    for cid in course_ids:
        get_data('course_users', course_id=cid)


    for term_id in term_ids:
        for user_id in user_ids:
            get_data('enrollments', term_id=term_id, user_id=user_id)


def populate_quiz_cache(course_ids, quiz_ids):
    logger.info("Populating quiz cache")
    course_ids = course_ids if course_ids else None #all_course_ids
    quiz_ids = quiz_ids if quiz_ids else None #all_quiz_ids

    for course_id in course_ids:
        for quiz_id in quiz_ids:
            get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)
            get_data('n_quiz', course_id=course_id, quiz_id=quiz_id)
    #search_urls

def populate_submissions_cache(course_ids, quiz_ids):
    logger.info("Populating submissions cache")
    course_ids = course_ids if course_ids else None #all_course_ids
    quiz_ids = quiz_ids if quiz_ids else None #all_quiz_ids

    for course_id in course_ids:
        for quiz_id in quiz_ids:
            get_data('c_quiz_submissions', course_id=course_id, quiz_id=quiz_id)
            get_data('n_quiz_submissions', course_id=course_id, quiz_id=quiz_id)


def get_courses_from_terms(term_ids):
    """
    Given a list of term_ids, return a deduplicated list of all course_ids
    in those terms, based on the term cache.
    """
    term_cache = cache_manager.load_term_cache()
    courses = set()

    for tid in term_ids:
        term = term_cache.get(tid, {})
        courses.update(term.get("courses", []))

    return list(courses)


def get_courses_from_users(user_ids):
    """
    Given a list of user_ids, return a deduplicated list of all course_ids
    they are enrolled in, based on the user cache.
    """
    user_cache = cache_manager.load_user_cache()
    courses = set()

    for uid in user_ids:
        user = user_cache.get(uid, {})
        courses.update(user.get("courses", []))

    return list(courses)
