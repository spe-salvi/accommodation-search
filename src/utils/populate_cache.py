from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.cache_manager import *
from api.api_params import get_data
import logging
import utils.cache_manager as cache_manager
import config.config as config
import api.api_endpoints as api_endpoints
import input.input_api as input_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# all_course_ids, all_user_ids, all_quiz_ids = set(), set(), set()

# def call_populate(term_id=None, course_ids=None, user_ids=None, quiz_ids=None, accom_type='all'):
#     logger.info("Starting cache population process")
#     populate_term_cache(term_id)
#     populate_course_cache(course_ids)
#     populate_user_cache(term_id, course_ids, user_ids)
#     populate_quiz_cache(course_ids, quiz_ids)
#     populate_submissions_cache(course_ids, quiz_ids)

#     if accom_type == 'spell_check' or accom_type == 'all':
#         populate_question_cache(course_ids, quiz_ids)

# def populate_term_cache(term_id, course_ids=None):
#     logger.info("Populating term cache")

#     if not term_id:
#         logger.error("No term IDs provided for populating term cache")
#         return

#     logger.info(f"Processing term {term_id}")
#     get_data("term", term_id=term_id)   # cache writes happen under lock
#     if not course_ids:
#         get_data("courses", term_id=term_id)
#     logger.info(f"Finished processing term {term_id}")


# def populate_course_cache(course_ids):
#     global all_user_ids, all_quiz_ids
#     logger.info("Populating course cache")
#     logger.info(f"Initial all_user_ids: {all_user_ids}")
#     logger.info(f"Initial all_quiz_ids: {all_quiz_ids}")

#     if not course_ids:
#         logger.error("No course IDs provided for populating course cache")

#     def process_course(cid):
#         try:
#             logger.info(f"Processing course {cid}")
#             # Each call handles its own locking inside endpoint
#             get_data("course", course_id=cid)
#             get_data("c_quizzes", course_id=cid)
#             get_data("n_quizzes", course_id=cid)
#             get_data("course_users", course_id=cid)
#             logger.info(f"Finished processing course {cid}")
#         except Exception as e:
#             logger.error(f"Error processing course {cid}: {e}")
#             raise

#     # Run one thread per course (cap to avoid too many threads)
#     with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
#         futures = {executor.submit(process_course, cid): cid for cid in course_ids}
#         for future in as_completed(futures):
#             cid = futures[future]
#             try:
#                 future.result()
#                 logger.info(f"Completed course {cid}")
#             except Exception:
#                 logger.error(f"Course {cid} failed")

#     course_cache = cache_manager.load_course_cache()
#     for cid in course_ids:
#         if cid not in course_cache:
#             logger.warning(f"Course ID {cid} not found in course cache after population.")
#         for quiz_id in course_cache.get(cid, {}).get("quizzes", []):
#             all_quiz_ids.add(quiz_id)
#         for user_id in course_cache.get(cid, {}).get("users", []):
#             all_user_ids.add(user_id)

#     logger.info(f"Loaded {len(course_cache)} courses from cache.")



# def populate_user_cache(term_id, course_ids, user_ids):
#     global all_course_ids, all_user_ids
#     logger.info("Populating user cache")
#     logger.info(f"Initial all_user_ids: {all_user_ids}")
#     logger.info(f"Initial all_course_ids: {all_course_ids}")

#     course_ids = course_ids if course_ids else list(all_course_ids)
#     user_ids = user_ids if user_ids else list(all_user_ids)

#     # Threaded fetching of course users
#     with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
#         futures = [executor.submit(get_data, 'course_users', course_id=cid) for cid in course_ids]
#         for f in as_completed(futures):
#             _ = f.result()

#     # Threaded fetching of enrollments
#     with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
#         futures = [
#             executor.submit(get_data, 'enrollments', term_id=term_id, user_id=uid)
#             for uid in user_ids
#         ]
#         for f in as_completed(futures):
#             _ = f.result()

#     # Refresh cache after threaded fetches
#     user_cache = cache_manager.load_user_cache()
#     logger.info(f"Loaded {len(user_cache)} users from cache.")
#     for uid in user_ids:
#         if uid not in user_cache:
#             logger.warning(f"User ID {uid} not found in user cache after population.")
#         for course_id in user_cache.get(uid, {}).get("courses", []):
#             all_course_ids.add(course_id)



