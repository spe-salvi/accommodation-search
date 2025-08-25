# import pytest
# from unittest.mock import patch, MagicMock
# import utils.resolvers as resolvers
# import logging

# logging.basicConfig(level=logging.DEBUG)

# @pytest.fixture
# def mock_get_data():
#     with patch("utils.resolvers.get_data") as mock:
#         yield mock

# @pytest.fixture
# def mock_load_user_cache():
#     with patch("utils.resolvers.load_user_cache") as mock:
#         yield mock

# @pytest.fixture
# def mock_save_course_cache():
#     with patch("utils.resolvers.save_course_cache") as mock:
#         yield mock

# @pytest.fixture
# def mock_flip_cache():
#     with patch("utils.resolvers.flip_cache", return_value={"123": "456"}) as mock:
#         yield mock

# # user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': (course_id, course_id, course_id)}, ...}

# # Case: input term is none and user is none
# def test_terms_none_users_none(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     resolvers.resolve_enrollments(None, None)
#     assert not mock_get_data.called

# # Case: input term is empty and user is empty
# def test_terms_empty_users_empty(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     resolvers.resolve_enrollments([], [])
#     assert not mock_get_data.called

# # Case: input term is one and user is one
# def test_terms_empty_users_empty(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     resolvers.resolve_enrollments([111], [1234])
#     assert mock_get_data.call_count == 2

# # Case: input term is many and user is one
# def test_multiple_terms_for_one_user(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [None, {"123": {"courses": ["101"]}}]
#     resolvers.resolve_enrollments(["2025F", "2025S"], ["123"])
#     assert mock_get_data.call_count == 3

# # Case: user cache is none
# def test_user_cache_is_none(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [None, {"123": {"courses": ["101"]}}]
#     resolvers.resolve_enrollments(["2025F"], ["123"])
#     assert mock_get_data.call_count == 2

# # Case: user cache is empty
# def test_user_cache_is_empty_dict(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [{}, {"123": {"courses": ["999"]}}]
#     resolvers.resolve_enrollments(["2025F"], ["123"])
#     assert mock_get_data.call_count == 2

# # Case: user already in cache
# def test_user_already_in_cache(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [{"123": {"courses": ["101"]}}, {"123": {"courses": ["101"]}}]
#     resolvers.resolve_enrollments(["2025F"], ["123"])
#     assert not mock_get_data.called

# # Case: empty written to cache
# def test_empty_list_saved_to_cache(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [{"123": {"courses": []}}, {"123": {"courses": []}}]
#     resolvers.resolve_enrollments(["2025F"], ["123"])
#     assert not mock_get_data.called

# # Case: cache compare more
# def test_cache_compare_more(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [
#         {"111": {"courses": ["101"]}},
#         {
#             "111": {"courses": ["101"]},
#             "222": {"courses": ["102"]}
#         }
#     ]
#     resolvers.resolve_enrollments(["2025F"], ["111", "222"])
#     assert mock_get_data.call_count == 2

# # Case: user cache none and term input none
# def test_terms_none_and_cache_none(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache):
#     mock_load_user_cache.side_effect = [None, {"789": {"courses": ["301"]}}]
#     resolvers.resolve_enrollments(None, ["789"])
#     assert mock_get_data.call_count == 2

# # Case: user not found
# def test_user_not_found(mock_get_data, mock_load_user_cache, mock_flip_cache, mock_save_course_cache, caplog):
#     mock_load_user_cache.side_effect = [{"not_in_list": {}}, {"not_in_list": {}}]
#     with caplog.at_level(logging.INFO):
#         resolvers.resolve_enrollments(["2025F"], ["u1"])
#     assert mock_get_data.call_count == 2
#     assert any("The user (u1) was not found." in message for message in caplog.messages)