import pytest
from unittest.mock import patch
import api.api_endpoints as endpoints
from api.api_endpoints import endpoint_submissions, submission_cache
import logging

@pytest.fixture(autouse=True)
def reset_term_cache():
    endpoints.term_cache = {}

@pytest.fixture
def mock_save_term_cache():
    with patch("utils.cache_manager.save_term_cache") as mock:
        yield mock

@pytest.fixture
def reset_quiz_cache():
    """Fixture to reset the quiz_cache before each test."""
    endpoints.quiz_cache = {}

@pytest.fixture
def reset_submission_cache():
    endpoints.submission_cache = {}

##################################### Endpoint for Terms ########################################

# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
 
# def test_endpoint_term_none(mock_save_term_cache):
#     # Test when term_id is not provided
#     endpoints.endpoint_term({'id': 'T1', 'name': 'Term 1', 'courses': []})
#     assert 'T1' in endpoints.term_cache
#     assert endpoints.term_cache['T1']['name'] == 'Term 1'
#     assert endpoints.term_cache['T1']['courses'] == []
#     mock_save_term_cache.assert_called_once_with()

# def test_endpoint_term_id(mock_save_term_cache):
#     # Test when term_id is provided
#     endpoints.endpoint_term({'id': 'T2', 'name': 'Term 2'}, term_id='T2')
#     assert 'T2' in endpoints.term_cache
#     assert endpoints.term_cache['T2']['name'] == 'Term 2'
#     assert endpoints.term_cache['T2']['courses'] == []
#     mock_save_term_cache.assert_called_once_with()

# def test_endpoint_term_missing_id(mock_save_term_cache, caplog):
#     # Test when 'id' key is missing in the data
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_term({'name': 'Term 3'})
#         assert "The 'id' key is missing in the provided data." in caplog.text
#     mock_save_term_cache.assert_not_called()

####################################### Endpoints for Courses ########################################

# term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}

# def test_endpoint_courses_with_course_id():
#     result = endpoints.endpoint_courses([], course_id='C1')
#     assert result is None

# def test_endpoint_courses_with_quiz_id():
#     result = endpoints.endpoint_courses([], quiz_id='Q1')
#     assert result is None

# def test_endpoint_courses_with_user_id():
#     result = endpoints.endpoint_courses([], user_id='U1')
#     assert result is None

# def test_endpoint_courses_with_term_id_none():
#     data = [{'id': 'C1', 'enrollment_term_id': 'T1'}]
#     endpoints.endpoint_courses(data)
#     assert 'T1' in endpoints.term_cache
#     assert endpoints.term_cache['T1']['courses'] == ['C1']

# def test_endpoint_courses_with_term_id_given(monkeypatch):
#     monkeypatch.setattr(endpoints, "term_cache", {'T1': {'name': 'Term 1', 'courses': ['C2']}})
#     data = [{'id': 'C2', 'enrollment_term_id': 'T1'}]
#     endpoints.endpoint_courses(data, term_id='T1')
#     assert 'T1' in endpoints.term_cache
#     assert endpoints.term_cache['T1']['courses'] == ['C2']

# def test_endpoint_courses_with_data_none_and_term_id_none():
#     result = endpoints.endpoint_courses(None)
#     assert result is None

# def test_endpoint_courses_with_data_none_and_term_id_given():
#     result = endpoints.endpoint_courses(None, term_id='T1')
#     assert result is None

# def test_endpoint_courses_missing_id(caplog):
#     # Test when 'id' key is missing in a course
#     data = [{'enrollment_term_id': 'T1'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_courses(data)
#         assert "endpoint_courses: Missing 'id' or 'enrollment_term_id' in provided data" in caplog.text

# def test_endpoint_courses_missing_enrollment_term_id(caplog):
#     # Test when 'enrollment_term_id' key is missing in a course
#     data = [{'id': 'C1'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_courses(data)
#         assert "endpoint_courses: Missing 'id' or 'enrollment_term_id' in provided data" in caplog.text

####################################### Endpoints for Quizzes ########################################

# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}

# def test_endpoint_quizzes_with_term_id(caplog):
#     result = endpoints.endpoint_quizzes([], term_id='T1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quizzes: Invalid input provided; skipping course cache update." in caplog.text
#     assert result is None

# def test_endpoint_quizzes_with_quiz_id(caplog):
#     result = endpoints.endpoint_quizzes([], quiz_id='Q1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quizzes: Invalid input provided; skipping course cache update." in caplog.text
#     assert result is None

# def test_endpoint_quizzes_with_user_id(caplog):
#     result = endpoints.endpoint_quizzes([], user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quizzes: Invalid input provided; skipping course cache update." in caplog.text
#     assert result is None

