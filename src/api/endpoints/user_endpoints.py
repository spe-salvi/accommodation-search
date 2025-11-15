from db.repositories.user_repo import UserRepository
from db.repositories.course_repo import CourseRepository
import logging

logger = logging.getLogger(__name__)
user_repo = UserRepository()
course_repo = CourseRepository()


def endpoint_users(data=None, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=None, quiz_type=None):
    if not data:
        logger.warning("endpoint_users called with missing data.")
        return

    for user in data:
        uid = user.get('id')
        sortable_name = user.get('sortable_name')
        sis = user.get('sis_user_id')

        user_repo.upsert(uid, sortable_name, sis, None)

    logger.info(f"Processed ({len(data)} user(s)).")
    return

'''
-- USER STORE
CREATE TABLE IF NOT EXISTS user_store (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    sis_id TEXT,
    email TEXT
);
'''

def endpoint_enrollments(data=None, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=None, quiz_type=None):
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
