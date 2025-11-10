import logging
from api.client import get_data
from db.repositories.quiz_repo import QuizRepository
from db.repositories.course_repo import CourseRepository

logger = logging.getLogger(__name__)
quiz_repo = QuizRepository()
course_repo = CourseRepository()


async def get_quiz_ids_from_courses(course_ids: list[str], quiz_name: str, quiz_type="both") -> list[str]:
    """
    Fetch quiz IDs matching quiz_name across the given courses.
    Always calls Canvas via get_data(), writes to SQLite through endpoint_quiz,
    and returns canonical quiz_ids from the local DB.

    quiz_type: "classic", "new", or "both"
    """
    if not course_ids:
        logger.info("No course IDs provided; returning empty list.")
        return []

    quiz_ids = set()
    quiz_name_lower = (quiz_name or "").strip().lower()

    for cid in course_ids:
        logger.info(f"Fetching quizzes for course {cid} (type={quiz_type})")

        # 1️⃣ Always hit Canvas to populate/update DB for this course
        if quiz_type in ("classic", "both"):
            get_data("c_quizzes", course_id=cid, search_param=quiz_name)
        if quiz_type in ("new", "both"):
            get_data("n_quizzes", course_id=cid, search_param=quiz_name)

        # 2️⃣ Read back from the DB
        quizzes = quiz_repo.list_all()
        for q in quizzes:
            if str(q.get("course_id")) != str(cid):
                continue
            title = str(q.get("title", "")).lower()
            if quiz_name_lower in title or not quiz_name_lower:
                quiz_ids.add(q["quiz_id"])
                quiz_repo.link_to_course(cid, q["quiz_id"])

    logger.info(f"Resolved {len(quiz_ids)} quiz(es) across {len(course_ids)} course(s) for '{quiz_name}'.")
    return list(quiz_ids)