# def test_endpoint_quizzes_with_data_none_and_course_id_none(caplog):
#     result = endpoints.endpoint_quizzes(None)
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quizzes: Invalid input provided; skipping course cache update." in caplog.text
#     assert result is None

# def test_endpoint_quizzes_with_data_none_and_course_id_given(caplog):
#     result = endpoints.endpoint_quizzes(None, course_id='C1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quizzes: Invalid input provided; skipping course cache update." in caplog.text
#     assert result is None

# def test_endpoint_quizzes_with_data_given_and_course_id_none(caplog):
#     result = endpoints.endpoint_quizzes([])
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quizzes: Invalid input provided; skipping course cache update." in caplog.text
#     assert result is None

# def test_endpoint_quizzes_missing_id(caplog):
#     # Test when 'id' key is missing in a quiz
#     data = [{'name': 'Quiz 1'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_quizzes(data, course_id='C1')
#         assert "endpoint_quizzes: Missing 'id' in provided data:" in caplog.text

####################################### Endpoints for Enrollments ########################################

# # user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': (course_id, course_id, course_id)}, ...}

# def test_endpoint_enrollments_with_data(caplog):
#     endpoints.endpoint_enrollments(data = [{'name' : 'John Doe'}], course_id='C1', user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_enrollments: Invalid input provided; skipping user cache update." in caplog.text

# def test_endpoint_enrollments_with_term_id(caplog):
#     endpoints.endpoint_enrollments(term_id='T1', course_id='C1', user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_enrollments: Invalid input provided; skipping user cache update." in caplog.text

# def test_endpoint_enrollments_with_quiz_id(caplog):
#     endpoints.endpoint_enrollments(course_id = 'C1', quiz_id='Q1', user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_enrollments: Invalid input provided; skipping user cache update." in caplog.text

# def test_endpoint_enrollments_with_course_id_none(caplog):
#     endpoints.endpoint_enrollments(course_id=None, user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_enrollments: Invalid input provided; skipping user cache update." in caplog.text

# def test_endpoint_enrollments_with_user_id_none(caplog):
#     endpoints.endpoint_enrollments(course_id='C1', user_id=None)
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_enrollments: Invalid input provided; skipping user cache update." in caplog.text

# def test_endpoint_enrollments_update_course(monkeypatch):
#     monkeypatch.setattr(endpoints, "user_cache", {'U1': {'name': 'John Doe', 'sis_id': 'PHL-113', 'email': 'jdoe@web.com', 'courses': ['C1']}})
#     endpoints.endpoint_enrollments(course_id='C2', user_id='U1')
#     assert 'C2' in endpoints.user_cache['U1']['courses']


####################################### Endpoints for Course #########################################

# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}

# def test_endpoint_course_with_term_id(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course(data, term_id='T1', course_id='C1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course: Invalid input provided; skipping course cache update." in caplog.text

# def test_endpoint_course_with_quiz_id(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course(data, course_id = 'C1', quiz_id='Q1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course: Invalid input provided; skipping course cache update." in caplog.text

# def test_endpoint_course_with_user_id(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course(data, course_id = 'C1', user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course: Invalid input provided; skipping course cache update." in caplog.text

# def test_endpoint_course_with_course_id_none(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course(data, course_id=None)
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course: Invalid input provided; skipping course cache update." in caplog.text

# def test_endpoint_course_with_data_none(caplog):
#     endpoints.endpoint_course(data = None, course_id='C1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course: Invalid input provided; skipping course cache update." in caplog.text

# def test_endpoint_course_key_error_id(caplog):
#     data = [{'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_course(data, course_id='C1')
#         assert "endpoint_course: Missing 'id' in provided data:" in caplog.text


####################################### Endpoints for Course Users #########################################

# course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
# user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': [course_id, course_id, course_id]}, ...}

# def test_endpoint_course_users_with_term_id(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course_users(data, term_id='T1', course_id='C1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course_users: Invalid input provided; skipping cache updates." in caplog.text

# def test_endpoint_course_users_with_quiz_id(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course_users(data, course_id = 'C1', quiz_id='Q1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course_users: Invalid input provided; skipping cache updates." in caplog.text

# def test_endpoint_course_users_with_user_id(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course_users(data, course_id = 'C1', user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course_users: Invalid input provided; skipping cache updates." in caplog.text

# def test_endpoint_course_users_with_course_id_none(caplog):
#     data = [{'id': 'C1', 'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     endpoints.endpoint_course_users(data, course_id=None)
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course_users: Invalid input provided; skipping cache updates." in caplog.text

# def test_endpoint_course_users_with_data_none(caplog):
#     endpoints.endpoint_course_users(data = None, course_id='C1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_course_users: Invalid input provided; skipping cache updates." in caplog.text