# def populate_quiz_cache(course_ids, quiz_ids=None):
#     global all_course_ids, all_quiz_ids
#     logger.info("Populating quiz cache")

#     course_ids = course_ids if course_ids else list(all_course_ids)
#     quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)
#     pairs = [(course, quiz) for course in course_ids for quiz in quiz_ids]

#     # # Filter quiz_ids by course
#     # filtered_quiz_ids = set()
#     # course_cache = cache_manager.load_course_cache()
#     # for cid in course_ids:
#     #     course_quizzes = set(course_cache.get(cid, {}).get("quizzes", []))
#     #     for qid in quiz_ids:
#     #         if qid in course_quizzes:
#     #             filtered_quiz_ids.add((cid, qid))

#     logger.info(f"Course cache keys: {list(course_cache.keys())}")
#     logger.info(f"Sample course entry: {course_cache.values()}")

#     # if not filtered_quiz_ids:
#     #     logger.warning("No valid course/quiz pairs found to populate.")
#     #     return

#     def process_quiz(cid, qid):
#         try:
#             logger.info(f"Processing course/quiz {cid} | {qid}")
#             get_data('c_quiz', course_id=cid, quiz_id=qid)
#             get_data('n_quiz', course_id=cid, quiz_id=qid)
#             logger.info(f"Finished processing course/quiz {cid} | {qid}")
#         except Exception as e:
#             logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
#             raise

#     with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
#         futures = [executor.submit(process_quiz, cid, qid) for cid, qid in pairs]
#         for f in as_completed(futures):
#             _ = f.result()

#     quiz_cache = api_endpoints.quiz_cache
#     for _, qid in pairs:
#         if qid not in quiz_cache:
#             logger.warning(f"Quiz ID {qid} not found in quiz cache after population.")
#         else:
#             all_course_ids.add(quiz_cache[qid].get("course_id"))
#     #search_urls

# def populate_submissions_cache(course_ids, quiz_ids=None):
#     global all_course_ids, all_quiz_ids
#     logger.info("Populating submissions cache")
#     logger.info(f"Initial all_course_ids: {all_course_ids}")
#     logger.info(f"Initial all_quiz_ids: {all_quiz_ids}")

#     course_ids = course_ids if course_ids else list(all_course_ids)
#     quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

#     def process_submission(cid, qid):
#         try:
#             logger.info(f"Processing course/quiz {cid} | {qid}")
#             # Each call handles its own locking inside endpoint
#             get_data('c_quiz_submissions', course_id=cid, quiz_id=qid)
#             get_data('n_quiz_submissions', course_id=cid, quiz_id=qid)
#             logger.info(f"Finished processing course/quiz {cid} | {qid}")
#         except Exception as e:
#             logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
#             raise

#     with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
#         futures = [
#             executor.submit(process_submission, cid, qid)
#             for cid in course_ids for qid in quiz_ids
#         ]
#         for f in as_completed(futures):
#             _ = f.result()

#     logger.info("Finished populating submissions cache")

# def populate_question_cache(course_ids, quiz_ids=None):
#     global all_course_ids, all_quiz_ids
#     logger.info("Populating question cache")
#     logger.info(f'Initial all_course_ids: {all_course_ids}')
#     logger.info(f'Initial all_quiz_ids: {all_quiz_ids}')

#     course_ids = course_ids if course_ids else list(all_course_ids)
#     quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

#     def process_question(cid, qid):
#         try:
#             logger.info(f"Processing course/quiz {cid} | {qid}")
#             # Each call handles its own locking inside endpoint
#             get_data('n_quiz_items', course_id=cid, quiz_id=qid)
#             logger.info(f"Finished processing course/quiz {cid} | {qid}")
#         except Exception as e:
#             logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
#             raise

#     with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
#         futures = [
#             executor.submit(process_question, cid, qid)
#             for cid in course_ids for qid in quiz_ids
#         ]
#         for f in as_completed(futures):
#             _ = f.result()


