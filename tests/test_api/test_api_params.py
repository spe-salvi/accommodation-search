# import pytest
# from unittest.mock import patch, MagicMock
# import api.api_endpoints as api_endpoints
# import api.api_params as api_params

# def test_get_urls_all_keys():
#     urls = api_params.get_urls(term_id=115, course_id=10348, quiz_id=40122, user_id=5961)
#     expected_keys = {
#         'term', 'courses', 'course', 'course_users', 'users', 'c_quizzes', 'c_quiz',
#         'c_quiz_submissions', 'n_quizzes', 'n_quiz', 'n_quiz_submissions', 'enrollments'
#     }
#     assert set(urls.keys()) == expected_keys
#     assert 'courses' in urls
#     assert urls['course'][0].endswith('/v1/courses/10348')
#     assert urls['users'][0].endswith('/v1/users/5961')

# def test_function_dict_references():
#     assert api_params.function_dict['courses'] is api_endpoints.endpoint_courses
#     assert api_params.function_dict['c_quiz'] is api_endpoints.endpoint_quiz

# def test_get_data_calls_retry_and_function():
#     with patch('api.api_params.get_urls') as mock_get_urls, \
#          patch('api.api_params.retry.retry_get') as mock_retry_get:
#         mock_get_urls.return_value = {'foo': ['url', {'param': 115}]}
#         mock_function = MagicMock()
#         api_params.function_dict['foo'] = mock_function
#         mock_retry_get.return_value = {'data': 123}
#         api_params.get_data('foo', 115, 10348, 40122, 5961)
#         mock_get_urls.assert_called_once_with(115, 10348, 40122, 5961)
#         mock_retry_get.assert_called_once_with('url', {'param': 115})
#         mock_function.assert_called_once_with({'data': 123}, term_id=115, course_id=10348, quiz_id=40122, user_id=5961)