# def test_endpoint_course_users_key_error_id(caplog):
#     data = [{'course_code': 'CODE1', 'name': 'Course 1', 'term': 'T1'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_course_users(data, course_id='C1')
#         assert "endpoint_course_users: Missing 'id' in provided data:" in caplog.text

####################################### Endpoints for Quiz #########################################

# quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}

# def test_endpoint_quiz_with_term_id(caplog):
#     data = [{'quiz_id': 'Q1', 'title': 'Quiz 1', 'type': 'classic', 'course_id': 'C1', 'time_limit': 30}]
#     endpoints.endpoint_quiz(data, term_id='T1', course_id='C1', quiz_id='Q1', acc_type='quiz')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quiz: Invalid input provided; skipping quiz cache update." in caplog.text

# def test_endpoint_quiz_with_user_id(caplog):
#     data = [{'quiz_id': 'Q1', 'title': 'Quiz 1', 'type': 'classic', 'course_id': 'C1', 'time_limit': 30}]
#     endpoints.endpoint_quiz(data, course_id = 'C1', quiz_id='Q1', user_id='U1', acc_type='quiz')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quiz: Invalid input provided; skipping quiz cache update." in caplog.text

# def test_endpoint_quiz_with_data_none(caplog):
#     endpoints.endpoint_quiz(data=None, course_id='C1', quiz_id='Q1', acc_type='quiz')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quiz: Invalid input provided; skipping quiz cache update." in caplog.text

# def test_endpoint_quiz_with_course_id_none(caplog):
#     data = [{'quiz_id': 'Q1', 'title': 'Quiz 1', 'type': 'classic', 'course_id': 'C1', 'time_limit': 30}]
#     endpoints.endpoint_quiz(data, course_id = None, quiz_id='Q1', acc_type='quiz')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quiz: Invalid input provided; skipping quiz cache update." in caplog.text

# def test_endpoint_quiz_with_quiz_id_none(caplog):
#     data = [{'quiz_id': 'Q1', 'title': 'Quiz 1', 'type': 'classic', 'course_id': 'C1', 'time_limit': 30}]
#     endpoints.endpoint_quiz(data, course_id = 'C1', quiz_id=None, acc_type='quiz')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_quiz: Invalid input provided; skipping quiz cache update." in caplog.text

# def test_endpoint_quiz_key_error_title(caplog):
#     data = [{'quiz_id': 'Q1', 'type': 'classic', 'course_id': 'C1', 'time_limit': 30}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_quiz(data, course_id='C1', quiz_id='Q1', acc_type='quiz')
#         assert "endpoint_quiz: Missing 'title' or 'time_limit' in provided data:" in caplog.text

# def test_endpoint_quiz_key_error_time_limit(caplog):
#     data = [{'quiz_id': 'Q1', 'title': 'Quiz 1', 'type': 'classic', 'course_id': 'C1'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_quiz(data, course_id='C1', quiz_id='Q1', acc_type='quiz')
#         assert "endpoint_quiz: Missing 'title' or 'time_limit' in provided data:" in caplog.text

####################################### Endpoints for Submissions #########################################

# submission_cache = {submission_id: {'user_id': user_id, 'quiz_id': quiz_id, 'extra_time': extra_time, 'extra_attempts': extra_attempts, 'date': date}, ...}

# def test_endpoint_submissions_with_term_id(caplog):
#     data = [{'user_id': 'U1', 'extra_time': 3, 'extra_attempts': 1, 'workflow_state': 'complete'}]
#     endpoints.endpoint_submissions(data, term_id='T1', course_id='C1', quiz_id='Q1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_submissions: Invalid input provided; skipping submission cache update." in caplog.text

# def test_endpoint_submissions_with_user_id(caplog):
#     data = [{'user_id': 'U1', 'extra_time': 3, 'extra_attempts': 1, 'workflow_state': 'complete'}]
#     endpoints.endpoint_submissions(data, course_id = 'C1', quiz_id='Q1', user_id='U1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_submissions: Invalid input provided; skipping submission cache update." in caplog.text

# def test_endpoint_submissions_with_data_none(caplog):
#     endpoints.endpoint_submissions(data=None, course_id='C1', quiz_id='Q1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_submissions: Invalid input provided; skipping submission cache update." in caplog.text

# def test_endpoint_submissions_with_course_id_none(caplog):
#     data = [{'user_id': 'U1', 'extra_time': 3, 'extra_attempts': 1, 'workflow_state': 'complete'}]
#     endpoints.endpoint_submissions(data, course_id = None, quiz_id='Q1')
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_submissions: Invalid input provided; skipping submission cache update." in caplog.text

# def test_endpoint_submissions_with_quiz_id_none(caplog):
#     data = [{'user_id': 'U1', 'extra_time': 3, 'extra_attempts': 1, 'workflow_state': 'complete'}]
#     endpoints.endpoint_submissions(data, course_id = 'C1', quiz_id=None)
#     with caplog.at_level(logging.ERROR):
#         assert "endpoint_submissions: Invalid input provided; skipping submission cache update." in caplog.text

