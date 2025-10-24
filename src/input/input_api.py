<<<<<<< HEAD
import config.config as config
import re
import logging

logging.basicConfig(level=logging.INFO)
=======
import asyncio
import logging
import re
from utils.retry_request import retry_get
import config.config as config

>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
logger = logging.getLogger(__name__)

# =====================================================
# TERM UTILITIES
# =====================================================

def get_term_id(term_name: str) -> str | None:
    """
    Convert a user-friendly term name (e.g. 'Fall 2025') into a Canvas term ID.
    """
    if not term_name:
        return None

    lookup = {}
<<<<<<< HEAD
    logger.info(f'Term Name: {term_name}')
=======
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
    for code, full in config.TERMS.items():
        season, year = full.split()
        year = int(year)
        season_variants = {season.lower(), season[:2].lower()}
        year_variants = {str(year), str(year % 100)}
        for s in season_variants:
            for y in year_variants:
                lookup[f"{s} {y}"] = code

<<<<<<< HEAD
    norm = str(re.sub(r"\s+", " ", term_name.strip().lower()))
    return lookup.get(norm)
=======
    norm = re.sub(r"\s+", " ", term_name.strip().lower())
    return str(lookup.get(norm))


# -----------------------------
# COURSE HELPERS
# -----------------------------
async def get_course_ids_by_term_and_search(term_id: str, course_search_term: str) -> list[str]:
    """Return Canvas course IDs matching search term (and optional term ID)."""
    def fetch():
        url = f"{config.API_URL}/v1{config.FUS_ACCOUNT}/courses"
        params = {}
        if course_search_term:
            params["search_term"] = course_search_term
        if term_id:
            params["enrollment_term_id"] = term_id
        data = retry_get(url, params)
        course_ids = [str(c["id"]) for c in data if "id" in c]
        logger.info(f"Found {len(course_ids)} course(s) for term {term_id} with search '{course_search_term}'")
        return course_ids

    return await asyncio.get_running_loop().run_in_executor(None, fetch)


async def get_course_ids_by_users(user_ids: list[str], term_id: str = None) -> list[str]:
    """Return unique course IDs for given users within an optional term."""
    if not user_ids:
        logger.info("No user IDs provided; returning empty list")
        return []

    logger.info(f"Fetching courses for {len(user_ids)} users with term_id={term_id}")
    
    async def fetch_enrollments(uid):
        def fetch():
            url = f"{config.API_URL}/v1/users/{uid}/enrollments"
            params = {
                "type[]": ["StudentEnrollment"],  # Only get student enrollments
                "state[]": ["active", "completed"]  # Both active and completed enrollments
            }
            if term_id:
                params["enrollment_term_id"] = term_id
            
            logger.info(f"Fetching enrollments for user {uid} with params: {params}")
            data = retry_get(url, params)
            
            if data:
                # Log the raw enrollment data for debugging
                logger.debug(f"Raw enrollment data for user {uid}: {data[:2]}")  # Log first 2 enrollments
                course_ids = [str(e["course_id"]) for e in data if "course_id" in e]
                logger.info(f"Found {len(course_ids)} courses for user {uid} in term {term_id}")
                return course_ids
            else:
                logger.warning(f"No enrollment data returned for user {uid}")
                return []
                
        return await asyncio.get_running_loop().run_in_executor(None, fetch)

    results = await asyncio.gather(*(fetch_enrollments(u) for u in user_ids))
    course_ids = list({cid for sub in results for cid in sub})
    logger.info(f"Aggregated {len(course_ids)} unique course(s) across {len(user_ids)} user(s)")
    
    if not course_ids:
        logger.warning("No courses found for any users - this might indicate an API or filtering issue")
    
    return course_ids


# -----------------------------
# USER HELPERS
# -----------------------------
async def get_user_ids_by_search(term_id: str, student_search_term: str) -> list[str]:
    """Return user IDs matching the search term."""
    def fetch():
        url = f"{config.API_URL}/v1{config.FUS_ACCOUNT}/users"
        params = {
            'search_term': student_search_term
        }
        if term_id:
            params['enrollment_term_id'] = term_id
        data = retry_get(url, params)
        user_ids = [str(u["id"]) for u in data if "id" in u]
        logger.info(f"Found {len(user_ids)} user(s) for search '{student_search_term}'")
        return user_ids

    return await asyncio.get_running_loop().run_in_executor(None, fetch)


async def get_user_ids_by_courses(course_ids: list[str]) -> list[str]:
    """Return all unique user IDs enrolled in the provided courses."""
    if not course_ids:
        logger.info("No course IDs provided; returning empty list")
        return []

    async def fetch_users(cid):
        def fetch():
            url = f"{config.API_URL}/v1/courses/{cid}/users"
            data = retry_get(url, {})
            return [str(u["id"]) for u in data if "id" in u]
        return await asyncio.get_running_loop().run_in_executor(None, fetch)

    results = await asyncio.gather(*(fetch_users(cid) for cid in course_ids))
    user_ids = list({uid for sub in results for uid in sub})
    logger.info(f"Fetched {len(user_ids)} unique user(s) from {len(course_ids)} course(s)")
    return user_ids


# -----------------------------
# QUIZ HELPERS
# -----------------------------
async def get_quiz_ids_from_courses(course_ids: list[str], quiz_name: str, quiz_type="both") -> list[str]:
    """Return quiz/assignment IDs that match quiz_name across courses."""
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
                        quiz_ids.append(str(q.get("id")))

            if quiz_ids:
                logger.info(f"Course {cid}: matched {len(quiz_ids)} quiz(es) for '{quiz_name}'")
            return quiz_ids

        return await asyncio.get_running_loop().run_in_executor(None, fetch)

    results = await asyncio.gather(*(fetch_quizzes(cid) for cid in course_ids))
    quiz_ids = list({qid for sub in results for qid in sub})
    logger.info(f"Resolved {len(quiz_ids)} total quiz(es) named '{quiz_name}' across {len(course_ids)} course(s)")
    return quiz_ids
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
