import logging
from controller.process_input import normalize_input
from api.client import get_data
import utils.dataframe_utils as dataframe_utils
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from utils import dataframe_utils
from api.client import CanvasClient
from controller.pipeline import resolve_pipeline
from db.database import Database
from db.repositories.course_repo import CourseRepository
from db.repositories.quiz_repo import QuizRepository
from db.repositories.user_repo import UserRepository
from db.repositories.submission_repo import SubmissionRepository
from db.repositories.term_repo import TermRepository

logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# Core entrypoint
# -----------------------------------------------------------

def generate_report(entry_vars):
    """
    Full report generation flow:
      1. Resolve user input into term, course, quiz, etc. IDs
      2. Sync (or confirm) data in SQLite cache
      3. Pull from the local DB
      4. Build the final DataFrame
    """
    try:
        logger.info("=== Starting report generation ===")

        # --- 1. Resolve user input to IDs via pipeline ---
        normalized_input = resolve_pipeline(entry_vars)
        if not normalized_input:
            logger.error("Pipeline returned no normalized input.")
            return None

        term_id, course_ids, user_ids, quiz_ids, accom_type, quiz_type, date_filter, clear_cache = normalized_input
        logger.info(
            f"Resolved inputs:\n  term_id={term_id}, courses={course_ids}, "
            f"users={user_ids}, quizzes={quiz_ids}, accom_type={accom_type}, "
            f"quiz_type={quiz_type}, date_filter={date_filter}, clear_cache={clear_cache}"
        )

        # --- 2. Ensure local database is populated/synced ---
        db = Database()
        client = CanvasClient()
        if clear_cache:
            logger.warning("Clear cache requested — reinitializing database.")
            db.recreate_schema()

        prepare_db(client, db, term_id, course_ids)

        # --- 3. Fetch data directly from local repos ---
        logger.info("Fetching from local repositories for dataframe assembly.")
        course_repo = CourseRepository(db)
        quiz_repo = QuizRepository(db)
        user_repo = UserRepository(db)
        submission_repo = SubmissionRepository(db)
        term_repo = TermRepository(db)

        courses = []
        quizzes = []
        users = []
        submissions = []

        # Term
        term = term_repo.get_by_id(str(term_id))
        logger.debug(f"Fetched term: {term}")

        # Courses
        for cid in course_ids:
            cset = course_repo.get_by_id(str(cid))
            courses.extend(cset if isinstance(cset, list) else [cset])
        logger.debug(f"Fetched {len(courses)} courses from DB.")

        # Quizzes
        for cid in course_ids:
            qset = quiz_repo.get_by_course_id(str(cid))
            quizzes.extend(qset)
        logger.debug(f"Fetched {len(quizzes)} quizzes from DB.")

        # Users
        for cid in course_ids:
            uset = user_repo.get_users_by_course(str(cid))
            users.extend(uset)
        logger.debug(f"Fetched {len(users)} users from DB.")

        # Submissions
        for cid in course_ids:
            sset = submission_repo.get_all_by_course(str(cid))
            submissions.extend(sset)
        logger.debug(f"Fetched {len(submissions)} submissions from DB.")

        if not any([courses, quizzes, users, submissions]):
            logger.warning("No data found in database for this query.")
            return pd.DataFrame()  # Return empty DataFrame

        # --- 4. Build the DataFrame ---
        results_df = dataframe_utils.create_df(
            term=term,
            courses=courses,
            quizzes=quizzes,
            users=users,
            submissions=submissions,
            accom_type=accom_type,
            quiz_type=quiz_type,
            date_filter=date_filter,
        )

        logger.info(f"✅ Report built successfully. {len(results_df)} rows generated.")
        return results_df

    except Exception as e:
        logger.exception(f"Error generating report: {e}")
        return None


# -----------------------------------------------------------
# Utility: Populate local DB (if missing data)
# -----------------------------------------------------------

def prepare_db(client: CanvasClient, db: Database, term_id: str, course_ids: list):
    """
    Ensures all required entities for the given term and courses exist in SQLite.
    Pulls from Canvas if missing.
    """
    logger.info("Preparing database from Canvas API as needed...")
    term_repo = TermRepository(db)
    course_repo = CourseRepository(db)
    quiz_repo = QuizRepository(db)
    user_repo = UserRepository(db)
    submission_repo = SubmissionRepository(db)

    # Term
    if not term_repo.exists(str(term_id)):
        logger.info(f"Fetching term {term_id} from Canvas API.")
        term_data = client.get_term(term_id)
        term_repo.upsert(term_data)

    # Courses
    for cid in course_ids:
        if not course_repo.exists(str(cid)):
            logger.info(f"Fetching course {cid} from Canvas API.")
            course_data = client.get_course(cid)
            course_repo.upsert(course_data)

        # Quizzes
        if not quiz_repo.exists_for_course(str(cid)):
            logger.info(f"Fetching quizzes for course {cid}.")
            quizzes = client.get_quizzes(cid)
            for quiz in quizzes:
                quiz_repo.upsert(quiz)

        # Users
        if not user_repo.exists_for_course(str(cid)):
            logger.info(f"Fetching users for course {cid}.")
            users = client.get_users(cid)
            for user in users:
                user_repo.upsert(user)
                user_repo.link_to_course(user['id'], cid)

        # Submissions
        if not submission_repo.exists_for_course(str(cid)):
            logger.info(f"Fetching submissions for course {cid}.")
            submissions = client.get_submissions(cid)
            for submission in submissions:
                submission_repo.upsert(submission)

    logger.info("Database preparation complete.")


