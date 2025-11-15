import logging
import utils.dataframe_utils as dataframe_utils
import asyncio
import controller.process_input as process_input
from api.client import get_data

from db.repositories.term_repo import TermRepository
from db.repositories.course_repo import CourseRepository
from db.repositories.user_repo import UserRepository
from db.repositories.quiz_repo import QuizRepository
from db.repositories.submission_repo import SubmissionRepository
from db.repositories.question_repo import QuestionRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# Core entrypoint
# -----------------------------------------------------------
def generate_report(entry_vars):

    # def norm(v):
    #     return v.strip() if v and v.strip() != "" else None

    try:
        # values = {k: (norm(var.get()) if var.get() else None) for k, var in entry_vars.items()}

        # term_name = values.get("Term Name")
        # course_search = values.get("Course (ID / SIS ID / Code)")
        # student_search = values.get("Student (Name / SIS ID / Login)")
        # quiz_name = values.get("Quiz Name")
        # accom_type = accom_type_var.get()
        # quiz_type = quiz_type_var.get()
        # date_filter = date_filter_var.get()

        term_name = None#'Fall 2025'
        course_search = 'THE-115-OL-A'#'MTH-156-OL-A'
        quiz_name = 'Decalogue'#'Exam #2'
        student_search = '2635745'
        accom_type = 'all'
        quiz_type = 'both'#'new'
        date_filter = 'both'
        # clear_cache = True

        #No term -> good, course not limited by user
        #No quiz -> good
        #No course -> no course, no quiz
        #No user -> no user

        input_data = [
            term_name,
            course_search,
            quiz_name,
            student_search,
            accom_type,
            quiz_type,
            date_filter
        ]

        normalized_input = process_input.normalize_input(input_data)
        print(f'Normalized Input: {normalized_input}')
        populate_db(normalized_input)

        get_db()


        # logger.info("Building results DataFrame")
        # logger.info(f'Len cleaned input: {len(cleaned_input)}')
        # logger.info("Creating results DataFrame")
        # results_df = dataframe_utils.create_df(course_ids=cleaned_input[1], quiz_ids=cleaned_input[2], 
        #                                         user_ids=cleaned_input[3], accom_type=cleaned_input[4],
        #                                         quiz_type=cleaned_input[5], date_filter=cleaned_input[6])
        
        
    except Exception as e:
        logger.exception("Error in generate_report: %s", e)

def populate_db(input):
    get_data('term', term_id=input[0])
    get_data('courses', term_id=input[0])
    if input[1]:
        for course_id in input[1]:
            get_data('course', course_id=course_id)
            get_data('course_users', course_id=course_id)
            get_data('c_quizzes', course_id=course_id, search_param=None)
            get_data('n_quizzes', course_id=course_id, search_param=None)
            if input[3]:
                for user_id in input[3]:
                    get_data('enrollments', user_id=user_id, term_id=input[0])
            else:
                print('No users')
            if input[2]:
                for quiz_id in input[2]:
                    get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)
                    get_data('n_quiz', course_id=course_id, quiz_id=quiz_id)
                    get_data('c_quiz_submissions', course_id=course_id, quiz_id=quiz_id)
                    get_data('n_quiz_submissions', course_id=course_id, quiz_id=quiz_id)
                    get_data('n_quiz_items', course_id=course_id, quiz_id=quiz_id)
            else:
                print('No quizzes')
    else:
        print('No courses')


def get_db():
    term_db = TermRepository()
    course_db = CourseRepository()
    user_db = UserRepository()
    quiz_db = QuizRepository()
    # submission_db = SubmissionRepository()
    # question_db = QuestionRepository()

    term_data = term_db.list_all()
    course_data = course_db.list_all()
    user_data = user_db.list_all()
    quiz_data = quiz_db.list_all()
    # submission_data = submission_db.list_all()
    # question_data = question_db.list_all()

    print(f'TERM DATA: {term_data}')
    print(f'COURSE DATA: {course_data}')
    print(f'USER DATA: {user_data}')
    print(f'QUIZ DATA: {quiz_data}')
    # print(f'SUBMISSION DATA: {submission_data}')
    # print(f'QUESTION DATA: {question_data}')