# import pytest
# from unittest.mock import patch
# import utils.resolvers as resolvers
# import api.api_params as api_params
# import utils.paginate
# import api.api_endpoints as api_endpoints

# @pytest.fixture(autouse=True)
# def clean_cache_files():
#     """Automatically clean up cache files before each test"""
#     print("🧹 Cleaning up cache files...")
#     import os
#     for cache_file in ['term_cache.json', 'course_cache.json', 'user_cache.json']:
#         if os.path.exists(cache_file):
#             os.remove(cache_file)
#     yield  # this is where the test runs
#     # Optionally clean up after the test too
#     for cache_file in ['term_cache.json', 'course_cache.json', 'user_cache.json']:
#         if os.path.exists(cache_file):
#             os.remove(cache_file)


# def test_resolve_terms_debug(caplog):
#     term_id = "113"  # Spring 2024 term
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test...")
    
#     # First ensure the cache is empty
#     resolvers.term_cache = {}
    
#     # Define the real API URLs
#     test_urls = {
#         'term': [f'https://franciscan.instructure.com/api/v1/accounts/1/terms/{term_id}', {}],
#         'courses': [f'https://franciscan.instructure.com/api/v1/courses', {"enrollment_term_id": term_id}]
#     }
    
#     # Only patch cache operations and provide real URLs
#     # Create spy functions that wrap the real endpoint functions
#     original_term_func = api_params.function_dict['term']
#     original_courses_func = api_params.function_dict['courses']
    
#     def spy_term_func(*args, **kwargs):
#         spy_term_func.call_count += 1
#         spy_term_func.call_args_list.append((args, kwargs))
#         return original_term_func(*args, **kwargs)
    
#     def spy_courses_func(*args, **kwargs):
#         spy_courses_func.call_count += 1
#         spy_courses_func.call_args_list.append((args, kwargs))
#         return original_courses_func(*args, **kwargs)
    
#     # Initialize call tracking
#     spy_term_func.call_count = 0
#     spy_term_func.call_args_list = []
#     spy_courses_func.call_count = 0
#     spy_courses_func.call_args_list = []
    
#     # Replace the functions in the dictionary
#     api_params.function_dict['term'] = spy_term_func
#     api_params.function_dict['courses'] = spy_courses_func
#     real_load_term_cache = utils.cache_manager.load_term_cache
#     def load_term_cache_side_effect():
#         if not hasattr(load_term_cache_side_effect, "called"):
#             load_term_cache_side_effect.called = True
#             return {}
#         return real_load_term_cache()

#     with patch("utils.resolvers.load_term_cache", side_effect=load_term_cache_side_effect) as mock_load_cache, \
#         patch("api.api_params.get_urls", return_value=test_urls), \
#         patch("utils.resolvers.get_data", wraps=api_params.get_data) as spy_get_data, \
#         patch("utils.retry_request.paginatedGet", wraps=utils.paginate.paginatedGet) as spy_paginated_get:

#         print("🚀 About to call resolve_terms...")
#         result = resolvers.resolve_terms([term_id])
#         print(f"✅ resolve_terms returned: {result}")

#         # Check call counts
#         print(f"📊 Call counts:")
#         print(f"  - load_term_cache: {mock_load_cache.call_count}")
#         print(f"  - get_data: {spy_get_data.call_count}")
#         print(f"  - paginatedGet: {spy_paginated_get.call_count}")

#         # Print all logs
#         print("📜 All captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print the actual calls made
#         if spy_get_data.call_count > 0:
#             print("\n🌐 Actual API calls made:")
#             for call in spy_get_data.call_args_list:
#                 search_type, kwargs = call[0], call[1]
#                 print(f"   Type: {search_type}")
#                 print(f"   Args: {kwargs}")
                
