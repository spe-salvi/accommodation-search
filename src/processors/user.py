from db.repositories.user_repo import UserRepository
from db.repositories.course_repo import CourseRepository
import logging

logger = logging.getLogger(__name__)
user_repo = UserRepository()
course_repo = CourseRepository()

def get_user_ids_by_search(term_id, user_input):
    """
    Return user_ids matching partial name, SIS ID, or email.
    Optionally filter by courses in the given term.
    """
    if not user_input:
        return []

    matches = []
    users = user_repo.list_all()
    user_input = user_input.lower()

    for u in users:
        if (user_input in str(u.get("name", "")).lower()
            or user_input in str(u.get("sis_id", "")).lower()
            or user_input in str(u.get("email", "")).lower()):
            matches.append(u["user_id"])

    if not term_id:
        return matches

    # filter by users who are in that term’s courses
    course_ids = [c["course_id"] for c in course_repo.list_all() if c.get("term_id") == str(term_id)]
    term_user_ids = {u["user_id"] for cid in course_ids for u in user_repo.get_users_by_course(cid)}

    filtered = [u for u in matches if u in term_user_ids]
    logger.info(f"User search '{user_input}' matched {len(filtered)} users in term {term_id}")
    return filtered

def get_user_ids_by_courses(course_ids):
    """
    Return all users across provided courses.
    """
    results = set()
    for cid in course_ids:
        for u in user_repo.get_users_by_course(cid):
            results.add(u["user_id"])
    return list(results)


def endpoint_enrollments(data=None, term_id=None, course_id=None, quiz_id=None, user_id=None):
    """
    Process enrollment data for a user and persist user info + user-course links.
    """
    if not data or not user_id:
        logger.warning("endpoint_enrollments called with missing data or user_id.")
        return

    uid = str(user_id)
    enrollments = data if isinstance(data, list) else [data]

    for enrollment in enrollments:
        user_repo.upsert(uid)

        # Link user to their enrolled course
        cid = str(enrollment.get("course_id", "")) or str(course_id or "")
        if cid:
            user_repo.link_to_course(uid, cid)

    logger.info(f"Processed enrollments for user {uid} ({len(enrollments)} course(s)).")
    return
