# import pytest
# from unittest.mock import patch
# import utils.cache_manager as cache_manager
# import utils.dataframe_utils as df_utils
# import api.api_endpoints as api_endpoints

# @pytest.fixture(autouse=True)
# def clear_global_lists():
#     # Clear global lists before each test to avoid contamination
#     df_utils.course_id_df.clear()
#     df_utils.quiz_id_df.clear()
#     df_utils.user_id_df.clear()
#     df_utils.accom_type_df.clear()
#     df_utils.accom_date_df.clear()
#     df_utils.quiz_type_df.clear()
#     yield
#     # Optional: clear after as well
#     df_utils.course_id_df.clear()
#     df_utils.quiz_id_df.clear()
#     df_utils.user_id_df.clear()
#     df_utils.accom_type_df.clear()
#     df_utils.accom_date_df.clear()
#     df_utils.quiz_type_df.clear()

# # def test_cache_to_df_integration():
# #     # Fake course cache with 1 course, 1 quiz, 1 user
# #     fake_course_cache = {
# #         "101": {
# #             "quizzes": ["501"],
# #             "users": ["u1"]
# #         }
# #     }

# #     # Patch load_course_cache to return our fake cache
# #     with patch.object(cache_manager, "load_course_cache", return_value=fake_course_cache), \
# #          patch("utils.dataframe_utils.is_accommodated", return_value=(True, "past")) as mock_is_accommodated:

# #         # Call the function under test
# #         df_utils.cache_to_df(accom_type="time", date_filter="past")

# #         # Assertions
# #         assert mock_is_accommodated.call_count > 0, "is_accommodated should be called at least once"
# #         assert "101" in df_utils.course_id_df, "Course ID should be appended to global dataframe lists"
# #         assert "501" in df_utils.quiz_id_df, "Quiz ID should be appended to global dataframe lists"
# #         assert "u1" in df_utils.user_id_df, "User ID should be appended to global dataframe lists"
# #         assert "time" in df_utils.accom_type_df, "Accommodation type should be recorded"
# #         assert "past" in df_utils.accom_date_df, "Accommodation date should match mocked return"
# #         assert len(df_utils.quiz_type_df) > 0, "Quiz type entries should be added"

# #         # Print the resulting DataFrame
# #         df = df_utils.create_df()
# #         print(df)

# #         # Validate dataframe shape
# #         assert not df.empty, "DataFrame should not be empty after processing"

# # def test_cache_to_df_is_acc_integration():
# #     import pytest
# # from unittest.mock import patch
# # import utils.cache_manager as cache_manager
# # import utils.dataframe_utils as df_utils
# # import api.api_endpoints as api_endpoints

# # @pytest.fixture(autouse=True)
# # def clear_global_lists():
# #     # Clear global lists before and after each test
# #     df_utils.course_id_df.clear()
# #     df_utils.quiz_id_df.clear()
# #     df_utils.user_id_df.clear()
# #     df_utils.accom_type_df.clear()
# #     df_utils.accom_date_df.clear()
# #     df_utils.quiz_type_df.clear()
# #     yield
# #     df_utils.course_id_df.clear()
# #     df_utils.quiz_id_df.clear()
# #     df_utils.user_id_df.clear()
# #     df_utils.accom_type_df.clear()
# #     df_utils.accom_date_df.clear()
# #     df_utils.quiz_type_df.clear()

# def test_cache_to_df_full_integration():
#     # Arrange: Fake course cache
#     fake_course_cache = {
#         "101": {
#             "quizzes": ["501"],
#             "users": ["u1"]
#         }
#     }

#     # Fake API caches
#     api_endpoints.submission_cache.clear()
#     api_endpoints.quiz_cache.clear()
#     api_endpoints.submission_cache["u1"] = {
#         "101": {
#             "501": {"extra_time": 20, "extra_attempts": 2, "date": "past"}
#         }
#     }
#     api_endpoints.quiz_cache["501"] = {"time_limit": 10}  # ensures time > time_limit * 2

#     # Patch: load_course_cache returns fake course cache, get_data does nothing
#     with patch.object(cache_manager, "load_course_cache", return_value=fake_course_cache), \
#          patch("quizzes.quizzes.get_data") as mock_get_data:

#         # Act: Run the integration
#         df_utils.cache_to_df(accom_type="time", date_filter="past")

#         # Assert: No API calls should be needed since caches are populated
#         mock_get_data.assert_not_called()

#         # Validate global DF values
#         assert "101" in df_utils.course_id_df
#         assert "501" in df_utils.quiz_id_df
#         assert "u1" in df_utils.user_id_df
#         assert "time" in df_utils.accom_type_df
#         assert "past" in df_utils.accom_date_df
#         assert any(q in ["classic", "new"] for q in df_utils.quiz_type_df)
