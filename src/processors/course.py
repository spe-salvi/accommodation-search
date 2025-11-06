import logging
from db.repositories.course_repo import CourseRepository

logger = logging.getLogger(__name__)
course_repo = CourseRepository()

def endpoint_courses(data, term_id=None, **kwargs):
    """
    Process a list of courses for a given term and persist them to SQLite.
    Example API data (abbreviated):
    [
      {"id": 54091, "name": "Intro to Programming", "course_code": "CS101", "enrollment_term_id": 116},
      {"id": 54092, "name": "Data Structures", "course_code": "CS102", "enrollment_term_id": 116}
    ]
    """
    if not data:
        logger.warning("endpoint_courses called with empty data.")
        return []

    stored = []
    for course in data:
        course_id = str(course.get("id"))
        name = course.get("name", "")
        code = course.get("course_code", "")
        term = str(course.get("enrollment_term_id") or term_id)

        if not course_id or not name:
            logger.warning(f"Skipping invalid course record: {course}")
            continue

        course_repo.upsert(course_id, code, name, term)
        stored.append(course_id)
        logger.info(f"Stored course {course_id}: {name}")

    return stored


def endpoint_course(data, term_id=None, **kwargs):
    """
    Process a single course response and persist it.
    """
    if not data:
        logger.warning("endpoint_course called with empty data.")
        return None

    course_id = str(data.get("id"))
    name = data.get("name", "")
    code = data.get("course_code", "")
    term = str(data.get("enrollment_term_id") or term_id)

    if not course_id or not name:
        logger.warning(f"Invalid course record: {data}")
        return None

    course_repo.upsert(course_id, code, name, term)
    logger.info(f"Stored single course {course_id}: {name}")
    return course_id


def endpoint_course_users(data, course_id=None, **kwargs):
    """
    Links users to a course in the course_users table.
    Example input:
    [
      {"id": 341, "name": "Jane Doe"},
      {"id": 342, "name": "John Smith"}
    ]
    """
    if not data or not course_id:
        logger.warning("endpoint_course_users called with missing data or course_id.")
        return []

    linked = []
    for user in data:
        uid = str(user.get("id"))
        if not uid:
            continue
        course_repo.link_user(course_id, uid)
        linked.append(uid)

    logger.info(f"Linked {len(linked)} users to course {course_id}")
    return linked

def endpoint_course_quizzes(data, course_id=None, **kwargs):
    """Link quizzes to a course."""
    if not data or not course_id:
        return []

    linked = []
    for quiz in data:
        qid = str(quiz.get("id"))
        if not qid:
            continue
        course_repo.link_quiz(course_id, qid)
        linked.append(qid)

    logger.info(f"Linked {len(linked)} quizzes to course {course_id}")
    return linked