#         # Print endpoint function calls
#         print("\n🔄 Endpoint function calls:")
#         print(f"   endpoint_term calls: {spy_term_func.call_count}")
#         if spy_term_func.call_count > 0:
#             print("   Term endpoint data:")
#             for call in spy_term_func.call_args_list:
#                 args, kwargs = call
#                 # print(f"     - Data: {args[0] if args else None}")
#                 print(f"     - Args: {kwargs}")
                
#         print(f"   endpoint_courses calls: {spy_courses_func.call_count}")
#         if spy_courses_func.call_count > 0:
#             print("   Courses endpoint data:")
#             for call in spy_courses_func.call_args_list:
#                 args, kwargs = call
#                 # print(f"     - Data: {args[0] if args else None}")
#                 print(f"     - Args: {kwargs}")

#         # Print the global term cache state
#         print("\n📦 Term cache state after execution:")
#         print(f"   {api_endpoints.term_cache}")

#         # Assertions
#         assert spy_get_data.call_count > 0, "get_data should have been called"
#         assert spy_paginated_get.call_count > 0, "paginatedGet should have been called"
#         assert spy_term_func.call_count > 0, "endpoint_term should have been called"
#         assert spy_courses_func.call_count > 0, "endpoint_courses should have been called"
#         assert isinstance(result, dict), "Result should be a dictionary"
#         assert term_id in result, f"Result should contain term_id {term_id}"
        
#         # Check if data actually made it to the term cache
#         assert api_endpoints.term_cache, "Term cache should not be empty after execution"
#         assert term_id in api_endpoints.term_cache, f"Term {term_id} should be in the term cache"


# def test_resolve_cids_debug(caplog):
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test...")
    
#     # First ensure the cache is empty
#     resolvers.term_cache = {}
    
#     test_url = {
#         'courses': [f'https://franciscan.instructure.com/api/v1/courses', {}]
#     }

#     original_courses_func = api_params.function_dict['courses']

    
#     def spy_courses_func(*args, **kwargs):
#         spy_courses_func.call_count += 1
#         spy_courses_func.call_args_list.append((args, kwargs))
#         return original_courses_func(*args, **kwargs)
    
#     spy_courses_func.call_count = 0
#     spy_courses_func.call_args_list = []

#     api_params.function_dict['courses'] = spy_courses_func
#     real_load_term_cache = utils.cache_manager.load_term_cache

#     def load_term_cache_side_effect():
#         if not hasattr(load_term_cache_side_effect, "called"):
#             load_term_cache_side_effect.called = True
#             return {}
#         return real_load_term_cache()

#     with patch("utils.resolvers.load_term_cache", side_effect=load_term_cache_side_effect) as mock_load_cache, \
#         patch("api.api_params.get_urls", return_value=test_url), \
#         patch("utils.resolvers.get_data", wraps=api_params.get_data) as spy_get_data, \
#         patch("utils.retry_request.paginatedGet", wraps=utils.paginate.paginatedGet) as spy_paginated_get:

#         print("🚀 About to call resolve_cids...")
#         result = resolvers.resolve_cids()
#         print(f"✅ resolve_cids returned: {result}")

#         # Check call counts
#         print(f"📊 Call counts:")
#         print(f"  - load_term_cache: {mock_load_cache.call_count}")
#         print(f"  - get_data: {spy_get_data.call_count}")
#         print(f"  - paginatedGet: {spy_paginated_get.call_count}")

#         # Print all logs
#         print("📜 All captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print the actual calls made
#         if spy_get_data.call_count > 0:
#             print("\n🌐 Actual API calls made:")
#             for call in spy_get_data.call_args_list:
#                 search_type, kwargs = call[0], call[1]
#                 print(f"   Type: {search_type}")
#                 print(f"   Args: {kwargs}")

#                 # Print endpoint function calls
#         print("\n🔄 Endpoint function calls:")                
#         print(f"   endpoint_courses calls: {spy_courses_func.call_count}")
#         if spy_courses_func.call_count > 0:
#             print("   Courses endpoint data:")
#             for call in spy_courses_func.call_args_list:
#                 args, kwargs = call
#                 # print(f"     - Data: {args[0] if args else None}")
#                 print(f"     - Args: {kwargs}")

