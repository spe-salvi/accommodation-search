# from utils.dataframe_utils import cache_to_df, build_df
# from utils.cache_manager import *
# from api.api_params import get_data, get_urls
# import api.api_endpoints as api_endpoints
# import logging
# import requests
# import config.config as config

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def resolve_search_params(cleaned_input:list):
#     terms, course_ids, quiz_ids, user_ids, accom_type, date_filter = cleaned_input
#     cids = []

#     if course_ids:
#         logger.info(f"Resolving course IDs: {course_ids}")
#         cids = test_course_id(course_ids)
#         logger.info(f"Resolved course IDs: {cids}")
#         logger.info(f'Resolving quiz IDs: {quiz_ids}')
#         resolve_qids(cids, quiz_ids)
#         logger.info(f'Resolving user IDs: {user_ids}')
#         resolve_uids(cids, user_ids)
#     elif user_ids:
#         logger.info(f'elif user_ids, Resolving enrollments for: {user_ids}')
#         resolve_enrollments(terms, user_ids) # TODO: Return only cids, not write to cache
#         logger.info(f'elif user_ids, Resolving quiz IDs: {quiz_ids}')
#         resolve_qids(cids, quiz_ids)
#     elif quiz_ids:
#         all_cids = []
#         if terms:
#             logger.info(f'elif quiz_ids, if terms, Resolving terms for: {terms}')
#             term_cache = resolve_terms(terms)
#             for key in term_cache:
#                 all_cids.extend(term_cache[key]['courses'])
#         else:
#             logger.info(f'if not terms, Resolving all course IDs')
#             all_cids = resolve_cids()
#         logger.info(f'elif quiz_ids, Resolved course IDs: {all_cids}')
#         logger.info(f'elif quiz_ids, Resolving url course IDs')
#         cids = resolve_url(all_cids, quiz_ids)
#         logger.info(f'elif quiz_ids, Resolved url course IDs: {cids}')
#         logger.info(f'elif quiz_ids, Resolving user IDs: {user_ids}')
#         resolve_uids(cids, user_ids)
#     logger.info('Cache to dataframe')
#     # Test below
#     build_df(course_ids, quiz_ids, user_ids, accom_type, date_filter)
#     # cache_to_df(accom_type, date_filter)

# # term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
# def resolve_terms(terms):
#     logger.info(f"Resolve_terms called with {terms}")
#     logger.info('Loading term cache 1')
#     term_cache = load_term_cache()

#     if not terms:
#         logger.info("No terms provided.")
#         return term_cache or {}
    
#     for i in range(len(terms)):
#         term = terms[i]
#         if term_cache:
#             if term not in term_cache:
#                 logger.info(f'Term {term} not in cache, fetching data.')
#                 get_data('term', term_id=term)
#                 get_data('courses', term_id=term)
#         else:
#             logger.info('No term cache found, fetching data for (all) term(s).')
#             get_data('term', term_id=term)
#             get_data('courses', term_id=term)
#     logger.info('Loading term cache 2')
#     term_cache = load_term_cache()
#     return term_cache

# # term_cache = {term_id: {'name': term_name, 'courses': (course_id, course_id, course_id)}, ...}
# def resolve_cids():
#     logger.info('Resolve_cids called')
#     logger.info('Loading course cache 1')
#     course_cache = load_course_cache()
#     if not course_cache:
#         logger.info('No course cache found, fetching data for all courses.')
#         get_data('courses')
#     logger.info('Loading course cache 2')
#     course_cache = load_course_cache()
#     course_ids = list(course_cache.keys())
#     return course_ids

