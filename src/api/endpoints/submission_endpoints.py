import logging
from db.repositories.submission_repo import SubmissionRepository

logger = logging.getLogger(__name__)
repo = SubmissionRepository()

def endpoint_submissions(data, term_id=None, course_id=None, quiz_id=None, user_id=None):
    """
    Store all submissions for a given quiz into the database.
    """
    if not data or not course_id or not quiz_id:
        logger.warning("endpoint_submissions called with missing course_id or quiz_id.")
        return

    submissions = []
    if isinstance(data, dict) and "quiz_submissions" in data:
        submissions = data["quiz_submissions"]
    elif isinstance(data, list):
        submissions = data
    else:
        logger.warning("endpoint_submissions: Unrecognized data format.")
        return

    for sub in submissions:
        uid = sub.get("user_id")
        if not uid:
            continue

        # Determine submission date/status
        workflow = sub.get("workflow_state", "")
        if workflow in ["complete", "graded"]:
            date = "past"
        elif workflow in ["settings_only", "unsubmitted"]:
            date = "future"
        else:
            date = ""

        repo.upsert({
            "user_id": uid,
            "course_id": course_id,
            "quiz_id": quiz_id,
            "extra_time": sub.get("extra_time", 0),
            "extra_attempts": sub.get("extra_attempts", 0),
            "date": date
        })

    logger.info(f"Stored submissions for course {course_id}, quiz {quiz_id} ({len(submissions)} records).")


def is_accommodated(course_id, quiz_id, user_id, accom_type):
    """
    Check if a submission record shows accommodation for time or attempts.
    """
    record = repo.get_submission(str(user_id), str(course_id), str(quiz_id))
    if not record:
        logger.warning(f"No submission record found for user={user_id}, course={course_id}, quiz={quiz_id}")
        return (False, "NA")

    extra_time = record["extra_time"]
    extra_attempts = record["extra_attempts"]
    date = record["date"]

    if accom_type == "time" and extra_time and extra_time > 0:
        return (True, date)

    if accom_type == "attempts" and extra_attempts and extra_attempts > 0:
        return (True, date)

    return (False, "NA")
