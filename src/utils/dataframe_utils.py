from quizzes.quizzes import is_accommodated
import utils.fetch as fetch
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_accommodation_df(course_ids, quiz_ids, user_ids, assignment_ids, accom_type, quiz_type, date_filter):
    """
    Build accommodation DataFrame for a set of courses, users, quizzes, and accommodation types.
    Handles 'time', 'attempts', and 'split_test'.
    Never leaves Accommodation Type as 'None'.
    """
    acc_df = pd.DataFrame(columns=[
        'Course ID Acc', 'Quiz ID Acc', 'User ID Acc', 'Accommodation Type', 'Accommodation Date', 'Quiz Type'
    ])

    # Determine which accommodations to check
    valid_accoms = []
    if accom_type in ('time', 'all', None):
        valid_accoms.append('time')
    if accom_type in ('attempts', 'all', None):
        valid_accoms.append('attempts')
    if accom_type in ('split_test', 'all', None):
        valid_accoms.append('split_test')

    # Default quiz types
    quiz_types = ['classic', 'new'] if (quiz_type == 'both' or quiz_type is None) else [quiz_type]

    for course_id in course_ids:
        for quiz_id in quiz_ids:
            for user_id in user_ids:
                for qt in quiz_types:

                    # Check time/attempts accommodations
                    for check_type in ['time', 'attempts']:
                        if check_type not in valid_accoms:
                            continue

                        accom_data = is_accommodated(course_id, quiz_id, user_id, check_type)
                        if not accom_data[0]:
                            continue

                        accom_date = accom_data[1]
                        if date_filter not in ('both', None) and accom_date != date_filter:
                            continue

                        acc_df.loc[len(acc_df)] = [
                            str(course_id),
                            str(quiz_id),
                            str(user_id),
                            check_type,
                            accom_date,
                            qt
                        ]

                    # Check split_test accommodations
                    if 'split_test' in valid_accoms:
                        # Fetch quiz title from your quiz_df (or however you have access to it)
                        title = fetch.fetch_quiz_title(course_id, quiz_id)  # placeholder function
                        sortable_name = fetch.fetch_user_sortable_name(user_id)  # placeholder
                        last_name = sortable_name.split(",")[0].strip()

                        if last_name and f"{last_name}" in title and "Part" in title:
                            # Determine date for consistency (could be past/future logic)
                            accom_date = "past"  # or fetch if available
                            acc_df.loc[len(acc_df)] = [
                                str(course_id),
                                str(quiz_id),
                                str(user_id),
                                'split_test',
                                accom_date,
                                qt
                            ]

    return acc_df

def create_df(course_ids=None, quiz_ids=None, user_ids=None, assignment_ids=None,
              accom_type=None, quiz_type=None, date_filter=None):
    """
    Build the full results DataFrame for courses, users, quizzes, and accommodations.
    Supports accommodation types: time, attempts, split_test, both.
    Filters by quiz type (classic/new/both) and date (past/future/both).
    Never produces 'None' in Accommodation Type.
    """
    # Fetch base DataFrames
    term_df       = fetch.fetch_term_df()
    course_df     = fetch.fetch_course_df()
    user_df       = fetch.fetch_user_df()
    quiz_df       = fetch.fetch_quiz_df()
    submission_df = fetch.fetch_submission_df()

    # Default IDs if none provided
    if course_ids is None:
        course_ids = submission_df['Course ID Sub'].unique().tolist()
    if user_ids is None:
        user_ids = submission_df['User ID Sub'].unique().tolist()
    if quiz_ids is None:
        quiz_ids = submission_df['Quiz ID Sub'].unique().tolist()

    # Build accommodation DF in one pass
    accommodation_df = build_accommodation_df(
        course_ids=course_ids,
        user_ids=user_ids,
        quiz_ids=quiz_ids,
        assignment_ids=assignment_ids,
        accom_type=accom_type,
        quiz_type=quiz_type,
        date_filter=date_filter
    )

    # Normalize IDs
    submission_df = normalize_ids(submission_df, ["User ID Sub", "Course ID Sub", "Quiz ID Sub"])
    course_df     = normalize_ids(course_df, ["Course ID Course", "User ID Course", "Quiz ID Course"])
    user_df       = normalize_ids(user_df, ["User ID", "Course ID User"])
    quiz_df       = normalize_ids(quiz_df, ["Quiz ID", "Course ID Quiz"])
    accommodation_df = normalize_ids(accommodation_df, ["Course ID Acc", "Quiz ID Acc", "User ID Acc"])

    # Merge everything together
    final_df = (
        submission_df
        .merge(term_df, left_on="Course ID Sub", right_on="Course ID Term", how="left")
        .merge(course_df, left_on="Course ID Sub", right_on="Course ID Course", how="left")
        .merge(user_df, left_on=["Course ID Sub", "User ID Sub"],
                        right_on=["Course ID User", "User ID"], how="left")
        .merge(quiz_df, left_on=["Course ID Sub", "Quiz ID Sub"],
                       right_on=["Course ID Quiz", "Quiz ID"], how="left")
        .merge(accommodation_df, left_on=["Course ID Sub", "Quiz ID Sub", "User ID Sub"],
                               right_on=["Course ID Acc", "Quiz ID Acc", "User ID Acc"], how="left")
    )

    # Fill missing accommodation values safely
    final_df["Extra Time"] = final_df["Extra Time"].fillna(0).astype(int)
    final_df["Extra Attempts"] = final_df["Extra Attempts"].fillna(0).astype(int)
    final_df["Accommodation Type"] = final_df["Accommodation Type"].fillna("None")

    # Filter accommodations as requested
    if accom_type and accom_type != 'all':
        final_df = final_df[final_df["Accommodation Type"] == accom_type]
    else:
        final_df = final_df[final_df["Accommodation Type"] != 'None']

    # Filter quiz type
    if quiz_type and quiz_type != 'both':
        final_df = final_df[final_df["Type"] == quiz_type]

    # Filter date
    if date_filter in ('past', 'future'):
        final_df = final_df[final_df["Date"] == date_filter]

    # Filter by IDs
    if course_ids:
        final_df = final_df[final_df["Course ID Sub"].isin(course_ids)]
    if user_ids:
        final_df = final_df[final_df["User ID"].isin(user_ids)]
    if quiz_ids:
        final_df = final_df[final_df["Quiz ID"].isin(quiz_ids)]

    # Cleanup redundant columns
    final_df.drop(columns=[
        "Course ID Term", "Course ID Course", "Course ID User", "Course ID Quiz",
        "Course ID Acc", "User ID Sub", "User ID Acc", "Quiz ID Sub", "Quiz ID Acc",
        "Accommodation Date", "Quiz Type"
    ], inplace=True)

    # Final column order
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

def mark_split_test_accommodations(df):
    """
    Look for quizzes split into multiple parts (like Final Exam - John Doe Part 1/Part 2)
    and assign 'split_test' as the accommodation type.
    """
    df = df.copy()
    
    # Extract the student's last name from the Sortable Name column
    df['Last Name'] = df['Sortable Name'].str.split(',').str[0].str.strip()

    # Identify rows where the quiz title contains the student's last name AND 'Part 1' or 'Part 2'
    split_mask = df.apply(
        lambda row: row['Last Name'] in row['Title'] and any(f'Part {i}' in row['Title'] for i in [1,2,3,4]),
        axis=1
    )

    # Update Accommodation Type for these rows
    df.loc[split_mask, 'Accommodation Type'] = 'split_test'

    # Optional: remove the helper column
    df.drop(columns=['Last Name'], inplace=True)
    
    return df