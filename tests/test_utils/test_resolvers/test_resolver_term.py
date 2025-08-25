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
# def mock_load_term_cache():
#     with patch("utils.resolvers.load_term_cache") as mock:
#         yield mock

# # Case: terms is None
# def test_terms_is_none(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.return_value={}
#     result = resolvers.resolve_terms(None)
#     assert result == {}
#     mock_get_data.assert_not_called()

# # Case: terms is empty
# def test_terms_is_empty(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.return_value={}
#     result = resolvers.resolve_terms([])
#     assert result == {}
#     mock_get_data.assert_not_called()

# # Case: term_cache is None initially
# def test_term_cache_is_none(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.side_effect=[None, {'2025F': {'some': 'data'}}]
#     result = resolvers.resolve_terms(['2025F'])
#     assert result == {'2025F': {'some': 'data'}}
#     assert mock_get_data.call_count == 2

# # Case: term_cache is empty
# def test_term_cache_is_empty(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.side_effect=[{}, {'2025F': {'some': 'data'}}]
#     result = resolvers.resolve_terms(['2025F'])
#     assert result == {'2025F': {'some': 'data'}}
#     assert mock_get_data.call_count == 2

# # Case: get_data does not write to term_cache
# def test_get_data_t_writes_nothing(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.side_effect=[{}, {}]
#     result = resolvers.resolve_terms(['2025F'])
#     assert result == {}
#     assert mock_get_data.call_count == 2

# # Case: get_data writes empty entry to term_cache
# def test_get_data_t_writes_empty_entry(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.side_effect=[{}, {'2025F': {}}]
#     result = resolvers.resolve_terms(['2025F'])
#     assert result == {'2025F': {}}
#     assert mock_get_data.call_count == 2

# # Case: term already in cache
# def test_term_already_in_cache(mock_get_data, mock_load_term_cache):
#     mock_load_term_cache.side_effect=[{'2025F': {'name': 'Fall 2025'}}, {'2025F': {'name': 'Fall 2025'}}]
#     result = resolvers.resolve_terms(['2025F'])
#     assert result == {'2025F': {'name': 'Fall 2025'}}
#     mock_get_data.assert_not_called()