def call_populate(term_id=None, course_ids=None, user_ids=None, quiz_ids=None, accom_type='all'):
    """
    Populates all caches in a single ThreadPoolExecutor for maximum efficiency.
    """
    logger.info("Starting cache population process")
<<<<<<< HEAD
    term_search = kwargs.get('input_data')[0]
    course_search = kwargs.get('input_data')[1]
    quiz_search = kwargs.get('input_data')[2]
    user_search = kwargs.get('input_data')[3]
    accom_type = kwargs.get('input_data')[4]
    # date_filter = kwargs.get('input_data')[5]
    
    term_ids = input_api.get_term_id(term_search)
    logger.info(f'Term IDs: {term_ids}')
    populate_term_cache(term_ids)

    user_ids = get_user_ids(user_search)
    logger.info(f'User IDs: {user_ids}')
    course_ids = get_course_ids(term_ids, user_ids, course_search)
    logger.info(f'Course IDs: {course_ids}')
    quiz_ids = get_quiz_ids(course_ids, quiz_search)
    logger.info(f'Quiz IDs: {quiz_ids}')

    # # Standard pipeline
    # populate_course_cache(course_ids)
    # populate_user_cache(term_ids, course_ids, user_ids)
    # populate_quiz_cache(course_ids, quiz_ids)
    # populate_submissions_cache(course_ids, quiz_ids)
    # populate_question_cache(course_ids, quiz_ids)

    # if accom_type == 'spell_check' or accom_type == 'all':
    #     populate_question_cache(course_ids, quiz_ids)

def populate_term_cache(term_id, course_ids=None):
    # logger.info("Populating term cache")

    if not term_id:
        logger.error("No term IDs provided for populating term cache")
        return

    # logger.info(f"Processing term {term_id}")
    get_data("term", term_id=term_id)   # cache writes happen under lock
    if not course_ids:
        get_data("courses", term_id=term_id)
    # logger.info(f"Finished processing term {term_id}")


def populate_course_cache(course_ids):
    global all_user_ids, all_quiz_ids
    # logger.info("Populating course cache")
    # logger.info(f"Initial all_user_ids: {all_user_ids}")
    # logger.info(f"Initial all_quiz_ids: {all_quiz_ids}")

    # if not course_ids:
    #     logger.info("No course IDs provided for populating course cache")

    def process_course(cid):
        try:
            # logger.info(f"Processing course {cid}")
            # Each call handles its own locking inside endpoint
            get_data("course", course_id=cid)
            get_data("c_quizzes", course_id=cid)
            get_data("n_quizzes", course_id=cid)
            get_data("course_users", course_id=cid)
            # logger.info(f"Finished processing course {cid}")
        except Exception as e:
            # logger.error(f"Error processing course {cid}: {e}")
            raise

    # Run one thread per course (cap to avoid too many threads)
=======

    tasks = []

    # 1️⃣ Term cache tasks
    if term_id:
        tasks.append(('term', {'term_id': term_id}))
        tasks.append(('courses', {'term_id': term_id}))  # populate course list for term

    # 2️⃣ Course cache tasks
    for cid in course_ids or []:
        tasks.append(('course', {'course_id': cid}))
        tasks.append(('c_quizzes', {'course_id': cid}))
        tasks.append(('n_quizzes', {'course_id': cid}))
        tasks.append(('course_users', {'course_id': cid}))  # one call per course

    # 🔹 Execute all tasks that populate course_cache first
    # course_task_types = {'term', 'courses', 'course', 'c_quizzes', 'n_quizzes', 'course_users'}
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = {
            executor.submit(get_data, ttype, **params): (ttype, params)
            for ttype, params in tasks
        }
        for future in as_completed(futures):
<<<<<<< HEAD
            cid = futures[future]
            # try:
            future.result()
                # logger.info(f"Completed course {cid}")
            # except Exception:
            #     logger.error(f"Course {cid} failed")

    course_cache = cache_manager.load_course_cache()
    for cid in course_ids:
        # if cid not in course_cache:
            # logger.warning(f"Course ID {cid} not found in course cache after population.")
        for quiz_id in course_cache.get(cid, {}).get("quizzes", []):
            all_quiz_ids.add(quiz_id)
        for user_id in course_cache.get(cid, {}).get("users", []):
            all_user_ids.add(user_id)

    # logger.info(f"Loaded {len(course_cache)} courses from cache.")