# # course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
# def resolve_qids(course_ids, quiz_ids=None):
#     logger.info("Resolve_qids called")
#     if not course_ids:
#         return
#     logger.info('Loading course cache 1')
#     course_cache = load_course_cache()
#     for course_id in course_ids:
#         if course_cache and quiz_ids:
#             logger.info("Comparing quiz IDs to current cache")
#             if helper_cache_compare(course_cache, course_id, quiz_ids, 'quiz'):
#                 continue
#             else:
#                 logger.info("Quiz IDs not found in cache, fetching data.")
#                 get_data('c_quizzes', course_id=course_id)
#                 get_data('n_quizzes', course_id=course_id)
#         else:
#             logger.info("No course cache or quiz IDs found, fetching data.")
#             get_data('c_quizzes', course_id=course_id)
#             get_data('n_quizzes', course_id=course_id)
#     logger.info('Loading course cache 2')
#     course_cache = load_course_cache()
#     if quiz_ids and not any(helper_cache_compare(course_cache, course_id, quiz_ids, 'quiz') for course_id in course_ids):
#         logger.error(f'Some entered quizzes were not found.')
#     return

# def helper_cache_compare(course_cache, idx_id, para_ids, param_type):
#     logger.info("Helper_cache_compare called")
#     if not course_cache or not idx_id or not para_ids:
#         return False
#     if param_type == 'quiz':
#         quizzes = course_cache.get(idx_id, {}).get('quizzes', [])
#         diff = list(set(para_ids) - set(quizzes))
#         logger.info("Difference found in quizzes")
#     elif param_type == 'user':
#         users = course_cache.get(idx_id, {}).get('users', [])
#         diff = list(set(para_ids) - set(users))
#         logger.info("Difference found in users")

#     if diff == []:
#         logger.info("All IDs found in cache")
#         return True
#     return False

# # course_cache = {course_id: { 'code': course_code, 'name': course_name, 'term': term_id, 'users': [user_id, user_id, user_id], 'quizzes': [quiz_id, quiz_id, quiz_id]}, ...}
# def resolve_uids(course_ids, user_ids=None):
#     logger.info("Resolve_uids called")
#     if not course_ids:
#         return
#     logger.info('Loading course cache 1')
#     course_cache = load_course_cache()
#     for course_id in course_ids:
#         if course_cache and user_ids:
#             logger.info("Comparing user IDs to current cache")
#             if helper_cache_compare(course_cache, course_id, user_ids, 'user'):
#                 # print('pass')
#                 continue
#             else:
#                 logger.info("User IDs not found in cache, fetching data.")
#                 get_data('course_users', course_id=course_id)
#         else:
#             logger.info("No course cache or user IDs found, fetching data.")
#             get_data('course_users', course_id=course_id)
#     logger.info('Loading course cache 2')
#     course_cache = load_course_cache()
#     if user_ids and not any(helper_cache_compare(course_cache, course_id, user_ids, 'user') for course_id in course_ids):
#         logger.error(f'Some entered users were not found.')
#     return

# # user_cache = {user_id: {'name': sortable_name, 'sis_id': sis_user_id, 'email': email, 'courses': (course_id, course_id, course_id)}, ...}
# def resolve_enrollments(terms, user_ids):
#     logger.info("Resolve_enrollments called")
#     logger.info('Loading user cache 1')
#     user_cache = load_user_cache()
#     if not user_ids:
#         user_ids = []
#     logger.info(f"User IDs to resolve: {len(user_ids)}")
#     for user_id in user_ids:
#         if user_cache:
#             if user_id not in user_cache:
#                 if not terms:
#                     terms = [None]
#                 for j in range(len(terms)):
#                     term = terms[j]
#                     logger.info(f"user_cache:Fetching enrollments for user {user_id} in term {term}")
#                     get_data('enrollments', term_id=term, user_id=user_id)
#                 logger.info(f"user_cache: Fetching user data for user {user_id}")
#                 get_data('users', user_id=user_id)
#         else:
#             if not terms:
#                 terms = [None]
#             for j in range(len(terms)):
#                 term = terms[j]
#                 logger.info(f"no user_cache: Fetching enrollments for user {user_id} in term {term}")
#                 get_data('enrollments', term_id=term, user_id=user_id)
#             logger.info(f"no user_cache: Fetching user data for user {user_id}")
#             get_data('users', user_id=user_id)
#     logger.info('Loading user cache 2')
#     user_cache = load_user_cache()
#     for user_id in user_ids:
#         if user_id not in user_cache:
#             logger.error(f'The user ({user_id}) was not found.')
#     logger.info('Loading course cache')
#     course_cache = load_course_cache()
#     logger.info('Flipping user cache')
#     course_cache = flip_user_cache(user_cache, course_cache)
#     course_cache = load_course_cache()
#     logger.info('Saving course cache')
#     save_course_cache()
#     return

