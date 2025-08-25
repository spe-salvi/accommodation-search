from quizzes.quizzes import is_accommodated
import utils.cache_manager as cache_manager
import utils.getters as getters
import pandas as pd

course_id_df, quiz_id_df, user_id_df, accom_type_df, accom_date_df, quiz_type_df = [], [], [], [], [], []

def cache_to_df(accom_type, date_filter):
    # Break into new function
    # Pull from course cache
    cids, qids, uids = [], [], []
    course_cache = cache_manager.load_course_cache()
    for cid in course_cache.keys():
        for qid in course_cache[cid].get('quizzes', []):
            for uid in course_cache[cid].get('users', []):
                cids.append(cid)
                qids.append(qid)
                uids.append(uid)
    build_df(cids, qids, uids, accom_type, date_filter)

def build_df(course_ids, quiz_ids, user_ids, accom_type, date_filter):

    accom_checks = ['time', 'attempts'] if accom_type == 'both' else [accom_type]
    quiz_types = ['classic', 'new']

    for course_id in course_ids:
        for quiz_id in quiz_ids:
            for user_id in user_ids:
                for check_type in accom_checks:
                    for quiz_type in quiz_types:
                        accom_data = is_accommodated(course_id, quiz_id, user_id, check_type)

                        if not accom_data[0]:
                            continue  # Not accommodated, skip

                        accom_date = accom_data[1]
                        if date_filter != 'both' and accom_date != date_filter:
                            continue  # Date doesn't match filter

                        # Append to DF lists
                        compile_df_values(course_id, quiz_id, user_id, accom_type, accom_date, quiz_type)



def compile_df_values(course_id, quiz_id, user_id, accom_type, accom_date, quiz_type):
    global course_id_df, quiz_id_df, user_id_df, accom_type_df, accom_date_df, quiz_type_df
    print('add_to_df')
    course_id_df.append(course_id)
    # sis_id = get_course_sis_id(course_id)
    # course_sis_id_df.append(sis_id)
    quiz_id_df.append(quiz_id)
    # quiz_title_df.append(get_quiz_title(course_id, quiz_id, quiz_type))
    user_id_df.append(user_id)
    # user_name_df.append(get_user_name(user_id))
    # user_sis_id_df.append(get_user_sis_id(user_id))
    accom_type_df.append(accom_type)
    accom_date_df.append(accom_date)
    quiz_type_df.append(quiz_type)
    # 'Course ID': course_ids,
    # 'Course Code': course_codes,
    # 'Quiz ID': quiz_ids,
    # 'Quiz Titles': quiz_titles,
    # 'User IDs': user_ids,
    # 'Accommodation': accom_types,
    # 'Quiz Date': accom_datas
def create_df():
    # Get the original dataframes
    course_df = getters.get_course_df().reset_index().rename(columns={'index':'Course ID'})
    user_df = getters.get_user_df().reset_index().rename(columns={'index':'User ID'})
    quiz_df = getters.get_quiz_df().reset_index().rename(columns={'index':'Quiz ID'})
    submission_df = getters.get_submission_df()

    # Pull just the unique course-level info (code & name) by dropping the duplicates
    course_info = course_df[['Course ID', 'Course Code', 'Course Name']].drop_duplicates()

    # Merge submission rows with course metadata
    final_df = submission_df.merge(course_info, on='Course ID', how='left')

    # Bring in user details
    final_df = final_df.merge(
        user_df[['User ID','Sortable Name','SIS User ID','Email']], 
        on='User ID', 
        how='left'
    )

    # Bring in quiz details; course association already exists via submission_df
    final_df = final_df.merge(
        quiz_df[['Quiz ID','Title','Type']], 
        on='Quiz ID', 
        how='left'
    )

    # Optional: Order columns for readability
    final_df = final_df[[
        'User ID', 'Sortable Name', 'SIS User ID', 'Email',
        'Course ID', 'Course Code', 'Course Name',
        'Quiz ID', 'Title', 'Type',
        'Extra Time', 'Extra Attempts', 'Date'
    ]]

    return final_df