#                 # Print the global term cache state
#         print("\n📦 Term cache state after execution:")
#         print(f"   {api_endpoints.term_cache}")

#         # Assertions
#         assert spy_get_data.call_count > 0, "get_data should have been called"
#         assert spy_paginated_get.call_count > 0, "paginatedGet should have been called"
#         assert spy_courses_func.call_count > 0, "endpoint_courses should have been called"
#         assert isinstance(result, list), "Result should be a list"

#         # Check if data actually made it to the term cache
#         assert api_endpoints.term_cache, "Term cache should not be empty after execution"

# def test_resolve_qids_one_debug(caplog):
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test...")
    
#     # First ensure the cache is empty
#     resolvers.course_cache = {}
    
#     test_url = {
#         'c_quizzes': [f'https://franciscan.instructure.com/api/v1/courses/10348/quizzes', {}],
#         'n_quizzes': [f'https://franciscan.instructure.com/api/quiz/v1/courses/10348/quizzes', {}],
#     }

#     original_c_quizzes_func = api_params.function_dict['c_quizzes']
#     original_n_quizzes_func = api_params.function_dict['n_quizzes']

#     def spy_c_quizzes_func(*args, **kwargs):
#         spy_c_quizzes_func.call_count += 1
#         spy_c_quizzes_func.call_args_list.append((args, kwargs))
#         return original_c_quizzes_func(*args, **kwargs)

#     def spy_n_quizzes_func(*args, **kwargs):
#         spy_n_quizzes_func.call_count += 1
#         spy_n_quizzes_func.call_args_list.append((args, kwargs))
#         return original_n_quizzes_func(*args, **kwargs)

#     spy_c_quizzes_func.call_count = 0
#     spy_c_quizzes_func.call_args_list = []

#     spy_n_quizzes_func.call_count = 0
#     spy_n_quizzes_func.call_args_list = []

#     api_params.function_dict['c_quizzes'] = spy_c_quizzes_func
#     api_params.function_dict['n_quizzes'] = spy_n_quizzes_func
#     real_load_course_cache = utils.cache_manager.load_course_cache

#     def load_course_cache_side_effect():
#         if not hasattr(load_course_cache_side_effect, "called"):
#             load_course_cache_side_effect.called = True
#             return {}
#         return real_load_course_cache()

#     with patch("utils.resolvers.load_course_cache", side_effect=load_course_cache_side_effect) as mock_load_cache, \
#         patch("api.api_params.get_urls", return_value=test_url), \
#         patch("utils.resolvers.get_data", wraps=api_params.get_data) as spy_get_data, \
#         patch("utils.retry_request.paginatedGet", wraps=utils.paginate.paginatedGet) as spy_paginated_get:

#         print("🚀 About to call resolve_qids...")
#         result = resolvers.resolve_qids(['10348'])
#         print(f"✅ resolve_qids returned: {result}")

#         # Check call counts
#         print(f"📊 Call counts:")
#         print(f"  - load_course_cache: {mock_load_cache.call_count}")
#         print(f"  - get_data: {spy_get_data.call_count}")
#         print(f"  - paginatedGet: {spy_paginated_get.call_count}")

#         # Print all logs
#         print("📜 All captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print the actual calls made
#         if spy_get_data.call_count > 0:
#             print("\n🌐 Actual API calls made:")
#             for call in spy_get_data.call_args_list:
#                 search_type, kwargs = call[0], call[1]
#                 print(f"   Type: {search_type}")
#                 print(f"   Args: {kwargs}")

#                 # Print endpoint function calls
#         print("\n🔄 Endpoint function calls:")
#         print(f"   endpoint_quizzes calls: {spy_c_quizzes_func.call_count + spy_n_quizzes_func.call_count}")