=======
            ttype, params = futures[future]
            try:
                future.result()
                logger.debug(f"Completed {ttype} task with {params}")
            except Exception as e:
                logger.error(f"Task {ttype} failed with {params}: {e}")

    # 3️⃣ Filter course/quiz pairs after caches are populated
    course_cache = cache_manager.load_course_cache()  # ensure latest quizzes
    logger.info('Course Cache after first pool:')
    logger.info(course_cache)
    quiz_pairs = []
    for cid in course_ids or []:
        logger.info(f'Course ID for Pair Construction: {cid}')
        quizzes_in_course = set(course_cache.get(cid, {}).get('quizzes', []))
        logger.info(f'Num quizzes in course: {len(quizzes_in_course)}')
        if quiz_ids:
            quizzes_in_course &= set(quiz_ids)
        for qid in quizzes_in_course:
            quiz_pairs.append((cid, qid))

    # 4️⃣ Build remaining tasks: quizzes, submissions, questions, enrollments
    remaining_tasks = []
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59

    logger.info(f'Num Quiz Pairs: {len(quiz_pairs)}')
    for cid, qid in quiz_pairs:
        logger.info(f'Course | Quiz Pair: {cid} | {qid}')
        remaining_tasks.append(('c_quiz', {'course_id': cid, 'quiz_id': qid}))
        remaining_tasks.append(('n_quiz', {'course_id': cid, 'quiz_id': qid}))
        remaining_tasks.append(('c_quiz_submissions', {'course_id': cid, 'quiz_id': qid}))
        remaining_tasks.append(('n_quiz_submissions', {'course_id': cid, 'quiz_id': qid}))
        if accom_type in ('spell_check', 'all'):
            remaining_tasks.append(('n_quiz_items', {'course_id': cid, 'quiz_id': qid}))

<<<<<<< HEAD

def populate_user_cache(term_id, course_ids, user_ids):
    global all_course_ids, all_user_ids
    # logger.info("Populating user cache")
    # logger.info(f"Initial all_user_ids: {all_user_ids}")
    # logger.info(f"Initial all_course_ids: {all_course_ids}")

    term_ids = term_id if term_id else list(config.TERMS.keys())
    course_ids = course_ids if course_ids else list(all_course_ids)
    user_ids = user_ids if user_ids else list(all_user_ids)

    # Threaded fetching of course users
=======
    # 🔥 Single executor for all remaining tasks
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = {
            executor.submit(get_data, ttype, **params): (ttype, params)
            for ttype, params in remaining_tasks
        }
        for future in as_completed(futures):
            ttype, params = futures[future]
            try:
                future.result()
                logger.debug(f"Completed {ttype} task with {params}")
            except Exception as e:
                logger.error(f"Task {ttype} failed with {params}: {e}")

    logger.info('Quiz Cache after second pool:')
    logger.info(api_endpoints.quiz_cache)
    logger.info('Submission Cache after second pool:')
    logger.info(api_endpoints.submission_cache)

<<<<<<< HEAD
    # Refresh cache after threaded fetches
    user_cache = cache_manager.load_user_cache()
    # logger.info(f"Loaded {len(user_cache)} users from cache.")
    for uid in user_ids:
        # if uid not in user_cache:
        #     logger.warning(f"User ID {uid} not found in user cache after population.")
        for course_id in user_cache.get(uid, {}).get("courses", []):
            all_course_ids.add(course_id)



