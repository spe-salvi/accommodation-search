# import pytest
# import pandas as pd
# from unittest.mock import patch
# import utils.getters as getters

# def test_get_term_df():
#     fake_term_cache = {
#         "2024": {"name": "Spring 2024", "courses": ["101", "102"]},
#         "2025": {"name": "Fall 2025", "courses": ["201"]}
#     }
#     with patch("utils.getters.cache_manager.load_term_cache", return_value=fake_term_cache):
#         df = getters.get_term_df()
#         assert isinstance(df, pd.DataFrame)
#         assert list(df.columns) == ["Term Name", "Course IDs"]
#         assert df.loc["2024", "Term Name"] == "Spring 2024"
#         assert df.loc["2025", "Course IDs"] == ["201"]

# def test_get_course_df():
#     fake_course_cache = {
#         "101": {
#             "code": "CS101", "name": "Intro to CS", "term": "2024",
#             "users": ["u1", "u2"], "quizzes": ["q1", "q2"]
#         }
#     }
#     with patch("utils.getters.cache_manager.load_course_cache", return_value=fake_course_cache):
#         df = getters.get_course_df()
#         assert list(df.columns) == ["Course Code", "Course Name", "User IDs", "Quiz IDs"]
#         assert df.loc["101", "Course Name"] == "Intro to CS"
#         assert "q1" in df.loc["101", "Quiz IDs"]

# def test_get_user_df():
#     fake_user_cache = {
#         "u1": {
#             "name": "John Doe", "sis_id": "S123", "email": "john@example.com", "courses": ["101"]
#         }
#     }
#     with patch("utils.getters.cache_manager.load_user_cache", return_value=fake_user_cache):
#         df = getters.get_user_df()
#         assert list(df.columns) == ["Sortable Name", "SIS User ID", "Email", "Course IDs"]
#         assert df.loc["u1", "Email"] == "john@example.com"

# def test_get_quiz_df():
#     fake_quiz_cache = {
#         "q1": {"title": "Quiz 1", "type": "classic", "course_id": "101"},
#         "q2": {"title": "Quiz 2", "type": "new", "course_id": "102"}
#     }
#     with patch("utils.getters.api_endpoints.quiz_cache", fake_quiz_cache):
#         df = getters.get_quiz_df()
#         assert list(df.columns) == ["Title", "Type", "Course ID"]
#         assert df.loc["q1", "Type"] == "classic"

# def test_get_submission_df():
#     fake_submission_cache = {
#         "u1": {
#             "c1": {
#                 "q1": {
#                     "extra_time": 20,
#                     "extra_attempts": 1,
#                     "date": "past"
#                 }
#             }
#         }
#     }

#     with patch("utils.getters.api_endpoints.submission_cache", fake_submission_cache):
#         df = getters.get_submission_df()

#         assert isinstance(df, pd.DataFrame)
#         assert list(df.columns) == ["User ID", "Course ID", "Quiz ID", "Extra Time", "Extra Attempts", "Date"]
#         assert len(df) == 1
#         row = df.iloc[0]
#         assert row["User ID"] == "u1"
#         assert row["Course ID"] == "c1"
#         assert row["Quiz ID"] == "q1"
#         assert row["Extra Time"] == 20
#         assert row["Extra Attempts"] == 1
#         assert row["Date"] == "past"