#         if spy_c_quizzes_func.call_count > 0 or spy_n_quizzes_func.call_count > 0:
#             print("   Quizzes endpoint data:")
#             if spy_c_quizzes_func.call_count > 0:
#                 print("   c_quizzes calls:")
#                 for call in spy_c_quizzes_func.call_args_list:
#                     args, kwargs = call
#                     print(f"     - Args: {kwargs}")
#             if spy_n_quizzes_func.call_count > 0:
#                 print("   n_quizzes calls:")
#                 for call in spy_n_quizzes_func.call_args_list:
#                     args, kwargs = call
#                     print(f"     - Args: {kwargs}")

#                 # Print the global course cache state
#         print("\n📦 Course cache state after execution:")
#         print(f"   {api_endpoints.course_cache}")

#         # Assertions
#         assert spy_get_data.call_count > 0, "get_data should have been called"
#         assert spy_paginated_get.call_count > 0, "paginatedGet should have been called"
#         assert spy_c_quizzes_func.call_count > 0, "endpoint_quizzes for classic should have been called"
#         assert spy_n_quizzes_func.call_count > 0, "endpoint_quizzes for new should have been called"

#         # Check if data actually made it to the course cache
#         assert api_endpoints.course_cache, "Course cache should not be empty after execution"

# def test_resolve_qids_two_debug(caplog):
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test...")
    
#     # First ensure the cache is empty
#     resolvers.course_cache = {}
    
#     test_url = {
#         'c_quizzes': [f'https://franciscan.instructure.com/api/v1/courses/10281/quizzes', {}],
#         'n_quizzes': [f'https://franciscan.instructure.com/api/quiz/v1/courses/10281/quizzes', {}],
#     }

#     original_c_quizzes_func = api_params.function_dict['c_quizzes']
#     original_n_quizzes_func = api_params.function_dict['n_quizzes']

#     def spy_c_quizzes_func(*args, **kwargs):
#         spy_c_quizzes_func.call_count += 1
#         spy_c_quizzes_func.call_args_list.append((args, kwargs))
#         return original_c_quizzes_func(*args, **kwargs)

#     def spy_n_quizzes_func(*args, **kwargs):
#         spy_n_quizzes_func.call_count += 1
#         spy_n_quizzes_func.call_args_list.append((args, kwargs))
#         return original_n_quizzes_func(*args, **kwargs)

#     spy_c_quizzes_func.call_count = 0
#     spy_c_quizzes_func.call_args_list = []

#     spy_n_quizzes_func.call_count = 0
#     spy_n_quizzes_func.call_args_list = []

#     api_params.function_dict['c_quizzes'] = spy_c_quizzes_func
#     api_params.function_dict['n_quizzes'] = spy_n_quizzes_func
#     real_load_course_cache = utils.cache_manager.load_course_cache

#     def load_course_cache_side_effect():
#         if not hasattr(load_course_cache_side_effect, "called"):
#             load_course_cache_side_effect.called = True
#             return {}
#         return real_load_course_cache()

#     with patch("utils.resolvers.load_course_cache", side_effect=load_course_cache_side_effect) as mock_load_cache, \
#         patch("api.api_params.get_urls", return_value=test_url), \
#         patch("utils.resolvers.get_data", wraps=api_params.get_data) as spy_get_data, \
#         patch("utils.retry_request.paginatedGet", wraps=utils.paginate.paginatedGet) as spy_paginated_get:

#         print("🚀 About to call resolve_qids...")
#         result = resolvers.resolve_qids(['10281'])
#         print(f"✅ resolve_qids returned: {result}")

#         # Check call counts
#         print(f"📊 Call counts:")
#         print(f"  - load_course_cache: {mock_load_cache.call_count}")
#         print(f"  - get_data: {spy_get_data.call_count}")
#         print(f"  - paginatedGet: {spy_paginated_get.call_count}")

#         # Print all logs
#         print("📜 All captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print the actual calls made
#         if spy_get_data.call_count > 0:
#             print("\n🌐 Actual API calls made:")
#             for call in spy_get_data.call_args_list:
#                 search_type, kwargs = call[0], call[1]
#                 print(f"   Type: {search_type}")
#                 print(f"   Args: {kwargs}")

