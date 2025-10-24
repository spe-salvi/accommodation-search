import config.config as config
import requests
import utils.cache_manager as cache_manager
import logging
import threading

cache_lock = threading.Lock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

quiz_cache, submission_cache = {}, {}
### Make term cache
# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_term(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_term called")
    with cache_lock:
        term_cache = cache_manager.load_term_cache()
        if not term_id:
            if 'id' not in data:
                logging.error(f"endpoint_term: The 'id' key is missing in the provided data. {term_id}")
                return
            term_id = str(data.get('id'))
        term_entry = term_cache.setdefault(term_id, {"name": "", "courses": []})
        if not term_entry["name"]:
            term_entry["name"] = data.get('name', '')
        if not term_entry["courses"]:
            term_entry["courses"] = []
        term_cache[term_id] = term_entry
        cache_manager.save_term_cache()
    # logger.info(f"Term cache after term endpoint: {len(term_cache)} terms")

### Make term cache
# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_courses(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_courses called")
    if (not data) or course_id or quiz_id or user_id:
        return None

    ret_ids = []

    with cache_lock:
        term_cache = cache_manager.load_term_cache()
        for course in data:
            if 'id' not in course or 'enrollment_term_id' not in course:
                # logging.error(f"endpoint_courses: Missing 'id' or 'enrollment_term_id' in provided data: {course}")
                continue
            course_id = str(course.get('id'))
            ret_ids.append(course_id)
            enrollment_term_id = str(course.get('enrollment_term_id'))

            if term_id in term_cache:
                term_entry = term_cache[term_id]
            else:
                term_entry = term_cache.setdefault(enrollment_term_id, {"name": "", "courses": []})

            if not term_entry["courses"]:
                term_entry["courses"] = [course_id]
            else:
                course_ids = term_entry["courses"]
                course_ids.append(course_id)
                term_entry["courses"] = list(set(course_ids))
            term_cache[enrollment_term_id] = term_entry

        cache_manager.save_term_cache()
    # logger.info(f"Term cache after courses endpoint: {len(term_cache)} terms")
    return ret_ids


