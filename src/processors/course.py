import logging
import processors.user as user
from db.repositories.course_repo import CourseRepository
import api.client as client

logger = logging.getLogger(__name__)
course_repo = CourseRepository()


def get_course_ids_by_term_and_search(term_id: str, course_input: str):
    """
    Return course_ids that match the input text within a specific term.
    """
    logger.info(f"Fetching Canvas courses for term={term_id}, search='{course_input}'")
    client.get_data('courses', term_id=term_id, search_param=course_input)

    courses = course_repo.list_all()
    results = []

    for c in courses:
        if term_id and c.get("term_id") != str(term_id):
            continue
        if course_input and course_input.lower() not in str(c.get("name", "")).lower():
            continue
        results.append(c["course_id"])

    logger.info(f"Found {len(results)} courses matching '{course_input}' in term {term_id}")

    print(f'COURSE SEARCH RESULTS: {results}')
    return results


def get_course_ids_by_users(user_ids, term_id=None):
    """
    Return all course_ids that a user is enrolled in, optionally filtering by term.
    """
    course_repo = CourseRepository()
    user_courses = set()

    for uid in user_ids:
        client.get_data('enrollments', user_id=uid, term_id=term_id)
        for c in course_repo.list_all():
            users = user.get_user_ids_by_courses(c["course_id"])
            if any(u["user_id"] == uid for u in users):
                if not term_id or str(c.get("term_id")) == str(term_id):
                    user_courses.append(c["course_id"])

    print(f'COURSE BY USERS: {list(set(user_courses))}')
    return list(set(user_courses))