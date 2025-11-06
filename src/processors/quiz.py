import logging
import asyncio
from utils.retry_request import retry_get
import config as config
from db.repositories.quiz_repo import QuizRepository

logger = logging.getLogger(__name__)
quiz_repo = QuizRepository()

async def get_quiz_ids_from_courses(course_ids: list[str], quiz_name: str, quiz_type="both") -> list[str]:
    """
    Return quiz IDs that match quiz_name across multiple courses,
    and persist them in the quiz_store.
    """
    if not quiz_name or not course_ids:
        logger.info("Missing quiz name or course IDs; returning empty list")
        return []

    async def fetch_quizzes(cid):
        def fetch():
            quiz_ids = []
            quiz_name_norm = quiz_name.strip().lower()
            urls = []

            if quiz_type in ("classic", "both"):
                urls.append(f"{config.API_URL}/v1/courses/{cid}/quizzes?search_term={quiz_name}")

            if quiz_type in ("new", "both"):
                urls.append(f"{config.API_URL}/v1/courses/{cid}/assignments?search_term={quiz_name}")

            for url in urls:
                data = retry_get(url, {})
                for q in data:
                    name = q.get("name", "").strip().lower()
                    submission_types = q.get("submission_types", [])
                    is_new = "assignments" in url

                    if quiz_name_norm in name and (
                        not is_new or ("external_tool" in submission_types or "online_quiz" in submission_types)
                    ):
                        quiz_id = str(q.get("id"))
                        qtype = "new" if is_new else "classic"
                        quiz_repo.upsert(quiz_id, q.get("name", ""), qtype, str(cid))
                        quiz_repo.link_to_course(str(cid), quiz_id)
                        quiz_ids.append(quiz_id)

            if quiz_ids:
                logger.info(f"Course {cid}: found {len(quiz_ids)} quiz(es) for '{quiz_name}'")
            return quiz_ids

        return await asyncio.get_running_loop().run_in_executor(None, fetch)

    results = await asyncio.gather(*(fetch_quizzes(cid) for cid in course_ids))
    quiz_ids = list({qid for sub in results for qid in sub})
    logger.info(f"Resolved {len(quiz_ids)} total quizzes named '{quiz_name}'")
    return quiz_ids


def endpoint_quiz(data, term_id=None, course_id=None, quiz_id=None, user_id=None, acc_type=''):
    """
    Processes a single quiz response and saves it to the database.
    """
    if not data or not course_id or not quiz_id:
        logger.warning("endpoint_quiz: Missing required parameters.")
        return

    title = data.get('title', '')
    quiz_type = acc_type or 'classic'

    quiz_repo.upsert(str(quiz_id), title, quiz_type, str(course_id))
    quiz_repo.link_to_course(str(course_id), str(quiz_id))

    logger.info(f"Stored quiz {quiz_id}: {title} ({quiz_type}) in course {course_id}")
    return quiz_id