def populate_quiz_cache(course_ids, quiz_ids=None):
    global all_course_ids, all_quiz_ids
    # logger.info("Populating quiz cache")

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
        # logger.warning("No valid course/quiz pairs found to populate.")
        return

    def process_quiz(cid, qid):
        try:
            # logger.info(f"Processing course/quiz {cid} | {qid}")
            get_data('c_quiz', course_id=cid, quiz_id=qid)
            get_data('n_quiz', course_id=cid, quiz_id=qid)
            # logger.info(f"Finished processing course/quiz {cid} | {qid}")
        except Exception as e:
            # logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
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
    # logger.info("Populating submissions cache")
    # logger.info(f"Initial all_course_ids: {all_course_ids}")
    # logger.info(f"Initial all_quiz_ids: {all_quiz_ids}")

    course_ids = course_ids if course_ids else list(all_course_ids)
    quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

    def process_submission(cid, qid):
        try:
            # logger.info(f"Processing course/quiz {cid} | {qid}")
            # Each call handles its own locking inside endpoint
            get_data('c_quiz_submissions', course_id=cid, quiz_id=qid)
            get_data('n_quiz_submissions', course_id=cid, quiz_id=qid)
            # logger.info(f"Finished processing course/quiz {cid} | {qid}")
        except Exception as e:
            # logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
            raise

    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [
            executor.submit(process_submission, cid, qid)
            for cid in course_ids for qid in quiz_ids
        ]
        for f in as_completed(futures):
            _ = f.result()

    # logger.info("Finished populating submissions cache")

def populate_question_cache(course_ids, quiz_ids=None):
    global all_course_ids, all_quiz_ids
    # logger.info("Populating question cache")
    # logger.info(f'Initial all_course_ids: {all_course_ids}')
    # logger.info(f'Initial all_quiz_ids: {all_quiz_ids}')

    course_ids = course_ids if course_ids else list(all_course_ids)
    quiz_ids = quiz_ids if quiz_ids else list(all_quiz_ids)

    def process_question(cid, qid):
        try:
            # logger.info(f"Processing course/quiz {cid} | {qid}")
            # Each call handles its own locking inside endpoint
            get_data('n_quiz_items', course_id=cid, quiz_id=qid)
            # logger.info(f"Finished processing course/quiz {cid} | {qid}")
        except Exception as e:
            # logger.error(f"Error processing course/quiz {cid} | {qid}: {e}")
            raise

    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        futures = [
            executor.submit(process_question, cid, qid)
            for cid in course_ids for qid in quiz_ids
        ]
        for f in as_completed(futures):
            _ = f.result()

def get_user_ids(search_term=None):
    if search_term is None or search_term == '':
        return []
    try:
        return get_data('users', search_term=search_term)
    except:
        # logger.info(f'Failure processing user search with search term: {search_term}')
        return []

def get_course_ids(term_id=None, user_ids=None, search_param=None):
    if search_param or not user_ids:
        # Let the API handle the course search/filtering
        course_lists = get_data('courses', term_id=term_id, search_param=search_param)
        logger.debug(f'Course lists from API: {course_lists}')
        
        # Handle None response or empty list
        if not course_lists:
            return []
            
        # If it's a single list, wrap it; if it's already nested, use as is
        if isinstance(course_lists, list) and (not course_lists or not isinstance(course_lists[0], list)):
            course_lists = [course_lists]
            
        # Flatten and deduplicate, skipping None values
        course_ids = {
            str(cid) for sublist in course_lists 
            if sublist  # Skip None sublists
            for cid in sublist 
            if cid is not None  # Skip None course IDs
        }
        return list(course_ids)

    return get_courses_from_users(term_id=term_id, user_ids=user_ids)


def get_courses_from_users(term_id=None, user_ids=None):
    if not user_ids:  # Handles None and empty list
        return []
    
    course_ids = set()  # Use a set to deduplicate

    for uid in user_ids:
        data = get_data('enrollments', term_id=term_id, user_id=uid)
        if data:  # Check for None response
            # Extract course_ids correctly (was creating generator expressions)
            course_ids.update(str(e["course_id"]) for e in data if "course_id" in e)
    
    return list(course_ids)

def get_quiz_ids(course_ids, search_term):
    flattened = set()

    for course_id in course_ids:
        # Classic quizzes
        classic = get_data('c_quizzes', course_id=course_id, search_param=search_term)
        # New quizzes
        new = get_data('n_quizzes', course_id=course_id, search_param=search_term)

        for qlist in (classic, new):
            if qlist:
                for qid in qlist:
                    if qid:
                        flattened.add(str(qid))

    return list(flattened)

=======
    question_cache = cache_manager.load_question_cache()
    logger.info('Question Cache after second pool:')
    logger.info(question_cache)

    logger.info("Finished populating all caches")
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
