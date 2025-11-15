import logging
from api.client import get_data
from api.endpoints.user_endpoints import user_repo
from api.endpoints.course_endpoints import course_repo

logger = logging.getLogger(__name__)


def get_user_ids_by_search(term_id: str, user_input: str):
    """
    Fetch user IDs matching a partial name, SIS ID, or email.
    Always calls the Canvas API first to normalize results,
    writes to SQLite, then filters locally (and by term if provided).
    """
    if not user_input:
        return []

    logger.info(f"Fetching Canvas users for search='{user_input}', term={term_id or 'none'}")

    # 1. Always call Canvas API for this user search
    get_data('users', term_id=term_id, search_param=user_input)

    # 2. Read back from DB
    users = user_repo.list_all()
    user_input = user_input.lower()
    matches = [
        u["user_id"] for u in users
        if user_input in str(u.get("name", "")).lower()
        or user_input in str(u.get("sis_id", "")).lower()
        or user_input in str(u.get("email", "")).lower()
    ]

    if not term_id:
        logger.info(f"Resolved {len(matches)} user(s) for search '{user_input}' (no term filter).")
        print(f'User Matches: {matches}')
        return matches

    # 3. Filter by users enrolled in this term’s courses
    course_ids = [
        c["course_id"]
        for c in course_repo.list_all()
        if str(c.get("term_id")) == str(term_id)
    ]

    term_user_ids = {
        u["user_id"]
        for cid in course_ids
        for u in user_repo.get_users_by_course(cid)
    }

    filtered = [u for u in matches if u in term_user_ids]
    logger.info(f"Resolved {len(filtered)} user(s) in term {term_id} for search '{user_input}'.")

    if not term_user_ids:
        logger.info("No term-user links found; returning all user matches.")
        print(f'User Matches (2): {matches}')
        return matches
        
    print(f'User Filtered: {filtered}')
    return filtered


def get_user_ids_by_courses(course_ids):
    """
    Return all user IDs across provided course IDs.
    Calls Canvas API to fetch course users (if not cached),
    writes results to SQLite, and returns canonical user_ids.
    """
    print(f'------------------------------------------------------------------\n get_user_ids_by_courses INPUT: {course_ids}')
    results = set()

    for cid in course_ids:
        logger.info(f"Fetching Canvas users for course {cid}")
        get_data('course_users', course_id=cid)  # API fetch + DB write

        # Pull from DB after update
        print(f'XXXXXXXXXXXXXXXXXXXXX {course_repo.get_users_for_course(cid)} XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        for u in course_repo.get_users_for_course(cid):
            
            results.add(u)

    logger.info(f"Resolved {len(results)} unique user(s) across {len(course_ids)} courses.")

    print(f'Users By Courses Results: {list(results)}')
    return list(results)
