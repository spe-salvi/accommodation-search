from quizzes.quizzes import is_accommodated
import utils.fetch as fetch
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_df(course_ids, user_ids, quiz_ids, accom_type, quiz_type, date_filter):

    acc_df = pd.DataFrame(columns=[
        'Course ID Acc', 'Quiz ID Acc', 'User ID Acc', 'Accommodation Type', 'Quiz Type', 'Accommodation Date'])

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

                        acc_df.loc[len(acc_df)] = [course_id, quiz_id, user_id, accom_type, accom_date, quiz_type]
    logging.info(f"Accommodation DataFrame built with {len(acc_df)} records")
    return acc_df

def create_df(course_ids=None, user_ids=None, quiz_ids=None,
              accom_type=None, quiz_type=None, date_filter=None):
    term_df       = fetch.fetch_term_df()       # IDs as lists in column
    course_df     = fetch.fetch_course_df()     # IDs already as columns
    user_df       = fetch.fetch_user_df()       # IDs already as columns
    quiz_df       = fetch.fetch_quiz_df()
    submission_df = fetch.fetch_submission_df()
    accommodation_df = build_df(course_ids=course_ids, user_ids=user_ids, quiz_ids=quiz_ids,
              accom_type=accom_type, quiz_type=quiz_type, date_filter=date_filter)

    # print(course_df)
    # print(user_df)
    # print(quiz_df)
    # print(submission_df)

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
        .drop(columns=["Course ID Term", "Course ID Course", "Course ID User", "Course ID Quiz", "Course ID Acc", "User ID Sub", "User ID Acc", "Quiz ID Sub", "Quiz ID Acc", "Accommodation Date"])  # Clean up redundant columns
    )

    if course_ids:
        final_df = final_df[final_df["Course ID Sub"].isin(course_ids)]
    if user_ids:
        final_df = final_df[final_df["User ID"].isin(user_ids)]
    if quiz_ids:
        final_df = final_df[final_df["Quiz ID"].isin(quiz_ids)]
    if quiz_type:
        final_df = final_df[final_df["Type"] == quiz_type]
    if date_filter == "past":
        final_df = final_df[final_df["Date"] == "past"]
    elif date_filter == "future":
        final_df = final_df[final_df["Date"] == "future"]

    final_df["Extra Time"]     = final_df["Extra Time"].fillna(0).astype(int)
    final_df["Extra Attempts"] = final_df["Extra Attempts"].fillna(0).astype(int)

    cols = [
        "Term Name", "User ID", "Sortable Name", "SIS User ID", "Email",
        "Course ID Sub", "Course Code", "Course Name",
        "Quiz ID", "Title", "Type",
        "Extra Time", "Extra Attempts", "Date",
        "Accommodation Type", "Quiz Type"
    ]
    cols = [c for c in cols if c in final_df.columns]
    final_df = final_df[cols].rename(columns={"Course ID Sub": "Course ID"})
    final_df.drop_duplicates(inplace=True)
    final_df.reset_index(drop=True, inplace=True)

    return final_df