# # quiz_cache = {quiz_id: {'title':title, 'type':type, 'course_id':course_id}, ...}
# def resolve_url(course_ids, quiz_ids):
#     logger.info('Resolve_url called')
#     logger.info('Loading quiz cache')
#     quiz_cache = api_endpoints.quiz_cache
#     linked_course_ids = set()

#     if not quiz_ids or not course_ids:
#         return []

#     for quiz_id in quiz_ids:
#         # print(f'Quiz ID: {quiz_id}')
#         if quiz_id in quiz_cache:
#             course_id_in_cache = quiz_cache[quiz_id].get('course_id', None)
#             # print(f'CID in cache: {course_id_in_cache}')
#             for course_id in course_ids:
#                 # print('here')
#                 if ((course_id == course_id_in_cache)):
#                     # print('here2')
#                     linked_course_ids.add(course_id)
#     for course_id in course_ids:
#         if course_id not in linked_course_ids:
#             for quiz_id in quiz_ids:
#                 logger.info(f'Course not in quiz cache, fetching url')
#                 urls = get_urls(course_id=course_id, quiz_id=quiz_id)
#                 logger.info("Searching classic quiz URL")
#                 api_endpoints.search_urls(urls['c_quiz'], course_id)
#                 logger.info("Searching new quiz URL")
#                 api_endpoints.search_urls(urls['n_quiz'], course_id)

#     logger.info('Loading course cache')
#     course_cache = load_course_cache()
#     logger.info('Flipping quiz cache')
#     course_cache = flip_quiz_cache(quiz_cache, course_cache)
#     course_cache = load_course_cache()
#     logger.info('Saving course cache')
#     save_course_cache()

#     for quiz_id in quiz_ids:
#         if quiz_id in quiz_cache:
#             course_id = quiz_cache[quiz_id].get('course_id', None)
#             if course_id:
#                 linked_course_ids.add(course_id)

#     return list(linked_course_ids)

# def flip_user_cache(user_cache, existing_course_cache=None):
#     logger.info('Flipping user cache called')
#     course_cache = existing_course_cache or {}

#     for user_id, user_info in (user_cache or {}).items():
#         for course_id in user_info.get("courses", []):
#             c_cache = course_cache.setdefault(course_id, {
#                 "code": "",
#                 "name": "",
#                 "term": "",
#                 "users": [],
#                 "quizzes": []
#             })
#             if user_id not in c_cache["users"]:
#                 c_cache["users"].append(user_id)
                
#     return course_cache

# def flip_quiz_cache(quiz_cache, existing_course_cache=None):
#     logger.info('Flipping quiz cache called')
#     course_cache = dict(existing_course_cache) if existing_course_cache else {}

#     for quiz_id, quiz_info in (quiz_cache or {}).items():
#         course_id = quiz_info.get("course_id")
#         if not course_id:
#             continue
        
#         c_cache = course_cache.setdefault(course_id, {
#             "code": "",
#             "name": "",
#             "term": "",
#             "users": [],
#             "quizzes": []
#         })

#         if quiz_id not in c_cache["quizzes"]:
#             c_cache["quizzes"].append(quiz_id)

#     return course_cache

# def test_course_id(course_ids):
#     logger.info('Testing course IDs called')
#     cids = set()
#     logger.info('Loading course cache 1')
#     course_cache = load_course_cache()

#     for course_id in course_ids:
        
#         if course_id in course_cache:
#             cids.add(course_id)
#         else:
#             logger.info(f'Course ID {course_id} not found in cache, fetching from API')
#             url = get_urls(course_id=course_id)['course'][0]
#             logger.info(f'Fetching data from {url}')
#             response = requests.get(url, headers=config.HEADERS)
#             if response.status_code == 200:
#                 logger.info(f'Course ID {course_id} found, adding to cache')
#                 cids.add(course_id)