#                 # Print endpoint function calls
#         print("\n🔄 Endpoint function calls:")
#         print(f"   endpoint_quizzes calls: {spy_c_quizzes_func.call_count + spy_n_quizzes_func.call_count}")

#         if spy_c_quizzes_func.call_count > 0 or spy_n_quizzes_func.call_count > 0:
#             print("   Quizzes endpoint data:")
#             if spy_c_quizzes_func.call_count > 0:
#                 print("   c_quizzes calls:")
#                 for call in spy_c_quizzes_func.call_args_list:
#                     args, kwargs = call
#                     print(f"     - Args: {kwargs}")
#             if spy_n_quizzes_func.call_count > 0:
#                 print("   n_quizzes calls:")
#                 for call in spy_n_quizzes_func.call_args_list:
#                     args, kwargs = call
#                     print(f"     - Args: {kwargs}")

#                 # Print the global course cache state
#         print("\n📦 Course cache state after execution:")
#         print(f"   {api_endpoints.course_cache}")

#         # Assertions
#         assert spy_get_data.call_count > 0, "get_data should have been called"
#         assert spy_paginated_get.call_count > 0, "paginatedGet should have been called"
#         assert spy_c_quizzes_func.call_count > 0, "endpoint_quizzes for classic should have been called"
#         assert spy_n_quizzes_func.call_count > 0, "endpoint_quizzes for new should have been called"

#         # Check if data actually made it to the course cache
#         assert api_endpoints.course_cache, "Course cache should not be empty after execution"

# def test_resolve_uids_debug(caplog):
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test...")
    
#     # First ensure the cache is empty
#     resolvers.course_cache = {}
    
#     test_url = {
#         'course_users': [f'https://franciscan.instructure.com/api/v1/courses/10281/users', {}],
#     }

#     original_course_users_func = api_params.function_dict['course_users']

#     def spy_course_users_func(*args, **kwargs):
#         spy_course_users_func.call_count += 1
#         spy_course_users_func.call_args_list.append((args, kwargs))
#         return original_course_users_func(*args, **kwargs)

#     spy_course_users_func.call_count = 0
#     spy_course_users_func.call_args_list = []

#     api_params.function_dict['course_users'] = spy_course_users_func
#     real_load_course_cache = utils.cache_manager.load_course_cache

#     def load_course_cache_side_effect():
#         if not hasattr(load_course_cache_side_effect, "called"):
#             load_course_cache_side_effect.called = True
#             return {}
#         return real_load_course_cache()

#     with patch("utils.resolvers.load_course_cache", side_effect=load_course_cache_side_effect) as mock_load_cache, \
#         patch("api.api_params.get_urls", return_value=test_url), \
#         patch("utils.resolvers.get_data", wraps=api_params.get_data) as spy_get_data, \
#         patch("utils.retry_request.paginatedGet", wraps=utils.paginate.paginatedGet) as spy_paginated_get:

#         print("🚀 About to call resolve_uids...")
#         result = resolvers.resolve_uids(['10281'])
#         print(f"✅ resolve_uids returned: {result}")

#         # Check call counts
#         print(f"📊 Call counts:")
#         print(f"  - load_course_cache: {mock_load_cache.call_count}")
#         print(f"  - get_data: {spy_get_data.call_count}")
#         print(f"  - paginatedGet: {spy_paginated_get.call_count}")

#         # Print all logs
#         print("📜 All captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print the actual calls made
#         if spy_get_data.call_count > 0:
#             print("\n🌐 Actual API calls made:")
#             for call in spy_get_data.call_args_list:
#                 search_type, kwargs = call[0], call[1]
#                 print(f"   Type: {search_type}")
#                 print(f"   Args: {kwargs}")

#                 # Print endpoint function calls
#         print("\n🔄 Endpoint function calls:")
#         print(f"   endpoint_quizzes calls: {spy_course_users_func.call_count}")

