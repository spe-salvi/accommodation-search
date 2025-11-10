import logging
import asyncio
from utils.retry_request import retry_get
import config as config
from db.repositories.quiz_repo import QuizRepository

logger = logging.getLogger(__name__)
quiz_repo = QuizRepository()


def endpoint_quiz(data, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=''):
    """
    Processes a single quiz response and saves it to the database.
    """
    if not data or not course_id or not quiz_id:
        logger.warning("endpoint_quiz: Missing required parameters.")
        return

    title = data.get('title', '')
    time_limit = data.get('time_limit', '')

    quiz_repo.upsert(str(quiz_id), title, time_limit, acc_type, str(course_id))
    quiz_repo.link_to_course(str(course_id), str(quiz_id))

    logger.info(f"Stored quiz {quiz_id}: {title} ({acc_type}) in course {course_id}")
    return
