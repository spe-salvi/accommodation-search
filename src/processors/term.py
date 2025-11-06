import re
import logging
import config as config
from utils.retry_request import retry_get
from db.repositories.term_repo import TermRepository

logger = logging.getLogger(__name__)

term_repo = TermRepository()

def get_term_id(term_name: str) -> str | None:
    """Convert a user-friendly term name (e.g. 'Fall 2025') into a Canvas term ID."""
    if not term_name:
        return None

    lookup = {}
    for code, full in config.TERMS.items():
        season, year = full.split()
        year = int(year)
        season_variants = {season.lower(), season[:2].lower()}
        year_variants = {str(year), str(year % 100)}
        for s in season_variants:
            for y in year_variants:
                lookup[f"{s} {y}"] = code

    norm = re.sub(r"\s+", " ", term_name.strip().lower())
    term_id = lookup.get(norm)
    logger.info(f"Resolved '{term_name}' → term_id={term_id}")
    return str(term_id) if term_id else None


def endpoint_term(data, term_id=None, **kwargs):
    """
    Processes a term API response and persists it in SQLite.
    Expected data shape: { 'id': 116, 'name': 'Fall 2025', ... }
    """
    if not data:
        logger.warning("endpoint_term called with empty data.")
        return

    if not term_id:
        term_id = str(data.get('id'))

    name = data.get('name', '')
    if not term_id or not name:
        logger.warning("Invalid term data, missing id or name.")
        return

    term_repo.upsert(term_id, name)
    logger.info(f"Persisted term {term_id}: {name}")
    return term_id


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
    return linked_ids
