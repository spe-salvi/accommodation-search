import logging
import process_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_report(entry_vars):
    def norm(v):
        return v.strip() if v and v.strip() != "" else None

    try:
        values = {k: (norm(var.get()) if var.get() else None) for k, var in entry_vars.items()}

        # # Build the input list for normalize_input
        # input_data = [
        #     values.get("Term Name"),
        #     values.get("Course (Name / SIS ID / Code)"),
        #     values.get("Quiz Name"),
        #     values.get("Student (Name / SIS ID / Login)"),
        #     accom_type,
        #     quiz_type,
        #     date_filter
        # ]


        term_name = 'Fall 2025'
        course_search = 'THE-115-OL-A'#'MTH-156-OL-A'
        quiz_name = 'Decalogue'#'Exam #2'
        student_search = ''#'2631150'#'2635745'
        accom_type = 'all'
        quiz_type = 'both'#'new'
        date_filter = 'both'
        clear_cache = True

        # Optionally clear all caches before populating
        # if clear_cache:
        #     import utils.cache_manager as cache_manager
        #     logger.info("Clearing all caches")
        #     cache_manager.clear_all_caches()

        input_data = [
            term_name,
            course_search,
            quiz_name,
            student_search,
            accom_type,
            quiz_type,
            date_filter
        ]

        normalized_input = await process_input.normalize_input(input_data)

        logger.info("Calling populate_cache")
        
        populate_cache.call_populate(term_ids=normalized_input[0], course_ids=normalized_input[1],
                                        quiz_ids=normalized_input[2], user_ids=normalized_input[3],
                                        accom_type=normalized_input[4])
        logger.info("Building results DataFrame")
        logger.info(f'Len cleaned input: {len(normalized_input)}')
        logger.info("Creating results DataFrame")
        results_df = dataframe_utils.create_df(course_ids=normalized_input[1], quiz_ids=normalized_input[2], 
                                                user_ids=normalized_input[3], accom_type=normalized_input[4],
                                                quiz_type=normalized_input[5], date_filter=normalized_input[6])

        return results_df
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return