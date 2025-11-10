import re
import logging
import config as config
from db.repositories.term_repo import TermRepository

logger = logging.getLogger(__name__)
term_repo = TermRepository()

def endpoint_term(data, term_id=None, **kwargs):
    """
    Processes a term API response and persists it in SQLite.
    Expected data shape: { 'id': 116, 'name': 'Fall 2025', ... }
    """
    if not data:
        logger.warning("endpoint_term called with empty data.")
        return
    
    for term in data:
        if not term_id:
            if 'id' not in term:
                logging.error(f"endpoint_term: The 'id' key is missing in the provided data. {term_id}")
                return
            term_id = str(term.get('id'))

        name = term.get('name', '')

    if not term_id or not name:
        logger.warning("Invalid term data, missing id or name.")
        return

    term_repo.upsert(term_id, name)
    logger.info(f"Persisted term {term_id}: {name}")
    return


def endpoint_courses(data, term_id=None, **kwargs):
    """Link courses to a term."""
    if not data:
        logger.info("No course data to link.")
        return []

    linked_ids = []
    for course in data:
        cid = str(course.get("id"))
        tid = str(course.get("enrollment_term_id"))
        if not cid or not tid:
            continue
        term_repo.link_course(tid, cid)
        linked_ids.append(cid)

    logger.info(f"Linked {len(linked_ids)} courses to term {term_id or tid}")
    return