#     return cids

 















# ###############################################
#     # combos = set()
#     # resolved_course_ids = set()

#     # # STEP 1: Resolve course_ids
#     # if course_ids:
#     #     resolved_course_ids.update(course_ids)
#     # elif user_ids:
#     #     for user_id in user_ids:
#     #         for term in terms or [None]:
#     #             for user_id in endpoints.user_cache:
#     #                 resolved_course_ids.update(user_id[2])
#     #             else:
#     #                 enrollments = courses.get_data('enrollments', user_id=user_id, term_id=term)
#     #                 # resolved_course_ids.update(e['course_id'] for e in enrollments)
#     #                 # update from cache
#     # elif terms:
#     #     for term in terms:
#     #         resolved_course_ids.update(get_course_terms.narrow_courses(term))
#     #         # update from cache
#     # # else:
#     #     # search courses narrowed by quiz cache
#     #     # else search all courses
#     #     # cache
#     #     # narrow by quiz id if provided

#     # # STEP 2: Resolve quiz_ids and user_ids per course
#     # for c_id in resolved_course_ids:
#     #     quizzes = quiz_ids if quiz_ids else [
#     #         q['id'] for q in courses.get_data('quizzes', course_id=c_id)
#     #         #  update from cache
#     #     ]

#     #     users = user_ids if user_ids else [
#     #         u['id'] for u in courses.get_data('course_users', course_id=c_id)
#     #         # update from cache
#     #     ]

#     #     for q_id in quizzes:
#     #         for u_id in users:
#     #             combos.add((c_id, q_id, u_id))

#     # # STEP 3: Call build_df for each combination
#     # for c_id, q_id, u_id in combos:
#     #     df_utils.build_df(course_id=c_id, quiz_id=q_id, user_id=u_id)



# # def cases():
# #     for course_id in course_ids:
# #         if not quiz_ids:
# #             courses.get_data('c_quizzes', course_id=course_id)
# #             courses.get_data('n_quizzes', course_id=course_id)
# #             for quiz_id in endpoints.course_cache[course_id][2]:
# #                 quiz_ids.append(quiz_id)
# #             quiz_ids = list(set(quiz_ids))
# #         for quiz_id in quiz_ids:
# #             courses.get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)
# #             courses.get_data('n_quiz', course_id=course_id, quiz_id=quiz_id)
# #             if not user_ids:
# #                 courses.get_data('course_users', course_id=course_id)
# #                 for user_id in endpoints.course_cache[course_id][1]:
# #                     user_ids.append(user_id)
# #                 user_ids = list(set(user_ids))
# #                 for user_id in user_ids:
# #                     courses.get_data('users', user_id=user_id)
# #         df_utils.build_df()

# #     for term in terms:
# #         courses = get_course_terms.narrow_courses(term)
# #         for course_id in courses:
# #             if not quiz_ids:
# #                 courses.get_data('c_quizzes', course_id=course_id)
# #                 courses.get_data('n_quizzes', course_id=course_id)
# #                 for quiz_id in endpoints.course_cache[course_id][2]:
# #                     quiz_ids.append(quiz_id)
# #             quiz_ids = list(set(quiz_ids))
# #         for quiz_id in quiz_ids:
# #             courses.get_data('c_quiz', course_id=course_id, quiz_id=quiz_id)
# #             courses.get_data('n_quiz', course_id=course_id, quiz_id=quiz_id)
# #         if not user_ids:
# #             courses.get_data('course_users', course_id=course_id)
# #             for user_id in endpoints.course_cache[course_id][1]:
# #                 user_ids.append(user_id)
# #         df_utils.build_df()
# #     for quiz_id in quiz_ids:
# #         if not user_ids:
# #             courses.get_data('course_users', quiz_id=quiz_id)
# #             for user_id in endpoints.course_cache[quiz_id][1]:
# #                 user_ids.append(user_id)
# #         df_utils.build_df()
# #     for user_id in user_ids:

