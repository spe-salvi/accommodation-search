# import pytest
# from unittest.mock import patch
# import utils.resolvers as resolvers
# import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# logger.propagate=True

# @pytest.fixture
# def mock_test_course_id():
#     with patch("utils.resolvers.test_course_id") as mock:
#         yield mock

# @pytest.fixture
# def mock_resolve_cids():
#     with patch("utils.resolvers.resolve_cids") as mock:
#         yield mock

# @pytest.fixture
# def mock_resolve_qids():
#     with patch("utils.resolvers.resolve_qids") as mock:
#         yield mock

# @pytest.fixture
# def mock_resolve_uids():
#     with patch("utils.resolvers.resolve_uids") as mock:
#         yield mock

# @pytest.fixture
# def mock_resolve_enrollments():
#     with patch("utils.resolvers.resolve_enrollments") as mock:
#         yield mock

# @pytest.fixture
# def mock_resolve_terms():
#     with patch("utils.resolvers.resolve_terms") as mock:
#         yield mock

# @pytest.fixture
# def mock_resolve_url():
#     with patch("utils.resolvers.resolve_url") as mock:
#         yield mock

# @pytest.fixture
# def mock_load_course_cache():
#     with patch("utils.resolvers.load_course_cache") as mock:
#         yield mock

# @pytest.fixture
# def mock_requests_get():
#     with patch("utils.resolvers.requests.get") as mock:
#         yield mock

# ############################################################
# # Test cases for resolve_search_params
# ############################################################

# def test_course_ids_input(mock_test_course_id, mock_resolve_qids, mock_resolve_uids):
#     # terms, course_ids, quiz_ids, user_ids, accom_type, date_filter = cleaned_input
#     cleaned_input = [None, ['2025-PHL-213'], None, None, None, None]
#     resolvers.resolve_search_params(cleaned_input)
#     mock_test_course_id.assert_called_once_with(['2025-PHL-213'])
#     mock_resolve_qids.assert_called_once()
#     mock_resolve_uids.assert_called_once()

# def test_user_ids_input(mock_resolve_qids, mock_resolve_enrollments):
#     # terms, course_ids, quiz_ids, user_ids, accom_type, date_filter = cleaned_input
#     cleaned_input = [None, None, None, ['12345'], None, None]
#     resolvers.resolve_search_params(cleaned_input)
#     mock_resolve_enrollments.assert_called_once()
#     mock_resolve_qids.assert_called_once()

# def test_quiz_ids_input_terms(mock_resolve_terms, mock_resolve_uids, mock_resolve_url):
#     # terms, course_ids, quiz_ids, user_ids, accom_type, date_filter = cleaned_input
#     cleaned_input = [['123'], None, ['67890'], None, None, None]
#     resolvers.resolve_search_params(cleaned_input)
#     mock_resolve_terms.term_cache = {'123': {'courses': ['c201', 'c202']}}
#     mock_resolve_url.return_value = ['c201', 'c202']
#     mock_resolve_terms.assert_called_once_with(['123'])
#     mock_resolve_url.assert_called_once()
#     mock_resolve_uids.assert_called_once()

# def test_quiz_ids_input_no_terms(mock_resolve_terms, mock_resolve_cids, mock_resolve_uids, mock_resolve_url):
#     # terms, course_ids, quiz_ids, user_ids, accom_type, date_filter = cleaned_input
#     cleaned_input = [None, None, ['67890'], None, None, None]
#     resolvers.resolve_search_params(cleaned_input)
#     mock_resolve_cids.assert_called_once()
#     mock_resolve_cids.return_value = ['c201', 'c202']
#     mock_resolve_url.assert_called_once()
#     mock_resolve_uids.assert_called_once()

# ##########################################
# # Test cases for helper_cache_compare
# ##########################################

# # course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
# def test_helper_cache_compare_diff_q():
#     assert resolvers.helper_cache_compare({'123':{'quizzes':['67890']}}, '123', ['09876'], 'quiz') == False

