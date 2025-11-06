import asyncio
from utils.retry_request import retry_get
import config as config
import logging

logger = logging.getLogger(__name__)

'''

NONE

'''
async def get_user_ids_by_search(term_id: str, student_search_term: str) -> list[str]:
    """Return user IDs matching the search term."""
    def fetch():
        url = f"{config.API_URL}/v1{config.FUS_ACCOUNT}/users"
        '''
        None
        '''
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

'''

NONE

'''
async def get_user_ids_by_courses(course_ids: list[str]) -> list[str]:
    """Return all unique user IDs enrolled in the provided courses."""
    if not course_ids:
        logger.info("No course IDs provided; returning empty list")
        return []

    async def fetch_users(cid):
        def fetch():
            url = f"{config.API_URL}/v1/courses/{cid}/users"
            '''
            None
            '''
            data = retry_get(url, {})
            return [str(u["id"]) for u in data if "id" in u]
        return await asyncio.get_running_loop().run_in_executor(None, fetch)

    results = await asyncio.gather(*(fetch_users(cid) for cid in course_ids))
    user_ids = list({uid for sub in results for uid in sub})
    logger.info(f"Fetched {len(user_ids)} unique user(s) from {len(course_ids)} course(s)")
    return user_ids

### Make user cache
# user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': (course_id, course_id, course_id)}, ...}
def endpoint_enrollments(data=None, term_id=None, course_id=None, quiz_id=None, user_id=None):
    # logger.info("endpoint_enrollments called")

    if not data or not user_id:
        # logger.error("endpoint_enrollments: Invalid input provided; skipping user cache update.")
        return

    with cache_lock:
        user_cache = cache_manager.load_user_cache()
        uid = str(user_id)

        u_cache = user_cache.setdefault(uid, {})
        for key, default in [("sortable_name", ""), ("sis_id", ""), ("email", ""), ("courses", [])]:
            u_cache.setdefault(key, default)

        enrollments = data if isinstance(data, list) else [data]
        for enrollment in enrollments:
            cid = str(enrollment.get('course_id', ''))
            if cid and cid not in u_cache["courses"]:
                u_cache["courses"].append(cid)

        user_cache[uid] = u_cache
        cache_manager.save_user_cache()

    # logger.info(f"User cache after enrollments endpoint: {len(user_cache)} users")