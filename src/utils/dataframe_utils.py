from quizzes.quizzes import is_accommodated
import utils.fetch as fetch
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_df(course_ids, user_ids, quiz_ids, accom_type, quiz_type, date_filter):

    acc_df = pd.DataFrame(columns=[
        'Course ID Acc', 'Quiz ID Acc', 'User ID Acc', 'Accommodation Type', 'Accommodation Date', 'Quiz Type'])

    accom_checks = ['time', 'attempts'] if (accom_type == 'both' or accom_type is None) else [accom_type]
    quiz_types = ['classic', 'new'] if (quiz_type == 'both' or quiz_type is None) else [quiz_type]

    logging.info(f"Building accommodation DataFrame with filters - Course IDs: {len(course_ids)}, User IDs: {len(user_ids)}, Quiz IDs: {len(quiz_ids)}, Accommodation Type: {accom_type}, Quiz Type: {quiz_type}, Date Filter: {date_filter}")

    for course_id in course_ids:
        for quiz_id in quiz_ids:
            for user_id in user_ids:
                for check_type in accom_checks:
                    for quiz_type in quiz_types:
                        logging.info(f"→ Checking: C:{course_id}, Q:{quiz_id}, U:{user_id}, Type:{check_type}, QT:{quiz_type}")
                        accom_data = is_accommodated(course_id, quiz_id, user_id, check_type)

                        if not accom_data[0]:
                            logger.warning(f"→ Not accommodated: C:{course_id}, Q:{quiz_id}, U:{user_id}, Type:{check_type}, QT:{quiz_type}")
                            continue  # Not accommodated, skip

                        accom_date = accom_data[1]
                        if date_filter != 'both' and accom_date != date_filter:
                            logger.warning(f"→ Date filter mismatch: C:{course_id}, Q:{quiz_id}, U:{user_id}, Type:{check_type}, QT:{quiz_type}, Date:{accom_date}")
                            continue  # Date doesn't match filter

                        acc_df.loc[len(acc_df)] = [
                            str(course_id),
                            str(quiz_id),
                            str(user_id),
                            check_type,
                            accom_date,
                            quiz_type
                        ]
                        logger.info(f'Current Acc DF: \n{acc_df}')
    logging.info(f"Accommodation DataFrame built with {len(acc_df)} records")
    logger.info(f"Accommodation DF dtypes:\n{acc_df.dtypes}")

    return acc_df

def create_df(course_ids=None, user_ids=None, quiz_ids=None,
              accom_type=None, quiz_type=None, date_filter=None):
    term_df       = fetch.fetch_term_df()       # IDs as lists in column
    course_df     = fetch.fetch_course_df()     # IDs already as columns
    user_df       = fetch.fetch_user_df()       # IDs already as columns
    quiz_df       = fetch.fetch_quiz_df()
    submission_df = fetch.fetch_submission_df()
    logger.info(f"Submission DF dtypes:\n{submission_df.dtypes}")
    if course_ids is None:
        course_ids = list(set(submission_df['Course ID Sub'].to_list()))
    if user_ids is None:
        user_ids = list(set(submission_df['User ID Sub'].to_list()))
    if quiz_ids is None:
        quiz_ids = list(set(submission_df['Quiz ID Sub'].to_list()))
    accommodation_df = build_df(course_ids=course_ids, user_ids=user_ids, quiz_ids=quiz_ids,
              accom_type=accom_type, quiz_type=quiz_type, date_filter=date_filter)

    # print(course_df)
    # print(user_df)
    # print(quiz_df)
    # print(submission_df)

    submission_df = normalize_ids(submission_df, ["User ID Sub", "Course ID Sub", "Quiz ID Sub"])
    course_df = normalize_ids(course_df, ["Course ID Course", "User ID Course", "Quiz ID Course"])
    user_df = normalize_ids(user_df, ["User ID", "Course ID User"])
    quiz_df = normalize_ids(quiz_df, ["Quiz ID", "Course ID Quiz"])
    accommodation_df = normalize_ids(accommodation_df, ["Course ID Acc", "Quiz ID Acc", "User ID Acc"])

    logging.info(f'submission dataframe data types: \n{submission_df.dtypes}')
    logging.info(f'course dataframe data types: \n{course_df.dtypes}')
    logging.info(f'user dataframe data types: \n{user_df.dtypes}')
    logging.info(f'quiz dataframe data types: \n{quiz_df.dtypes}')
    logging.info(f'accommodation dataframe data types: \n{accommodation_df.dtypes}')

    print(set(accommodation_df["Course ID Acc"]) & set(submission_df["Course ID Sub"]))
    print(set(accommodation_df["Quiz ID Acc"]) & set(quiz_df["Quiz ID"]))
    print(set(accommodation_df["User ID Acc"]) & set(user_df["User ID"]))

    final_df = (
        submission_df
        # term
        .merge(term_df, left_on="Course ID Sub", right_on="Course ID Term", how="left")
        # course
        .merge(course_df, left_on="Course ID Sub", right_on="Course ID Course", how="left")
        # user
        .merge(user_df, left_on=["Course ID Sub", "User ID Sub"],
                        right_on=["Course ID User", "User ID"], how="left")
        # quiz
        .merge(quiz_df, left_on=["Course ID Sub", "Quiz ID Sub"],
                       right_on=["Course ID Quiz", "Quiz ID"], how="left")
        .merge(accommodation_df, left_on=["Course ID Sub", "Quiz ID Sub", "User ID Sub"],
                               right_on=["Course ID Acc", "Quiz ID Acc", "User ID Acc"], how="left")
        
    )

    final_df["Extra Time"]     = final_df["Extra Time"].fillna(0).astype(int)
    final_df["Extra Attempts"] = final_df["Extra Attempts"].fillna(0).astype(int)
    final_df["Accommodation Type"] = final_df["Accommodation Type"].fillna("None")

    if course_ids:
        final_df = final_df[final_df["Course ID Sub"].isin(course_ids)]
    if user_ids:
        final_df = final_df[final_df["User ID"].isin(user_ids)]
    if quiz_ids:
        final_df = final_df[final_df["Quiz ID"].isin(quiz_ids)]
    if quiz_type and quiz_type != 'both':
        final_df = final_df[final_df["Type"] == quiz_type]
    if accom_type and accom_type != 'both':
        final_df = final_df[final_df["Accommodation Type"] == accom_type]
    else:
        final_df = final_df[final_df["Accommodation Type"] != 'None']
    if date_filter in ('past', 'future'):
        final_df = final_df[final_df["Date"] == date_filter]



    final_df.drop(columns=["Course ID Term", "Course ID Course", "Course ID User", "Course ID Quiz", "Course ID Acc", "User ID Sub", "User ID Acc", "Quiz ID Sub", "Quiz ID Acc", "Accommodation Date", "Quiz Type"], inplace=True)  # Clean up redundant columns
    cols = [
        "Term Name", "User ID", "Sortable Name", "SIS User ID", "Email",
        "Course ID Sub", "Course Code", "Course Name",
        "Quiz ID", "Title", "Type",
        "Extra Time", "Extra Attempts", "Date",
        "Accommodation Type"
    ]
    final_df = final_df[cols].rename(columns={"Course ID Sub": "Course ID"})
    final_df.drop_duplicates(inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    return final_df

def normalize_ids(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df