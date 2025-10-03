from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.cache_manager import *
from api.api_params import get_data
import logging
import utils.cache_manager as cache_manager
import config.config as config
import api.api_endpoints as api_endpoints

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

all_course_ids, all_user_ids, all_quiz_ids = set(), set(), set()

def call_populate(**kwargs):
    logger.info("Starting cache population process")
    term_id = kwargs.get('term_ids') if kwargs.get('term_ids') else None
    course_ids = kwargs.get('course_ids') if kwargs.get('course_ids') else None
    user_ids = kwargs.get('user_ids') if kwargs.get('user_ids') else None
    quiz_ids = kwargs.get('quiz_ids') if kwargs.get('quiz_ids') else None
    accom_type = kwargs.get('accom_type') if kwargs.get('accom_type') else 'all'
    # date_filter = kwargs.get('input_data')[5]
    
    logger.info('Populating term cache')
    populate_term_cache(term_id)

    # logger.info('Getting user ids')
    # user_ids = get_user_ids(user_search)
    # logger.info('Getting course ids')
    # course_ids = get_course_ids(term_id, user_ids, course_search)
    # logger.info('Getting quiz ids')
    # quiz_ids = get_quiz_ids(course_ids, quiz_search)

    # Standard pipeline
    populate_course_cache(course_ids)
    populate_user_cache(term_id, course_ids, user_ids)
    populate_quiz_cache(course_ids, quiz_ids)
    populate_submissions_cache(course_ids, quiz_ids)
    populate_question_cache(course_ids, quiz_ids)

    if accom_type == 'spell_check' or accom_type == 'all':
        populate_question_cache(course_ids, quiz_ids)

def populate_term_cache(term_id, course_ids=None):
    logger.info("Populating term cache")

    if not term_id:
        logger.error("No term IDs provided for populating term cache")
        return

    logger.info(f"Processing term {term_id}")
    get_data("term", term_id=term_id)   # cache writes happen under lock
    if not course_ids:
        get_data("courses", term_id=term_id)
    logger.info(f"Finished processing term {term_id}")


def populate_course_cache(course_ids):
    global all_user_ids, all_quiz_ids
    logger.info("Populating course cache")
    logger.info(f"Initial all_user_ids: {all_user_ids}")
    logger.info(f"Initial all_quiz_ids: {all_quiz_ids}")

    if not course_ids:
        logger.info("No course IDs provided for populating course cache")

    def process_course(cid):
        try:
            logger.info(f"Processing course {cid}")
            # Each call handles its own locking inside endpoint
            get_data("course", course_id=cid)
            get_data("c_quizzes", course_id=cid)
            get_data("n_quizzes", course_id=cid)
            get_data("course_users", course_id=cid)
            logger.info(f"Finished processing course {cid}")
        except Exception as e:
            logger.error(f"Error processing course {cid}: {e}")
            raise

    # Run one thread per course (cap to avoid too many threads)
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = {executor.submit(process_course, cid): cid for cid in course_ids}
        for future in as_completed(futures):
            cid = futures[future]
            try:
                future.result()
                logger.info(f"Completed course {cid}")
            except Exception:
                logger.error(f"Course {cid} failed")

    course_cache = cache_manager.load_course_cache()
    for cid in course_ids:
        if cid not in course_cache:
            logger.warning(f"Course ID {cid} not found in course cache after population.")
        for quiz_id in course_cache.get(cid, {}).get("quizzes", []):
            all_quiz_ids.add(quiz_id)
        for user_id in course_cache.get(cid, {}).get("users", []):
            all_user_ids.add(user_id)

    logger.info(f"Loaded {len(course_cache)} courses from cache.")



def populate_user_cache(term_id, course_ids, user_ids):
    global all_course_ids, all_user_ids
    logger.info("Populating user cache")
    logger.info(f"Initial all_user_ids: {all_user_ids}")
    logger.info(f"Initial all_course_ids: {all_course_ids}")

    term_ids = term_id if term_id else list(config.TERMS.keys())
    course_ids = course_ids if course_ids else list(all_course_ids)
    user_ids = user_ids if user_ids else list(all_user_ids)

    # Threaded fetching of course users
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [executor.submit(get_data, 'course_users', course_id=cid) for cid in course_ids]
        for f in as_completed(futures):
            _ = f.result()

    # Threaded fetching of enrollments
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [
            executor.submit(get_data, 'enrollments', term_id=term_id, user_id=uid)
            for term_id in term_ids for uid in user_ids
        ]
        for f in as_completed(futures):
            _ = f.result()

    # Refresh cache after threaded fetches
    user_cache = cache_manager.load_user_cache()
    logger.info(f"Loaded {len(user_cache)} users from cache.")
    for uid in user_ids:
        if uid not in user_cache:
            logger.warning(f"User ID {uid} not found in user cache after population.")
        for course_id in user_cache.get(uid, {}).get("courses", []):
            all_course_ids.add(course_id)