# def test_endpoint_submissions_key_error_id(caplog):
#     data = [{'extra_time': 3, 'extra_attempts': 1, 'workflow_state': 'complete'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#         assert "endpoint_submissions: Missing 'user_id' in provided data:" in caplog.text

# def test_endpoint_submissions_key_error_extra_time(caplog):
#     data = [{'user_id': 'U1', 'extra_attempts': 1, 'workflow_state': 'complete'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#         assert "endpoint_submissions: Missing data in provided data:" in caplog.text

# def test_endpoint_submissions_key_error_extra_attempts(caplog):
#     data = [{'user_id': 'U1', 'extra_time': 3, 'workflow_state': 'complete'}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#         assert "endpoint_submissions: Missing data in provided data:" in caplog.text

# def test_endpoint_submissions_key_error_workflow_state(caplog):
#     data = [{'user_id': 'U1', 'extra_time': 3, 'extra_attempts': 1}]
#     with caplog.at_level(logging.ERROR):
#         endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#         assert "endpoint_submissions: Missing data in provided data:" in caplog.text

# def test_endpoint_submissions_workflow_complete(reset_submission_cache):
#     data = [{'user_id': 'U1', 'extra_time': 10, 'extra_attempts': 2, 'workflow_state': 'complete'}]
#     endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#     assert endpoints.submission_cache['U1']['C1']['Q1']['date'] == 'past'

# def test_endpoint_submissions_workflow_graded(reset_submission_cache):
#     data = [{'user_id': 'U1', 'extra_time': 15, 'extra_attempts': 3, 'workflow_state': 'graded'}]
#     endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#     assert endpoints.submission_cache['U1']['C1']['Q1']['date'] == 'past'

# def test_endpoint_submissions_workflow_settings_only(reset_submission_cache):
#     data = [{'user_id': 'U1', 'extra_time': 5, 'extra_attempts': 1, 'workflow_state': 'settings_only'}]
#     endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#     assert endpoints.submission_cache['U1']['C1']['Q1']['date'] == 'future'

# def test_endpoint_submissions_workflow_other(reset_submission_cache):
#     data = [{'user_id': 'U1', 'extra_time': 20, 'extra_attempts': 4, 'workflow_state': 'other'}]
#     endpoints.endpoint_submissions(data, course_id='C1', quiz_id='Q1')
#     assert endpoints.submission_cache['U1']['C1']['Q1']['date'] == ''

######################################### Search URLs #####################################################

# quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}
# def test_search_urls_url_none(reset_quiz_cache, caplog):
#     endpoints.search_urls(None, course_id='C1')
#     assert "search_urls: Invalid input provided; skipping URL search." in caplog.text
#     assert endpoints.quiz_cache == {}

# @patch('requests.get')
# def test_search_urls_course_id_none(reset_quiz_cache, caplog):
#     endpoints.search_urls('http://example.com', course_id=None)
#     assert "search_urls: Invalid input provided; skipping URL search." in caplog.text
#     assert endpoints.quiz_cache == {}

# @patch('requests.get')
# def test_search_urls_response_404(mock_get, reset_quiz_cache):
#     mock_get.return_value.status_code = 404
#     endpoints.search_urls('http://example.com', course_id='C1')
#     assert endpoints.quiz_cache == {}

# @patch('requests.get')
# def test_search_urls_response_200(mock_get, reset_quiz_cache):
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.json.return_value = [
#         {'id': 'Q1', 'title': 'Quiz 1'},
#         {'id': 'Q2', 'title': 'Quiz 2'}
#     ]
#     endpoints.search_urls('http://example.com', course_id='C1')
#     assert endpoints.quiz_cache == {
#         'Q1': {'title': 'Quiz 1', 'type': '', 'course_id': 'C1'},
#         'Q2': {'title': 'Quiz 2', 'type': '', 'course_id': 'C1'}
#     }

# @patch('requests.get')
# def test_search_urls_missing_id_key(mock_get, reset_quiz_cache, caplog):
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.json.return_value = [
#         {'title': 'Quiz 1'}
#     ]
#     endpoints.search_urls('http://example.com', course_id='C1')
#     assert "search_urls: Missing key in provided data" in caplog.text
#     assert endpoints.quiz_cache == {}

# @patch('requests.get')
# def test_search_urls_missing_title_key(mock_get, reset_quiz_cache, caplog):
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.json.return_value = [
#         {'id': 'Q1'}
#     ]
#     endpoints.search_urls('http://example.com', course_id='C1')
#     assert "search_urls: Missing key in provided data" in caplog.text
#     assert endpoints.quiz_cache == {}
