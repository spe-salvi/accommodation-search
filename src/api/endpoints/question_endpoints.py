import logging
from db.repositories.question_repo import QuestionRepository

logger = logging.getLogger(__name__)
repo = QuestionRepository()

def endpoint_items(data, **kwargs):
    """
    Persist question metadata for a quiz.
    Canvas returns quiz item data (e.g. for New Quizzes API).
    We’ll extract essay questions and whether spell_check is enabled.
    """
    course_id = kwargs.get('course_id')
    quiz_id = kwargs.get('quiz_id')
    if not data or not (course_id and quiz_id):
        logger.error("endpoint_items: Invalid input; skipping question persistence.")
        return

    cid = str(course_id)
    qid = str(quiz_id)
    count = 0

    for item in data:
        try:
            item_id = str(item.get("id"))
            entry = item.get("entry", {})
            q_type = entry.get("interaction_type_slug", "unknown")

            # We only track essay questions
            if q_type != "essay":
                continue

            # Pull spell_check flag (from interaction_data if available)
            spell_check = entry.get("interaction_data", {}).get("spell_check", False)
            repo.upsert(cid, qid, item_id, q_type, spell_check)
            count += 1

        except Exception as e:
            logger.error(f"Error processing quiz item: {e}")

    logger.info(f"Stored {count} essay questions for quiz {qid} in course {cid}.")
