import re
import logging
import config as config
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

    print(f'Term Input: {term_id}')

    return str(term_id) if term_id else None