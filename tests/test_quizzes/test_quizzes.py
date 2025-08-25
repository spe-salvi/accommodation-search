# import pytest
# from unittest.mock import patch
# import api.api_endpoints as api_endpoints
# from quizzes.quizzes import is_accommodated

# @pytest.fixture
# def mock_cache_time():
#     return {
#         'user1': {
#             'course1': {
#                 'quiz1': {
#                     'extra_time': 10,
#                     'extra_attempts': 0,
#                     'date': 'past'
#                 }
#             }
#         }
#     }

# @pytest.fixture
# def mock_cache_attempts():
#     return {
#         'user1': {
#             'course1': {
#                 'quiz1': {
#                     'extra_time': 0,
#                     'extra_attempts': 2,
#                     'date': 'past'
#                 }
#             }
#         }
#     }

# @patch('quizzes.quizzes.api_endpoints.submission_cache')
# @patch('quizzes.quizzes.get_data')
# def test_time_accommodation(mock_get_data, mock_submission_cache, mock_cache_time):
#     with patch.object(api_endpoints, 'submission_cache', mock_cache_time):
#         result = is_accommodated('course1', 'quiz1', 'user1', 'time')
#         assert result == (False, 'NA')  # Because 10 != 10*2

# @patch('quizzes.quizzes.api_endpoints.submission_cache')
# @patch('quizzes.quizzes.get_data')
# def test_attempts_accommodation(mock_get_data, mock_submission_cache, mock_cache_attempts):
#     with patch.object(api_endpoints, 'submission_cache', mock_cache_attempts):
#         result = is_accommodated('course1', 'quiz1', 'user1', 'attempts')
#         assert result == (True, 'past')

# @patch('quizzes.quizzes.api_endpoints.submission_cache')
# @patch('quizzes.quizzes.get_data')
# def test_missing_quiz(mock_get_data, mock_submission_cache, mock_cache_attempts):
#     # First cache: missing quiz_id
#     first_cache = {
#         'user1': {
#             'course1': {
#                 # 'quiz1' is missing
#             }
#         }
#     }
#     # Second cache: has quiz_id
#     second_cache = mock_cache_attempts

#     # Patch the cache to first_cache, then after get_data, patch to second_cache
#     with patch.object(api_endpoints, 'submission_cache', first_cache):
#         # Call is_accommodated, which will trigger get_data and expect the cache to update
#         with patch('quizzes.quizzes.get_data') as mock_get_data:
#             # When get_data is called, update the cache
#             def update_cache(*args, **kwargs):
#                 api_endpoints.submission_cache = second_cache
#             mock_get_data.side_effect = update_cache

#             result = is_accommodated('course1', 'quiz1', 'user1', 'attempts')
#             assert result == (True, 'past')
#             assert mock_get_data.call_count >= 1

# @patch('quizzes.quizzes.api_endpoints.submission_cache')
# @patch('quizzes.quizzes.get_data')
# def test_missing_course(mock_get_data, mock_submission_cache, mock_cache_attempts):
#     # First cache: missing quiz_id
#     first_cache = {
#         'user1': {
#             # course1 is missing
#         }
#     }
#     # Second cache: has quiz_id
#     second_cache = mock_cache_attempts

#     # Patch the cache to first_cache, then after get_data, patch to second_cache
#     with patch.object(api_endpoints, 'submission_cache', first_cache):
#         # Call is_accommodated, which will trigger get_data and expect the cache to update
#         with patch('quizzes.quizzes.get_data') as mock_get_data:
#             # When get_data is called, update the cache
#             def update_cache(*args, **kwargs):
#                 api_endpoints.submission_cache = second_cache
#             mock_get_data.side_effect = update_cache

#             result = is_accommodated('course1', 'quiz1', 'user1', 'attempts')
#             assert result == (True, 'past')
#             assert mock_get_data.call_count >= 1

# @patch('quizzes.quizzes.api_endpoints.submission_cache')
# @patch('quizzes.quizzes.get_data')
# def test_missing_user(mock_get_data, mock_submission_cache, mock_cache_attempts):
#     # First cache: missing quiz_id
#     first_cache = {
#         # user1 is missing
#     }
#     # Second cache: has quiz_id
#     second_cache = mock_cache_attempts

#     # Patch the cache to first_cache, then after get_data, patch to second_cache
#     with patch.object(api_endpoints, 'submission_cache', first_cache):
#         # Call is_accommodated, which will trigger get_data and expect the cache to update
#         with patch('quizzes.quizzes.get_data') as mock_get_data:
#             # When get_data is called, update the cache
#             def update_cache(*args, **kwargs):
#                 api_endpoints.submission_cache = second_cache
#             mock_get_data.side_effect = update_cache

#             result = is_accommodated('course1', 'quiz1', 'user1', 'attempts')
#             assert result == (True, 'past')
#             assert mock_get_data.call_count >= 1

# def test_null_data():
#     # Both before and after get_data, the cache is empty
#     empty_cache = {}

#     with patch.object(api_endpoints, 'submission_cache', empty_cache):
#         with patch('quizzes.quizzes.get_data') as mock_get_data:
#             # get_data does nothing and returns None
#             mock_get_data.return_value = None

#             result = is_accommodated('course1', 'quiz1', 'user1', 'attempts')
#             assert result == (False, 'NA')
#             assert mock_get_data.call_count >= 1

# @patch('quizzes.quizzes.api_endpoints.submission_cache')
# @patch('quizzes.quizzes.get_data')
# def test_no_acc_type(mock_get_data, mock_submission_cache, mock_cache_attempts):
#     with patch.object(api_endpoints, 'submission_cache', mock_cache_attempts):
#         result = is_accommodated('course1', 'quiz1', 'user1', None)
#         assert result == (False, 'NA')