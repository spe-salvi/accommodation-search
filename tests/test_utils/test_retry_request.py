# import pytest
# from unittest.mock import patch
# from utils.retry_request import retry_get

# test_url = 'https://franciscan.instructure.com/api/v1/courses/10348/quizzes/40122/submissions'

# # Helper to simulate paginatedGet raising an exception a certain number of times
# def make_side_effect(success_on_attempt):
#     calls = {'count': 0}
#     def side_effect(*args, **kwargs):
#         calls['count'] += 1
#         if calls['count'] < success_on_attempt:
#             raise Exception('Temporary error')
#         return {'result': 'success'}
#     return side_effect

# def test_retry_get_success_first_try():
#     with patch('utils.paginate.paginatedGet', return_value={'result': 'ok'}) as mock_get:
#         result = retry_get(test_url, {'a': 1})
#         assert result == {'result': 'ok'}
#         mock_get.assert_called_once()

# def test_retry_get_success_after_retries():
#     with patch('utils.paginate.paginatedGet', side_effect=make_side_effect(3)) as mock_get:
#         result = retry_get(test_url, {'a': 1})
#         assert result == {'result': 'success'}
#         assert mock_get.call_count == 3

# def test_retry_get_fails_after_max_retries():
#     with patch('utils.paginate.paginatedGet', side_effect=Exception('Always fails')) as mock_get:
#         with pytest.raises(Exception) as excinfo:
#             retry_get(test_url, {'a': 1})
#         assert 'Failed to fetch data after' in str(excinfo.value)
#         assert mock_get.call_count == 3

# # WRITE MORE TESTS