# import pytest
# from unittest.mock import patch, MagicMock
# import utils.resolvers as resolvers
# import logging

# logging.basicConfig(level=logging.DEBUG)

# @pytest.fixture
# def mock_api_endpoints():
#     with patch("utils.resolvers.api_endpoints") as mock:
#         yield mock

# @pytest.fixture
# def mock_get_urls():
#     with patch("utils.resolvers.get_urls") as mock:
#         yield mock

# @pytest.fixture
# def mock_flip_cache():
#     with patch("utils.resolvers.flip_cache") as mock:
#         yield mock

# # quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}

# # Case: input course is none
# def test_course_is_none(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.search_urls = MagicMock()

#     result = resolvers.resolve_url(None, ['q5'])

#     assert result == []
#     mock_api_endpoints.search_urls.assert_not_called()

# # Case: input course is empty
# def test_course_is_empty(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.search_urls = MagicMock()

#     result = resolvers.resolve_url([], ['q5'])

#     assert result == []
#     mock_api_endpoints.search_urls.assert_not_called()

# # Case: input course is one and quiz is one
# def test_course_is_one(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.search_urls = MagicMock()

#     result = resolvers.resolve_url(['c201'], ['q5'])

#     assert result == ['c201']
#     mock_api_endpoints.search_urls.assert_not_called()

# # Case: input quiz is none
# def test_quiz_is_none(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.search_urls = MagicMock()

#     result = resolvers.resolve_url(['c201'], None)

#     assert result == []
#     mock_api_endpoints.search_urls.assert_not_called()

# # Case: input quiz is empty
# def test_quiz_is_empty(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.search_urls = MagicMock()

#     result = resolvers.resolve_url(['c201'], [])

#     assert result == []
#     mock_api_endpoints.search_urls.assert_not_called()

# # Case: cache is none
# def test_none_cache(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = None
#     mock_api_endpoints.search_urls = MagicMock()

#     updated_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.quiz_cache = updated_cache

#     result = resolvers.resolve_url(['c201'], ['q5'])

#     assert result == ['c201']
#     mock_api_endpoints.search_urls.assert_not_called()
#     mock_flip_cache.assert_called_once_with(updated_cache)

# # Case: cache is empty
# def test_empty_cache(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {}
#     mock_api_endpoints.search_urls = MagicMock()

#     updated_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     mock_api_endpoints.quiz_cache = updated_cache

#     result = resolvers.resolve_url(['c201'], ['q5'])

#     assert result == ['c201']
#     mock_api_endpoints.search_urls.assert_not_called()
#     mock_flip_cache.assert_called_once_with(updated_cache)

# # Case: cache points to empty
# def test_points_to_empty_cache(mock_api_endpoints, mock_get_urls, mock_flip_cache, monkeypatch):
#     mock_api_endpoints.quiz_cache = {'q5': {}}
#     mock_api_endpoints.search_urls = MagicMock()
#     assert mock_api_endpoints.quiz_cache == {'q5': {}}

#     updated_cache = {
#         'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': 'c201'},
#     }
#     monkeypatch.setattr(mock_api_endpoints, 'quiz_cache', updated_cache)

#     result = resolvers.resolve_url(['c201'], ['q5'])

#     assert mock_api_endpoints.quiz_cache == updated_cache

#     assert result == ['c201']
#     mock_api_endpoints.search_urls.assert_not_called()
#     mock_flip_cache.assert_called_once_with(updated_cache)

# # Case: cache points to no courses
# def test_cache_points_to_no_courses(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {'q5': {'title': 'Quiz 5', 'type': 'graded', 'course_id': None}}
#     mock_api_endpoints.search_urls = MagicMock()

#     result = resolvers.resolve_url(['c201'], ['q5'])

#     assert result == []
#     assert mock_api_endpoints.search_urls.call_count == 2

# # Case: none saved to cache
# def test_none_saved(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q99': {'title': 'Unrelated Quiz', 'type': 'practice', 'course_id': 'c999'}
#     }

#     result = resolvers.resolve_url(['c101'], ['q1'])

#     assert result == []
#     assert mock_api_endpoints.search_urls.call_count == 2

# # Case: empty save to cache
# def test_empty_saved(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {}

#     result = resolvers.resolve_url(['c101'], ['q1'])

#     assert result == []
#     assert mock_api_endpoints.search_urls.call_count == 2


# # Case: already in cache
# def test_quiz_already_in_cache(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {
#         'q1': {'title': 'Quiz 1', 'type': 'graded', 'course_id': 'c101'},
#         'q2': {'title': 'Quiz 2', 'type': 'practice', 'course_id': 'c102'},
#     }

#     course_ids = ['c101', 'c102']
#     quiz_ids = ['q1', 'q2']

#     result = resolvers.resolve_url(course_ids, quiz_ids)

#     assert set(result) == {'c101', 'c102'}
#     mock_api_endpoints.search_urls.assert_not_called()
#     mock_flip_cache.assert_called_once_with(mock_api_endpoints.quiz_cache)

# # Case: cache compare less
# def test_cache_compare_less(mock_api_endpoints, mock_get_urls, mock_flip_cache):
#     mock_api_endpoints.quiz_cache = {'q1' : {'title': 'Quiz 1', 'type': 'graded', 'course_id': 'c101'},
#                                      'q2' : {'title': 'Quiz 2', 'type': 'graded', 'course_id': 'c102'}}
#     mock_api_endpoints.search_urls = MagicMock()


    
#     result = resolvers.resolve_url(['c101'], ['q1'])

#     assert set(result) == {'c101'}
#     mock_api_endpoints.search_urls.assert_not_called()
    
# # Case: cache compare more
# def test_cache_compare_more(mock_api_endpoints, mock_get_urls, mock_flip_cache, monkeypatch):
#     mock_api_endpoints.quiz_cache = {'q1' : {'title': 'Quiz 1', 'type': 'graded', 'course_id': 'c101'},}

#     def mock_search_urls(url, course_id):
#         if course_id == 'c102':
#             mock_api_endpoints.quiz_cache['q2'] = {'title': 'Quiz 2', 'type': 'graded', 'course_id': 'c102'}

#     mock_api_endpoints.search_urls = MagicMock(side_effect=mock_search_urls)

#     result = resolvers.resolve_url(['c101', 'c102'], ['q1', 'q2'])

#     updated_cache = {'q1' : {'title': 'Quiz 1', 'type': 'graded', 'course_id': 'c101'},
#                      'q2' : {'title': 'Quiz 2', 'type': 'graded', 'course_id': 'c102'}}
#     monkeypatch.setattr(mock_api_endpoints, 'quiz_cache', updated_cache)

#     assert mock_api_endpoints.quiz_cache == updated_cache

#     assert set(result) == {'c101', 'c102'}
#     assert mock_api_endpoints.search_urls.call_count == 4

# # Case: quiz not found
# def test_quiz_not_found(mock_api_endpoints, mock_get_urls, mock_flip_cache, monkeypatch):
#     mock_api_endpoints.quiz_cache = {}

#     def mock_search_urls(url, course_id):
#         if course_id == 'c101':
#             mock_api_endpoints.quiz_cache = {}

#     mock_api_endpoints.search_urls = MagicMock(side_effect=mock_search_urls)

#     result = resolvers.resolve_url(['c101'], ['q1'])

#     updated_cache = {}
#     monkeypatch.setattr(mock_api_endpoints, 'quiz_cache', updated_cache)

#     assert mock_api_endpoints.quiz_cache == updated_cache

#     assert set(result) == set()
#     assert mock_api_endpoints.search_urls.call_count == 2