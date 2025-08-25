# import pytest
# from unittest.mock import patch
# import utils.resolvers as resolvers
# import logging

# logging.basicConfig(level=logging.DEBUG)

# @pytest.fixture
# def mock_get_data():
#     with patch("utils.resolvers.get_data") as mock:
#         yield mock

# @pytest.fixture
# def mock_load_course_cache():
#     with patch("utils.resolvers.load_course_cache") as mock:
#         yield mock

# # Case: course_cache is None initially
# def test_course_cache_is_none(mock_get_data, mock_load_course_cache):
#     mock_load_course_cache.side_effect=[None, {'2025-PHL-213': {'name': 'Philosophy'}}]
#     result = resolvers.resolve_cids()
#     assert result == ['2025-PHL-213']
#     assert mock_get_data.call_count == 1

# # Case: course_cache is empty
# def test_course_cache_is_empty(mock_get_data, mock_load_course_cache):
#     mock_load_course_cache.side_effect=[{}, {'2025-PHL-213': {'name': 'Philosophy'}}]
#     result = resolvers.resolve_cids()
#     assert result == ['2025-PHL-213']
#     assert mock_get_data.call_count == 1

# # Case: get_data does not write to course_cache
# def test_get_data_c_writes_nothing(mock_get_data, mock_load_course_cache):
#     mock_load_course_cache.side_effect=[{}, {}]
#     result = resolvers.resolve_cids()
#     assert result == []
#     assert mock_get_data.call_count == 1

# # Case: get_data writes empty entry to course_cache
# def test_get_data_c_writes_empty_entry(mock_get_data, mock_load_course_cache):
#     mock_load_course_cache.side_effect=[{}, {'2025-PHL-213': {}}]
#     result = resolvers.resolve_cids()
#     assert result == ['2025-PHL-213']
#     assert mock_get_data.call_count == 1

# # Case: course already in cache
# def test_course_already_in_cache(mock_get_data, mock_load_course_cache):
#     mock_load_course_cache.side_effect=[{'2025-PHL-213': {'name': 'Philosophy'}}, {'2025-PHL-213': {'name': 'Philosophy'}}]
#     result = resolvers.resolve_cids()
#     assert result == ['2025-PHL-213']
#     mock_get_data.assert_not_called()
