import asyncio
import logging
from utils.retry_request import retry_get
import utils.pipeline as pipeline
import config.config as config
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# input_data = [term_id, course_id, quiz_id, user_id, accom_type, quiz_type, date_filter]

async def _fetch_ids_via_pipeline(term_name, course_search=None, student_search=None, quiz_name=None, quiz_type='both'):
    # Build the context (pipeline will resolve term -> users/courses -> quizzes)
    ctx = await pipeline.build_accommodation_context(
        term_input=term_name,
        course_input=course_search,
        user_input=student_search,
        quiz_name=quiz_name,
        quiz_type=quiz_type
    )
    # build_accommodation_context already runs resolve_dependencies internally
    return ctx


def normalize_input(input_data: list):
    """
    Returns:
        term_id, course_ids, quiz_ids, user_ids, accom_type, quiz_type, date_filter
    """
    term_name, course_search, quiz_name, student_search, accom_type, quiz_type, date_filter = input_data

    # Run the async DAG and wait for results
    ctx = asyncio.run(
        _fetch_ids_via_pipeline(
            term_name=term_name,
            course_search=course_search,
            student_search=student_search,
            quiz_name=quiz_name,
            quiz_type=quiz_type
        )
    )

    return (
        ctx.term_id,
        ctx.course_ids,
        ctx.quiz_ids,
        ctx.user_ids,
        accom_type,
        quiz_type,
        date_filter
    )