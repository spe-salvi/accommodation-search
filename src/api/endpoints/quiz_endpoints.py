import logging
import asyncio
from utils.retry_request import retry_get
import config as config
from db.repositories.quiz_repo import QuizRepository

logger = logging.getLogger(__name__)
quiz_repo = QuizRepository()


def endpoint_quiz(data, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=None, quiz_type=None):
    """
    Processes a single quiz response and saves it to the database.
    """
    if not data or not course_id or not quiz_id:
        logger.warning("endpoint_quiz: Missing required parameters.")
        return
    
    if isinstance(data, dict):
        if "errors" in data:
            logger.info(f"endpoint_quiz: Skipping upsert for {quiz_id} ({quiz_type}) — API returned errors.")
            return
        quizzes = [data]
    elif isinstance(data, list):
        # If it's an empty list or all items are error objects, skip
        if len(data) == 0 or all(isinstance(item, dict) and "errors" in item for item in data):
            logger.info(f"endpoint_quiz: No valid quiz data for {quiz_id} ({quiz_type}); skipping upsert.")
            return
        quizzes = data
    else:
        logger.warning(f"endpoint_quiz: Unexpected data type {type(data)} for quiz {quiz_id}. Skipping.")
        return

    for quiz in quizzes:
        title = quiz.get('title', '')
        time_limit = quiz.get('time_limit', '')

    print(f"[DEBUG] endpoint_quizzes received {len(quizzes)} quizzes for course {course_id}")
    print(f"[DEBUG] Processing quiz {quizzes}")
    quiz_repo.upsert(str(quiz_id), title, time_limit, acc_type, quiz_type, str(course_id))
    quiz_repo.link_to_course(str(course_id), str(quiz_id))

    logger.info(f"Stored quiz {quiz_id}: {title} ({acc_type}) in course {course_id}")
    return