### Add quizzes to course cache
# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
def endpoint_quizzes(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_quizzes called")

    if not data or not course_id:
        # logging.error("endpoint_quizzes: Invalid input provided; skipping course cache update.")
        return

    cid = str(course_id)
    quiz_ids = []

    with cache_lock:
        course_cache = cache_manager.load_course_cache()
        c_cache = course_cache.setdefault(cid, {})
        for key, default in [("code", ""), ("name", ""), ("term", ""), ("users", []), ("quizzes", [])]:
            c_cache.setdefault(key, default)

        for quiz in data:
            if 'id' not in quiz:
                # logger.error(f"endpoint_quizzes: Missing 'id' in provided data: {quiz}")
                continue
            qid = str(quiz.get('id'))
            quiz_ids.append(qid)
            if qid not in c_cache["quizzes"]:
                c_cache["quizzes"].append(qid)

        course_cache[cid] = c_cache
        cache_manager.save_course_cache()

    # logger.info(f"Course cache after quizzes endpoint: {len(course_cache)} courses")
    return quiz_ids


### Make user cache
# user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_enrollments(data=None, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_enrollments called")

    if not data or not user_id:
        # logger.error("endpoint_enrollments: Invalid input provided; skipping user cache update.")
        return

    with cache_lock:
        user_cache = cache_manager.load_user_cache()
        uid = str(user_id)

        u_cache = user_cache.setdefault(uid, {})
        for key, default in [("sortable_name", ""), ("sis_id", ""), ("email", ""), ("courses", [])]:
            u_cache.setdefault(key, default)

        enrollments = data if isinstance(data, list) else [data]
        for enrollment in enrollments:
            cid = str(enrollment.get('course_id', ''))
            if cid and cid not in u_cache["courses"]:
                u_cache["courses"].append(cid)

        user_cache[uid] = u_cache
        cache_manager.save_user_cache()

    # logger.info(f"User cache after enrollments endpoint: {len(user_cache)} users")

### Make course cache
# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
def endpoint_course(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_course called")

    if not data:
        logging.error("endpoint_course: No data provided; skipping course cache update.")
        return

    if 'id' not in data:
        logging.error(f"endpoint_course: Missing 'id' in provided data: {data}")
        return

    cid = str(data.get('id'))

    with cache_lock:
        course_cache = cache_manager.load_course_cache()
        cache = course_cache.setdefault(cid, {})
        for key, default in [("code", ""), ("name", ""), ("term", ""), ("users", []), ("quizzes", [])]:
            cache.setdefault(key, default)
        cache["code"] = data.get('course_code', '')
        cache["name"] = data.get('name', '')
        cache["term"] = data.get('enrollment_term_id', '')
        course_cache[cid] = cache
        cache_manager.save_course_cache()

    # logger.info(f"Course cache after course endpoint: {len(course_cache)} courses")

# Add users to course cache
# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
# user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': [course_id, course_id, course_id]}, ...}
def endpoint_course_users(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_course_users called")

    if not data or not course_id:
        logging.error("endpoint_course_users: Invalid input provided; skipping cache updates.")
        return

    cid = str(course_id)
    user_ids = []

    with cache_lock:
        course_cache = cache_manager.load_course_cache()
        user_cache = cache_manager.load_user_cache()

        for user in data:
            if 'id' not in user:
                logger.error(f"endpoint_course_users: Missing 'id' in provided data: {user}")
                continue
            uid = str(user.get('id'))
            user_ids.append(uid)

            # Update user cache
            u_cache = user_cache.setdefault(uid, {})
            for key, default in [("sortable_name", ""), ("sis_id", ""), ("email", ""), ("courses", [])]:
                u_cache.setdefault(key, default)
            u_cache["sortable_name"] = user.get('sortable_name', '')
            u_cache["sis_id"] = user.get('sis_user_id', '')
            u_cache["email"] = user.get('email', '')
            if cid not in u_cache["courses"]:
                u_cache["courses"].append(cid)
            user_cache[uid] = u_cache

            # Update course cache
            c_cache = course_cache.setdefault(cid, {})
            for key, default in [("code", ""), ("name", ""), ("term", ""), ("users", []), ("quizzes", [])]:
                c_cache.setdefault(key, default)
            if uid not in c_cache["users"]:
                c_cache["users"].append(uid)
            course_cache[cid] = c_cache

        cache_manager.save_course_cache()
        cache_manager.save_user_cache()

    # logger.info(f"User cache after course_users endpoint: {len(user_cache)} users")
    # logger.info(f"Course cache after course_users endpoint: {len(course_cache)} courses")
    return list(set(user_ids))


### Make quiz cache
# quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}
def endpoint_quiz(data, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=''):
    # logger.info("endpoint_quiz called")
    global quiz_cache

    if not data or not course_id or not quiz_id:
        logger.error("endpoint_quiz: Invalid input provided; skipping quiz cache update.")
        return

    with cache_lock:  # prevent race conditions if multiple threads hit the same quiz
        quiz_cache.setdefault(quiz_id, {}).update({
            'title': data.get('title', ''),
            'time_limit': data.get('time_limit', ''),
            'type': acc_type,
            'course_id': course_id
        })

    # logger.info(f"Quiz cache after quiz endpoint: {len(quiz_cache)} quizzes")

### Make submission cache
# submission_cache = {user_id: {course_id: {quiz_id: {'extra_time': extra_time, 'extra_attempts': extra_attempts, 'date': date}, ...}, ...}, ...}
def endpoint_submissions(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_submissions called")
    global submission_cache

    if not data or not course_id or not quiz_id:
        logger.error("endpoint_submissions: Incomplete parameters; skipping.")
        return
    
    if isinstance(data, dict) and "quiz_submissions" in data:
        submissions = data["quiz_submissions"]
    elif isinstance(data, list):
        submissions = data
    else:
        logger.error(f"endpoint_submissions: Unexpected data format: {data}")
        return

    with cache_lock:  # 🔒 thread-safe writes
        for submission in submissions:
            uid = submission.get('user_id', None)
            if not uid:
                logger.error(f"endpoint_submissions: Missing 'user_id' in provided data: {submission}")
                continue

            user_dict = submission_cache.setdefault(str(uid), {})
            course_dict = user_dict.setdefault(course_id, {})

            workflow = submission['workflow_state']

            course_dict[quiz_id] = {
                'extra_time': submission.get('extra_time', 0),
                'extra_attempts': submission.get('extra_attempts', 0),
                'date': (
                    'past' if workflow in ['complete', 'graded']
                    else 'future' if workflow in ['settings_only', 'unsubmitted']
                    else ''
                )
            }

            # logger.info(f"✅ Cached submission: user={uid}, course={course_id}, quiz={quiz_id}")

    # logger.info(f"Full submission cache: {len(submission_cache)} users")

# TODO: Finish this method
# Define endpoints, construct cache
# question_cache: {course_id: {quiz_id: {item_id: {'question_type':question_type, 'spell_check':(boolean)}}}}
def endpoint_items(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_items called")

    if not data or not (course_id and quiz_id):
        logging.error("endpoint_items: Invalid input provided; skipping cache updates.")
        return

    cid = str(course_id)
    qid = str(quiz_id)

    with cache_lock:
        question_cache = cache_manager.load_question_cache()

        for item in data:
            try:
                item_id = str(item.get("id"))
                entry = item.get("entry", {})
                q_type = entry.get("interaction_type_slug", "unknown")
                if q_type != "essay":
                    continue
                # Prefer spell_check from interaction_data (more reliable than entry.properties)
                spell_check = entry.get("interaction_data", {}).get("spell_check")

                # Insert into nested structure
                question_cache.setdefault(cid, {}).setdefault(qid, {})[item_id] = {
                    "question_type": q_type,
                    "spell_check": bool(spell_check),
                }

                # logger.info(
                    # f"Cached Q: C:{cid}, Q:{qid}, Item:{item_id}, "
                    # f"Type:{q_type}, SpellCheck:{spell_check}"
                # )
            except Exception as e:
                logger.error(f"Error processing item {item}: {e}")

        cache_manager.save_question_cache()

<<<<<<< HEAD
    # logger.info(
        # f"Question cache after item endpoint: "
        # f"{sum(len(q) for q in question_cache.get(cid, {}).values())} questions"
    # )
    return

#######################################################

### Make quiz cache
# quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}
def search_urls(url, course_id):
    # logger.info("search_urls called")
    global quiz_cache
    if not url or not course_id:
        logging.error("search_urls: Invalid input provided; skipping URL search.")
        return
    response = requests.get(url, headers=config.HEADERS)
    if response.status_code == 200:
        data = response.json()
        for quiz in data:
            if 'id' not in quiz or 'title' not in quiz:
                logging.error(f"search_urls: Missing key in provided data: {quiz}")
                continue
            quiz_id = str(quiz.get('id'))
            quiz_cache.setdefault(quiz_id, {}).update({
                'title': quiz.get('title', ''),
                'time_limit': quiz.get('time_limit', ''),
                'type': '',
                'course_id': course_id
            })
    # logger.info(f"Quiz cache after url search: {quiz_cache}")
=======
    logger.info(
        f"Question cache after item endpoint: "
        f"{sum(len(q) for q in question_cache.get(cid, {}).values())} questions"
    )
    return
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