#         if spy_course_users_func.call_count > 0:
#             print("   course_users calls:")
#             for call in spy_course_users_func.call_args_list:
#                 args, kwargs = call
#                 print(f"     - Args: {kwargs}")

#                 # Print the global course cache state
#         print("\n📦 Course cache state after execution:")
#         print(f"   {api_endpoints.course_cache}")

#         # Assertions
#         assert spy_get_data.call_count > 0, "get_data should have been called"
#         assert spy_paginated_get.call_count > 0, "paginatedGet should have been called"
#         assert spy_course_users_func.call_count > 0, "endpoint_course_users should have been called"

#         # Check if data actually made it to the course cache
#         assert api_endpoints.course_cache, "Course cache should not be empty after execution"

# def test_resolve_enrollments_debug(caplog):
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test...")
    
#     # First ensure the cache is empty
#     resolvers.user_cache = {}
    
#     test_url = {
#         'enrollments': [f'https://franciscan.instructure.com/api/v1/users/14172/enrollments', {}],
#         'users': [f'https://franciscan.instructure.com/api/v1/users/14172', {}],
#     }

#     original_enrollments_func = api_params.function_dict['enrollments']
#     original_users_func = api_params.function_dict['users']

#     def spy_enrollments_func(*args, **kwargs):
#         spy_enrollments_func.call_count += 1
#         spy_enrollments_func.call_args_list.append((args, kwargs))
#         return original_enrollments_func(*args, **kwargs)

#     def spy_users_func(*args, **kwargs):
#         spy_users_func.call_count += 1
#         spy_users_func.call_args_list.append((args, kwargs))
#         return original_users_func(*args, **kwargs)

#     spy_enrollments_func.call_count = 0
#     spy_enrollments_func.call_args_list = []

#     spy_users_func.call_count = 0
#     spy_users_func.call_args_list = []

#     api_params.function_dict['enrollments'] = spy_enrollments_func
#     api_params.function_dict['users'] = spy_users_func
#     real_load_user_cache = utils.cache_manager.load_user_cache

#     def load_user_cache_side_effect():
#         if not hasattr(load_user_cache_side_effect, "called"):
#             load_user_cache_side_effect.called = True
#             return {}
#         return real_load_user_cache()

#     with patch("utils.resolvers.load_user_cache", side_effect=load_user_cache_side_effect) as mock_load_cache, \
#         patch("api.api_params.get_urls", return_value=test_url), \
#         patch("utils.resolvers.get_data", wraps=api_params.get_data) as spy_get_data, \
#         patch("utils.retry_request.paginatedGet", wraps=utils.paginate.paginatedGet) as spy_paginated_get:

#         print("🚀 About to call resolve_enrollments...")
#         result = resolvers.resolve_enrollments(['115'], ['14172'])
#         print(f"✅ resolve_enrollments returned: {result}")

#         # Check call counts
#         print(f"📊 Call counts:")
#         print(f"  - load_user_cache: {mock_load_cache.call_count}")
#         print(f"  - get_data: {spy_get_data.call_count}")
#         print(f"  - paginatedGet: {spy_paginated_get.call_count}")

#         # Print all logs
#         print("📜 All captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print the actual calls made
#         if spy_get_data.call_count > 0:
#             print("\n🌐 Actual API calls made:")
#             for call in spy_get_data.call_args_list:
#                 search_type, kwargs = call[0], call[1]
#                 print(f"   Type: {search_type}")
#                 print(f"   Args: {kwargs}")

#                 # Print endpoint function calls
#         print("\n🔄 Endpoint function calls:")
#         print(f"   endpoint_enrollments calls: {spy_enrollments_func.call_count + spy_users_func.call_count}")

#         if spy_enrollments_func.call_count > 0 or spy_users_func.call_count > 0:
#             print("   Quizzes endpoint data:")
#             if spy_enrollments_func.call_count > 0:
#                 print("   enrollments calls:")
#                 for call in spy_enrollments_func.call_args_list:
#                     args, kwargs = call
#                     print(f"     - Args: {kwargs}")
#             if spy_users_func.call_count > 0:
#                 print("   users calls:")
#                 for call in spy_users_func.call_args_list:
#                     args, kwargs = call
#                     print(f"     - Args: {kwargs}")

