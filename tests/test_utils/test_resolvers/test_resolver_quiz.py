# import pytest
# from unittest.mock import patch
# import utils.resolvers as resolvers
# import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# logger.propagate=True

# @pytest.fixture
# def mock_get_data():
#     with patch("utils.resolvers.get_data") as mock:
#         yield mock

# @pytest.fixture
# def mock_load_course_cache():
#     with patch("utils.resolvers.load_course_cache") as mock:
#         yield mock

# @pytest.fixture
# def mock_helper_cache_compare():
#     with patch("utils.resolvers.helper_cache_compare") as mock:
#         yield mock

# # Case: quiz input is None
# def test_quiz_input_is_none(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[None,{'2025-PHL-213':{'quizzes': [123]}}]
#     resolvers.resolve_qids(['2025-PHL-213'])
#     assert mock_get_data.call_count == 2

# # Case: quiz input is empty
# def test_quiz_input_is_empty(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[None,{'2025-PHL-213':{'quizzes': [123]}}]
#     resolvers.resolve_qids(['2025-PHL-213'], [])
#     assert mock_get_data.call_count == 2

# # Case: course_cache is None initially
# def test_course_cache_is_none(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[None,{'2025-PHL-213':{'quizzes': [123]}}]
#     resolvers.resolve_qids(['2025-PHL-213'], [123, 456])
#     assert mock_get_data.call_count == 2

# # Case: get_data does not write to course_cache
# def test_get_data_c_writes_nothing(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{}, {}]
#     resolvers.resolve_qids(['2025-PHL-213'])
#     assert mock_get_data.call_count == 2

# # Case: course_cache is empty
# def test_course_cache_is_empty(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{},{'2025-PHL-213':{'quizzes': [123]}}]
#     resolvers.resolve_qids(['2025-PHL-213'], [123, 456])
#     assert mock_get_data.call_count == 2

# # Case: get_data writes empty entry to course_cache
# def test_get_data_c_writes_empty_entry(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{}, {'2025-PHL-213':{'quizzes': []}}]
#     resolvers.resolve_qids(['2025-PHL-213'])
#     assert mock_get_data.call_count == 2

# # Case: quiz input is one
# def test_quiz_input_is_one(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213':{'quizzes': [123]}},{'2025-PHL-213':{'quizzes': [123]}}]
#     resolvers.resolve_qids(['2025-PHL-213'], [123])
#     mock_get_data.assert_not_called()

# # Case: course_cache points to empty
# def test_course_cache_points_to_empty(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213':{'quizzes': []}}, {'2025-PHL-213':{'quizzes': [123, 456]}}]
#     mock_helper_cache_compare.side_effect = [True, True, True]
#     resolvers.resolve_qids(['2025-PHL-213'], [123, 456])
#     mock_get_data.assert_not_called()

# # Case: Cache compare less
# def test_cache_compare_less(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213':{'quizzes': [123, 456]}},{'2025-PHL-213':{'quizzes': [123, 456]}}]
#     mock_helper_cache_compare.return_value = [True]
#     resolvers.resolve_qids(['2025-PHL-213'],[123])
#     mock_get_data.assert_not_called()

# # Case: Cache compare different
# def test_cache_compare_different(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213':{'quizzes': [123]}},{'2025-PHL-213':{'quizzes': [123, 456]}}]
#     mock_helper_cache_compare.side_effect = [True, True, True]
#     resolvers.resolve_qids(['2025-PHL-213'],[456])
#     mock_get_data.assert_not_called()

# # Case: Cache compare more
# def test_cache_compare_more(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213':{'quizzes': [123]}},{'2025-PHL-213':{'quizzes': [123]}}]
#     mock_helper_cache_compare.return_value = [True]
#     resolvers.resolve_qids(['2025-PHL-213'],[123, 456])
#     mock_get_data.assert_not_called()

# # Case: course already in cache
# def test_course_already_in_cache(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213':{'quizzes': [123, 456]}},{'2025-PHL-213':{'quizzes': [123, 456]}}]
#     resolvers.resolve_qids(['2025-PHL-213'],[123, 456])
#     mock_get_data.assert_not_called()

# # Case: Course input none
# def test_course_input_none(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     resolvers.resolve_qids(None,[123, 456])
#     mock_get_data.assert_not_called()

# # Case: Course input empty
# def test_course_input_empty(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     resolvers.resolve_qids([],[123, 456])
#     mock_get_data.assert_not_called()

# # Case: Course input many
# def test_course_input_many(mock_get_data, mock_load_course_cache, mock_helper_cache_compare):
#     mock_load_course_cache.side_effect=[{},{'2025-PHL-213':{'quizzes': [123, 456]}, '2025-THE-115':{'quizzes': [789]}}]
#     resolvers.resolve_qids(['2025-PHL-213', '2025-THE-115'],[123, 456, 789])
#     assert mock_get_data.call_count == 4

# # Case: quiz is not found
# def test_quiz_not_found(mock_get_data, mock_load_course_cache, mock_helper_cache_compare, caplog):
#     caplog.set_level(logging.INFO)
#     mock_helper_cache_compare.return_value = False
#     assert mock_helper_cache_compare.return_value is False
#     resolvers.resolve_qids(['2025-PHL-213'],[123])
#     assert mock_helper_cache_compare.return_value is False
#     # assert caplog.records[0].msg == 'Some entered quizzes were not found.'
#     assert any('Some entered quizzes were not found.' in message for message in caplog.messages)