# def test_helper_cache_compare_same_q():
#     assert resolvers.helper_cache_compare({'123':{'quizzes':['67890']}}, '123', ['67890'], 'quiz') == True

# def test_helper_cache_compare_more_q():
#     assert resolvers.helper_cache_compare({'123':{'quizzes':['09876']}}, '123', ['09876', '05432'], 'quiz') == False

# def test_helper_cache_compare_less_q():
#     assert resolvers.helper_cache_compare({'123':{'quizzes':['67890', '12345']}}, '123', ['67890'], 'quiz') == True

# def test_helper_cache_compare_empty_q():
#     assert resolvers.helper_cache_compare({'123':{'quizzes':[]}}, '123', ['09876'], 'quiz') == False

# def test_helper_cache_compare_none_q():
#     assert resolvers.helper_cache_compare(None, '123', ['09876'], 'quiz') == False

# def test_helper_cache_compare_diff_u():
#     assert resolvers.helper_cache_compare({'123':{'users':['67890']}}, '123', ['09876'], 'user') == False

# def test_helper_cache_compare_same_u():
#     assert resolvers.helper_cache_compare({'123':{'users':['67890']}}, '123', ['67890'], 'user') == True

# def test_helper_cache_compare_more_u():
#     assert resolvers.helper_cache_compare({'123':{'users':['09876']}}, '123', ['09876', '05432'], 'user') == False

# def test_helper_cache_compare_less_u():
#     assert resolvers.helper_cache_compare({'123':{'users':['67890', '12345']}}, '123', ['67890'], 'user') == True

# def test_helper_cache_compare_empty_u():
#     assert resolvers.helper_cache_compare({'123':{'users':[]}}, '123', ['09876'], 'user') == False

# def test_helper_cache_compare_none_u():
#     assert resolvers.helper_cache_compare(None, '123', ['09876'], 'user') == False

# ##########################################
# # Test cases for flip_cache
# ###########################################

# def test_flip_cache_empty():
#     cache = {}
#     flipped = resolvers.flip_cache(cache)
#     assert flipped == {}

# def test_flip_cache_unique_values():
#     cache = {
#         'key1': 'value1',
#         'key2': 'value2',
#         'key3': 'value3',
#     }
#     flipped = resolvers.flip_cache(cache)
#     assert flipped == {
#         'value1': ['key1'],
#         'value2': ['key2'],
#         'value3': ['key3'],
#     }

# def test_flip_cache_duplicate_values():
#     cache = {
#         'key1': 'value1',
#         'key2': 'value1',
#         'key3': 'value2',
#     }
#     flipped = resolvers.flip_cache(cache)
#     assert flipped == {
#         'value1': ['key1', 'key2'],
#         'value2': ['key3'],
#     }

# ##########################################
# # Test cases for test_course_id
# ##########################################


# def test_test_course_id(mock_load_course_cache):
#     mock_load_course_cache.return_value = {
#         '123': {'code': 'C123', 'name': 'Course 123', 'term': 'T1', 'users': ['U1', 'U2'], 'quizzes': ['Q1', 'Q2']},
#         '456': {'code': 'C456', 'name': 'Course 456', 'term': 'T2', 'users': ['U3'], 'quizzes': ['Q3']}
#     }
    
#     course_ids = resolvers.test_course_id(['123', '456'])
#     assert course_ids == {'123', '456'}

# def test_test_course_id_not_found(mock_load_course_cache, mock_requests_get):
#     mock_load_course_cache.return_value = {}
    
#     course_ids = resolvers.test_course_id(['123'])
#     mock_requests_get.assert_called_once()
#     mock_requests_get.return_value.status_code = 404  # Simulate not found
#     assert course_ids == set()

# def test_test_course_id_found(mock_load_course_cache, mock_requests_get, monkeypatch):
#     mock_load_course_cache.return_value = {}
#     mock_requests_get.return_value.status_code = 200  # Simulate found

#     course_ids = resolvers.test_course_id(['123'])
#     mock_requests_get.assert_called_once()
#     assert course_ids == {'123'}