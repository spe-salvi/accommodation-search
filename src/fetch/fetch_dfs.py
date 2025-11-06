import pandas as pd
import logging

from db.repositories.term_repo import TermRepository
from db.repositories.course_repo import CourseRepository
from db.repositories.user_repo import UserRepository
from db.repositories.quiz_repo import QuizRepository
from db.repositories.submission_repo import SubmissionRepository
from db.repositories.question_repo import QuestionRepository

logger = logging.getLogger(__name__)

def fetch_term_df():
    """Return all terms as DataFrame."""
    repo = TermRepository()
    data = repo.list_terms()
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={"term_id": "Term ID", "term_name": "Term Name"}, inplace=True)
        df["Course ID Term"] = df["course_ids"].apply(lambda c: c if isinstance(c, list) else [])
        df = df.explode("Course ID Term")
    else:
        df = pd.DataFrame(columns=["Term ID", "Term Name", "Course ID Term"])
    return df

def fetch_course_df():
    """Return all courses as DataFrame."""
    repo = CourseRepository()
    data = repo.list_courses()
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={
            "course_id": "Course ID Course",
            "name": "Course Name",
            "code": "Course Code",
            "term_id": "Term ID",
        }, inplace=True)
    else:
        df = pd.DataFrame(columns=["Course ID Course", "Course Name", "Course Code", "Term ID"])
    return df

def fetch_user_df():
    """Return all users as DataFrame."""
    repo = UserRepository()
    data = repo.list_all()
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={
            "user_id": "User ID",
            "name": "Sortable Name",
            "sis_id": "SIS User ID",
            "email": "Email"
        }, inplace=True)
        # Build mapping table for course relationships
        course_links = []
        for u in data:
            links = repo.get_user_courses(u["user_id"])
            for cid in links:
                course_links.append({"User ID": u["user_id"], "Course ID User": cid})
        link_df = pd.DataFrame(course_links)
        if not link_df.empty:
            df = df.merge(link_df, on="User ID", how="left")
    else:
        df = pd.DataFrame(columns=["User ID", "Sortable Name", "SIS User ID", "Email", "Course ID User"])
    return df

def fetch_quiz_df():
    """Return all quizzes as DataFrame."""
    repo = QuizRepository()
    data = repo.list_all()
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={
            "quiz_id": "Quiz ID",
            "course_id": "Course ID Quiz",
            "title": "Title",
            "quiz_type": "Type",
        }, inplace=True)
    else:
        df = pd.DataFrame(columns=["Quiz ID", "Course ID Quiz", "Title", "Type"])
    return df

def fetch_submission_df():
    """Return all submissions as DataFrame."""
    repo = SubmissionRepository()
    data = repo.list_all()
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={
            "submission_id": "Submission ID",
            "user_id": "User ID Sub",
            "course_id": "Course ID Sub",
            "quiz_id": "Quiz ID Sub",
            "extra_time": "Extra Time",
            "extra_attempts": "Extra Attempts",
            "due_status": "Date"
        }, inplace=True)
    else:
        df = pd.DataFrame(columns=[
            "Submission ID", "User ID Sub", "Course ID Sub", "Quiz ID Sub",
            "Extra Time", "Extra Attempts", "Date"
        ])
    return df

def fetch_question_df():
    """Return all quiz questions as DataFrame."""
    repo = QuestionRepository()
    data = repo.list_all()
    df = pd.DataFrame(data)
    if not df.empty:
        df.rename(columns={
            "question_id": "Item ID Ques",
            "quiz_id": "Quiz ID Ques",
            "course_id": "Course ID Ques",
            "spell_check": "Spell Check",
        }, inplace=True)
    else:
        df = pd.DataFrame(columns=["Item ID Ques", "Quiz ID Ques", "Course ID Ques", "Spell Check"])
    return df
