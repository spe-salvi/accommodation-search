import logging
from api.client import get_data
from api.endpoints.quiz_endpoints import quiz_repo
from api.endpoints.course_endpoints import course_repo

logger = logging.getLogger(__name__)


async def get_quiz_ids_from_courses(course_ids: list[str], quiz_name: str, quiz_type="both") -> list[str]:
    if not course_ids:
        logger.info("No course IDs provided; returning empty list.")
        return []

    quiz_ids = set()

    # 1️⃣ Fetch and persist all quizzes first
    for cid in course_ids:
        logger.info(f"Fetching quizzes for course {cid} (type={quiz_type})")
        if quiz_type in ("classic", "both"):
            get_data("c_quizzes", course_id=cid, search_param=quiz_name, quiz_type='classic')
            logger.info(f"Classic quizzes fetched for course {cid}")
            print(f'DB Query Classic Quiz: {course_repo.get_quizzes_for_course(cid)}')
        if quiz_type in ("new", "both"):
            get_data("n_quizzes", course_id=cid, search_param=quiz_name, quiz_type='new')
            logger.info(f"New quizzes fetched for course {cid}")
            print(f'DB Query New Quiz: {course_repo.get_quizzes_for_course(cid)}')

    # 2️⃣ Now read back once everything’s persisted
    all_quizzes = []
    for cid in course_ids:
        all_quizzes.extend(course_repo.get_quizzes_for_course(cid))
        print(f'DB Query Both Quiz: {course_repo.get_quizzes_for_course(cid)}')

    print(f'QUIZZES: {all_quizzes}')

    logger.info(f"Resolved {len(quiz_ids)} quiz(es) across {len(course_ids)} course(s) for '{quiz_name}'.")
    return all_quizzes