def populate_quiz_cache(course_ids, quiz_ids=None):
    global all_course_ids, all_quiz_ids
    logger.info("Populating quiz cache")

    course_ids = course_ids if course_ids else list(all_course_ids)
    quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

    # Filter quiz_ids by course
    filtered_quiz_ids = set()
    course_cache = cache_manager.load_course_cache()
    for cid in course_ids:
        course_quizzes = set(course_cache.get(cid, {}).get("quizzes", []))
        for qid in quiz_ids:
            if qid in course_quizzes:
                filtered_quiz_ids.add((cid, qid))

    if not filtered_quiz_ids:
        logger.warning("No valid course/quiz pairs found to populate.")
        return

    def process_quiz(cid, qid):
        try:
            logger.info(f"Processing course/quiz {cid} | {qid}")
            get_data('c_quiz', course_id=cid, quiz_id=qid)
            get_data('n_quiz', course_id=cid, quiz_id=qid)
            logger.info(f"Finished processing course/quiz {cid} | {qid}")
        except Exception as e:
            logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
            raise

    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [executor.submit(process_quiz, cid, qid) for cid, qid in filtered_quiz_ids]
        for f in as_completed(futures):
            _ = f.result()

    quiz_cache = api_endpoints.quiz_cache
    for _, qid in filtered_quiz_ids:
        if qid not in quiz_cache:
            logger.warning(f"Quiz ID {qid} not found in quiz cache after population.")
        else:
            all_course_ids.add(quiz_cache[qid].get("course_id"))
    #search_urls

def populate_submissions_cache(course_ids, quiz_ids=None):
    global all_course_ids, all_quiz_ids
    logger.info("Populating submissions cache")
    logger.info(f"Initial all_course_ids: {all_course_ids}")
    logger.info(f"Initial all_quiz_ids: {all_quiz_ids}")

    course_ids = course_ids if course_ids else list(all_course_ids)
    quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

    def process_submission(cid, qid):
        try:
            logger.info(f"Processing course/quiz {cid} | {qid}")
            # Each call handles its own locking inside endpoint
            get_data('c_quiz_submissions', course_id=cid, quiz_id=qid)
            get_data('n_quiz_submissions', course_id=cid, quiz_id=qid)
            logger.info(f"Finished processing course/quiz {cid} | {qid}")
        except Exception as e:
            logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
            raise

    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [
            executor.submit(process_submission, cid, qid)
            for cid in course_ids for qid in quiz_ids
        ]
        for f in as_completed(futures):
            _ = f.result()

    logger.info("Finished populating submissions cache")

def populate_question_cache(course_ids, quiz_ids=None):
    global all_course_ids, all_quiz_ids
    logger.info("Populating question cache")
    logger.info(f'Initial all_course_ids: {all_course_ids}')
    logger.info(f'Initial all_quiz_ids: {all_quiz_ids}')

    course_ids = course_ids if course_ids else list(all_course_ids)
    quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

    def process_question(cid, qid):
        try:
            logger.info(f"Processing course/quiz {cid} | {qid}")
            # Each call handles its own locking inside endpoint
            get_data('n_quiz_items', course_id=cid, quiz_id=qid)
            logger.info(f"Finished processing course/quiz {cid} | {qid}")
        except Exception as e:
            logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
            raise

    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [
            executor.submit(process_question, cid, qid)
            for cid in course_ids for qid in quiz_ids
        ]
        for f in as_completed(futures):
            _ = f.result()

def get_user_ids(search_term=None):
    try:
        return get_data('users', search_term=search_term)
    except:
        logger.info(f'Failure processing user search with search term: {search_term}')
        return

def get_course_ids(term_id=None, user_ids=None, search_term=None):
    if search_term:
        # Flatten the list if get_data returns lists per term
        course_lists = get_data('courses', term_id=term_id, search_term=search_term)
        logger.info(f'Course_lists before flattening: {course_lists}')
        # Flatten and deduplicate
        course_ids = list({cid for sublist in course_lists for cid in (sublist or [])})
        return course_ids

    if len(user_ids) == 0:
        return get_courses_from_terms(term_id)
    return get_courses_from_users(user_ids)

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

def get_quiz_ids(course_ids, search_term):
    quiz_ids = []
    quiz_ids.append(get_data('c_quizzes', course_ids=course_ids, search_param=search_term))
    quiz_ids.append(get_data('n_quizzes', course_ids=course_ids, search_param=search_term))
    return list(set(quiz_ids))