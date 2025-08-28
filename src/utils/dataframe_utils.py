from quizzes.quizzes import is_accommodated
import utils.cache_manager as cache_manager
import utils.getters as getters
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logging.info(f'Build DF with: num course_ids:{len(cids)}, num quiz_ids:{len(qids)}, num user_ids:{len(uids)}')
    build_df(cids, qids, uids, accom_type, date_filter)

def build_df(course_ids, quiz_ids, user_ids, accom_type, date_filter):

    accom_checks = ['time', 'attempts'] if accom_type == 'both' else [accom_type]
    quiz_types = ['classic', 'new']

    for course_id in course_ids:
        for quiz_id in quiz_ids:
            for user_id in user_ids:
                for check_type in accom_checks:
                    for quiz_type in quiz_types:
                        logging.info(f"→ Checking: C:{course_id}, Q:{quiz_id}, U:{user_id}, Type:{check_type}, QT:{quiz_type}")
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

    print(course_df)
    print(user_df)
    print(quiz_df)
    print(submission_df)

    course_df["Course ID Course"] = course_df["Course ID Course"].astype(str)
    user_df["User ID"] = user_df["User ID"].astype(str)
    quiz_df["Quiz ID"] = quiz_df["Quiz ID"].astype(str)
    submission_df["Course ID Sub"] = submission_df["Course ID Sub"].astype(str).where(submission_df["Course ID Sub"].notna(), "")
    submission_df["User ID Sub"] = submission_df["User ID Sub"].astype(str).where(submission_df["User ID Sub"].notna(), "")
    submission_df["Quiz ID Sub"] = submission_df["Quiz ID Sub"].astype(str).where(submission_df["Quiz ID Sub"].notna(), "")

    # Merge logic remains the same, plus cleanup:
    final_df = (
        submission_df
        .merge(course_df, left_on='Course ID Sub', right_on='Course ID Course', how='left')
        .drop(columns=['Course ID Course'])
        .merge(user_df, left_on=['Course ID Sub', 'User ID Sub'], right_on=['Course ID User', 'User ID'], how='left')
        .drop(columns=['Course ID User'])
        .merge(quiz_df, left_on=['Course ID Sub', 'Quiz ID Sub'], right_on=['Course ID Quiz', 'Quiz ID'], how='left')
        .drop(columns=['Course ID Quiz'])
    )

    final_df = final_df[[
        'User ID', 'Sortable Name', 'SIS User ID', 'Email',
        'Course ID Sub', 'Course Code', 'Course Name',
        'Quiz ID', 'Title', 'Type',
        'Extra Time', 'Extra Attempts', 'Date'
    ]].rename(columns={'Course ID Sub': 'Course ID'})

    return final_df