#                 # Print the global user cache state
#         print("\n📦 User cache state after execution:")
#         print(f"   {api_endpoints.user_cache}")

#         # Assertions
#         assert spy_get_data.call_count > 0, "get_data should have been called"
#         assert spy_paginated_get.call_count > 0, "paginatedGet should have been called"
#         assert spy_enrollments_func.call_count > 0, "endpoint_enrollments should have been called"
#         assert spy_users_func.call_count > 0, "endpoint_users should have been called"

#         # Check if data actually made it to the user cache
#         assert api_endpoints.user_cache, "User cache should not be empty after execution"
#         assert api_endpoints.course_cache, "Course cache should not be empty after execution"


# def test_resolve_url_debug(caplog):
#     caplog.set_level("DEBUG")

#     print("🔍 Starting test for resolve_url...")

#     # Reset caches
#     api_endpoints.quiz_cache.clear()
#     api_endpoints.course_cache.clear()

#     # Define test data
#     course_ids = ['10348', '10281']
#     quiz_ids = ['40122', '153548']

#     def mock_get_urls_side_effect(term_id=None, course_id=None, quiz_id=None, user_id=None):
#         return {
#             'c_quiz': f"https://franciscan.instructure.com/api/v1/courses/{course_id}/quizzes/{quiz_id}",
#             'n_quiz': f"https://franciscan.instructure.com/api/quiz/v1/courses/{course_id}/quizzes/{quiz_id}"
#         }
    
#     # Patch dependencies
#     with patch("utils.resolvers.get_urls", side_effect=mock_get_urls_side_effect) as mock_get_urls, \
#          patch("api.api_endpoints.search_urls") as mock_search_urls, \
#          patch("utils.resolvers.load_course_cache", return_value={}) as mock_load_cache, \
#          patch("utils.resolvers.save_course_cache") as mock_save_cache, \
#          patch("utils.resolvers.flip_quiz_cache", wraps=resolvers.flip_quiz_cache) as spy_flip_quiz_cache:


#         # Simulate quiz_cache having one quiz already mapped
#         api_endpoints.quiz_cache['40122'] = {'course_id': '10348'}

#         print("🚀 Calling resolve_url...")
#         result = resolvers.resolve_url(course_ids, quiz_ids)
#         print(f"✅ resolve_url returned: {result}")

#         # Assertions
#         print("\n📊 Verifying mocks and side effects...")
#         assert mock_get_urls.call_count > 0, "get_urls should have been called"
#         assert mock_search_urls.call_count >= 2, "search_urls should have been called for uncached courses"
#         assert spy_flip_quiz_cache.call_count == 1, "flip_quiz_cache should have been called exactly once"
#         assert mock_load_cache.call_count > 0, "load_course_cache should have been called"
#         assert mock_save_cache.call_count > 0, "save_course_cache should have been called"

#         # Ensure that the cached course ('101') was not re-fetched
#         searched_courses = [call.args[1] for call in mock_search_urls.call_args_list]
#         assert '10281' in searched_courses, "Course '10281' should have been searched because it wasn't cached"

#         # Print logs
#         print("📜 Captured logs:")
#         for record in caplog.records:
#             print(f"   {record.levelname}: {record.getMessage()}")

#         # Print captured API calls
#         print("\n🌐 API calls to search_urls:")
#         for call in mock_search_urls.call_args_list:
#             print(f"   Called with: {call.args}")

#         print("\n📦 Final quiz cache:")
#         print(api_endpoints.quiz_cache)

#         # Check final linked courses
#         assert '10348' in result, "Course 10348 should be in result (from cache)"
#         assert '10281' in result or mock_search_urls.call_count > 0, "Course 10281 should be resolved via API search"