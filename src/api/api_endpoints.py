import config.config as config
import requests
import json
import os
from datetime import datetime, timedelta
import utils.cache_manager as cache_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

term_cache, course_cache, user_cache, quiz_cache, submission_cache = {}, {}, {}, {}, {}

### Make term cache
# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_term(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global term_cache
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

### Make term cache
# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_courses(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global term_cache
    if (not data) or course_id or quiz_id or user_id:
        return None

    for course in data:
        if 'id' not in course or 'enrollment_term_id' not in course:
            logging.error(f"endpoint_courses: Missing 'id' or 'enrollment_term_id' in provided data: {course}")
            continue
        course_id = str(course.get('id'))
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

### Add quizzes to course cache
# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
def endpoint_quizzes(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global course_cache

    if term_id or quiz_id or user_id or not data or not course_id:
        logging.error("endpoint_quizzes: Invalid input provided; skipping course cache update.")
        return
    for quiz in data:
        if 'id' not in quiz:
            logging.error(f"endpoint_quizzes: Missing 'id' in provided data: {quiz}")
            continue
        qid = str(quiz.get('id'))
        cache = course_cache.setdefault(course_id, {})
        for key, default in [("code", ""), ("name", ""), ("term", ""), ("users", []), ("quizzes", [])]:
            if not cache.get(key):
                cache[key] = default
        cache["quizzes"].append(qid)
        course_cache[course_id] = cache
    cache_manager.save_course_cache()

### Make user cache
# user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_enrollments(data=None, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global user_cache
    if not data or not user_id:
        logging.error("endpoint_enrollments: Invalid input provided; skipping user cache update.")
        return
    u_cache = user_cache.setdefault(user_id, {})
    for key, default in [("sortable_name", ""), ("sis_id", ""), ("email", ""), ("courses", [])]:
        if key not in u_cache:
            u_cache[key] = default
    enrollments = data if isinstance(data, list) else [data]
    for enrollment in enrollments:
        cid = str(enrollment.get('course_id', ''))
        if cid and cid not in u_cache["courses"]:
            u_cache["courses"].append(cid)
            
    user_cache[str(user_id)] = u_cache
    cache_manager.save_user_cache()

### Make course cache
# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
def endpoint_course(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global course_cache

    if not data or not course_id or term_id or quiz_id or user_id:
        logging.error("endpoint_course: Invalid input provided; skipping course cache update.")
        return
    
    for course in data:
        print('here1')
        if 'id' not in course:
            print('here2')
            logging.error(f"endpoint_course: Missing 'id' in provided data: {course}")
            continue
        print(f'here3, {course}')

        course_id = str(course.get('id'))
        cache = course_cache.setdefault(course_id, {})
        for key, default in [("code", ""), ("name", ""), ("term", ""), ("users", []), ("quizzes", [])]:
            if not cache.get(key):
                cache[key] = default
        cache["code"] = course.get('course_code', '')
        cache["name"] = course.get('name', '')
        cache["term"] = course.get('term', '')
        course_cache[course_id] = cache
    cache_manager.save_course_cache()

# Add users to course cache
# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
# user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': [course_id, course_id, course_id]}, ...}
def endpoint_course_users(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global course_cache, user_cache

    if not data or not course_id or term_id or quiz_id or user_id:
        logging.error("endpoint_course_users: Invalid input provided; skipping cache updates.")
        return
    
    for user in data:
        if 'id' not in user:
            logging.error(f"endpoint_course_users: Missing 'id' in provided data: {user}")
            continue
        uid = str(user.get('id'))
        u_cache = user_cache.setdefault(uid, {})
        for key, default in [("sortable_name", ""), ("sis_id", ""), ("email", ""), ("courses", [])]:
            if not u_cache.get(key):
                u_cache[key] = default
        u_cache["sortable_name"] = user.get('sortable_name', '')
        u_cache["sis_id"] = user.get('sis_user_id', '')
        u_cache["email"] = user.get('email', '')
        if course_id not in u_cache["courses"]:
            u_cache["courses"].append(course_id)

        c_cache = course_cache.setdefault(course_id, {})
        for key, default in [("code", ""), ("name", ""), ("term", ""), ("users", []), ("quizzes", [])]:
            if not c_cache.get(key):
                c_cache[key] = default
        c_cache["users"].append(uid)
        user_cache[uid] = u_cache
        course_cache[course_id] = c_cache
    cache_manager.save_course_cache()
    cache_manager.save_user_cache()

### Make quiz cache
# quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}
def endpoint_quiz(data, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=''):
    global quiz_cache
    if not data or not course_id or not quiz_id or term_id or user_id:
        logging.error("endpoint_quiz: Invalid input provided; skipping quiz cache update.")
        return
    
    if 'title' not in data or 'time_limit' not in data:
        logging.error(f"endpoint_quiz: Missing 'title' or 'time_limit' in provided data: {data}")
        return
    quiz_cache.setdefault(quiz_id, {}).update({'title': data.get('title', ''), 'time_limit': data.get('time_limit', ''), 'type': acc_type, 'course_id': course_id})
    print(f'Quiz cache: {quiz_cache}')

### Make submission cache
# submission_cache = {submission_id: {'user_id': user_id, 'quiz_id': quiz_id, 'extra_time': extra_time, 'extra_attempts': extra_attempts, 'date': date}, ...}
def endpoint_submissions(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    global submission_cache

    if not data or term_id or user_id or not course_id or not quiz_id:
        logging.error("endpoint_submissions: Invalid input provided; skipping submission cache update.")
        return
    
    submissions = data if isinstance(data, list) else [data]
    
    for submission in submissions:
        if 'user_id' not in submission:
            logging.error(f"endpoint_submissions: Missing 'user_id' in provided data: {submission}")
            continue
        uid = submission.get('user_id', None)

        user_dict = submission_cache.setdefault(str(uid), {})
        course_dict = user_dict.setdefault(course_id, {})
        quiz_dict = course_dict.setdefault(quiz_id, {})

        if not all(key in submission for key in ['extra_time', 'extra_attempts', 'workflow_state']):
            logging.error(f"endpoint_submissions: Missing data in provided data: {submission}")
            continue

        extra_time = submission.get('extra_time', '')
        extra_attempts = submission.get('extra_attempts', '')
        workflow = submission.get('workflow_state', '')
        quiz_dict['extra_time'] = extra_time
        quiz_dict['extra_attempts'] = extra_attempts
        quiz_dict['date'] = (
            'past' if workflow in ['complete', 'graded'] else
            'future' if workflow == 'settings_only' else
            ''
        )
        


#######################################################

### Make quiz cache
# quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}
def search_urls(url, course_id):
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
                'type': '',
                'course_id': course_id
            })
    print(f'Quiz cache after url search: {quiz_cache}')