# import pytest    
# import pandas as pd
# from unittest.mock import patch
# from utils.dataframe_utils import create_df
# import utils.dataframe_utils as df_utils

# def test_create_df_merges_all_getters_correctly():
#     # Setup global variables expected by create_df
#     df_utils.course_id_df = ["C1"]
#     df_utils.quiz_id_df = ["Q1"]
#     df_utils.user_id_df = ["U1"]
#     df_utils.accom_type_df = ["time"]
#     df_utils.accom_date_df = ["2025-08-06"]
#     df_utils.quiz_type_df = ["classic"]

#     # Mocked getter return values
#     mock_course_df = pd.DataFrame({
#         "Course Code": ["BIO101"],
#         "Course Name": ["Biology"],
#         "User IDs": [["U1"]],
#         "Quiz IDs": [["Q1"]]
#     }, index=["C1"])

#     mock_user_df = pd.DataFrame({
#         "Sortable Name": ["Jane Student"],
#         "SIS User ID": ["S123"],
#         "Email": ["jane@student.edu"],
#         "Course IDs": [["C1"]]
#     }, index=["U1"])

#     mock_quiz_df = pd.DataFrame({
#         "Title": ["Final Exam"],
#         "Type": ["classic"],
#         "Course ID": ["C1"]
#     }, index=["Q1"])

#     mock_submission_df = pd.DataFrame([{
#         "User ID": "U1",
#         "Course ID": "C1",
#         "Quiz ID": "Q1",
#         "Extra Time": 30,
#         "Extra Attempts": 1,
#         "Date": "2025-08-06"
#     }])

#     with patch("utils.getters.get_course_df", return_value=mock_course_df), \
#          patch("utils.getters.get_user_df", return_value=mock_user_df), \
#          patch("utils.getters.get_quiz_df", return_value=mock_quiz_df), \
#          patch("utils.getters.get_submission_df", return_value=mock_submission_df):

#         df = create_df()

#     # ✅ Assertions
#     assert not df.empty
#     assert df.shape[0] == 1
#     assert df.loc[0, "Course Code"] == "BIO101"
#     assert df.loc[0, "Sortable Name"] == "Jane Student"
#     assert df.loc[0, "Title"] == "Final Exam"
#     assert df.loc[0, "Extra Time"] == 30
#     assert df.loc[0, "Extra Attempts"] == 1
