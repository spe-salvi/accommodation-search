from processors.submission import is_accommodated
import fetch.fetch_dfs as fetch_dfs
import pandas as pd
import logging
from db.repositories.course_repo import CourseRepository
from db.repositories.quiz_repo import QuizRepository
from db.repositories.user_repo import UserRepository
from db.repositories.submission_repo import SubmissionRepository
from db.repositories.term_repo import TermRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_df(course_ids=None, quiz_ids=None, user_ids=None,
              accom_type=None, quiz_type=None, date_filter=None):

    course_repo = CourseRepository()
    quiz_repo = QuizRepository()
    user_repo = UserRepository()
    submission_repo = SubmissionRepository()

    courses = [c for cid in course_ids for c in course_repo.get_by_id(cid)]
    quizzes = [q for cid in course_ids for q in quiz_repo.get_by_course(cid)]
    users = [u for cid in course_ids for u in user_repo.get_users_by_course(cid)]
    submissions = [s for cid in course_ids for s in submission_repo.get_all_by_course(cid)]

    data_frames, question_df = fetch_all_data(accom_type)

    if course_ids is None:
        course_ids = data_frames["submission"]['Course ID Sub'].unique().tolist()
    if user_ids is None:
        user_ids = data_frames["submission"]['User ID Sub'].unique().tolist()
    if quiz_ids is None:
        quiz_ids = data_frames["submission"]['Quiz ID Sub'].unique().tolist()

    accommodation_df = build_accommodation_df(
        course_ids=course_ids,
        user_ids=user_ids,
        quiz_ids=quiz_ids,
        accom_type=accom_type,
        quiz_type=quiz_type,
        date_filter=date_filter,
        quiz_df=data_frames["quiz"],
        user_df=data_frames["user"],
        question_df=question_df
    )

    if accommodation_df.empty:
        logger.warning("Accommodation DF Empty")
        return data_frames

    if not data_frames or accommodation_df.empty:
        logger.warning("One or more DataFrames are empty. Merging may result in an empty DataFrame.")
        return pd.DataFrame()  # Return an empty DataFrame

    normalize_all(data_frames, accommodation_df, question_df)

    final_df = merge_all_data(data_frames, accommodation_df, question_df)

    final_df = clean_and_filter(final_df, course_ids, quiz_ids, user_ids,
                                accom_type, quiz_type, date_filter, question_df)

    return final_df


def fetch_all_data(accom_type=None):
    data_frames = {
        "term": fetch_dfs.fetch_term_df(),
        "course": fetch_dfs.fetch_course_df(),
        "user": fetch_dfs.fetch_user_df(),
        "quiz": fetch_dfs.fetch_quiz_df(),
        "submission": fetch_dfs.fetch_submission_df(),
    }
    question_df = fetch_dfs.fetch_question_df() if accom_type in ('spell_check', 'all') else None
    if question_df is not None and question_df.empty:
        question_df = None  # Treat empty question_df as None

    logger.info("Term DF:")
    logger.info(data_frames['term'])
    logger.info("Course DF:")
    logger.info(data_frames['course'])
    logger.info("User DF:")
    logger.info(data_frames['user'])
    logger.info("Quiz DF:")
    logger.info(data_frames['quiz'])
    logger.info("Submission DF:")
    logger.info(data_frames['submission'])
    logger.info("Question DF:")
    logger.info(question_df)
    return data_frames, question_df


def build_accommodation_df(course_ids, quiz_ids, user_ids, accom_type, quiz_type, date_filter,
                           quiz_df=None, user_df=None, question_df=None):
    """
    Vectorized build of accommodation DataFrame.
    Handles 'time', 'attempts', 'split_test', 'spell_check'.
    Accepts pre-fetched quiz_df, user_df, question_df.
    """
    acc_rows = []

    # Determine which accommodations to check
    valid_accoms = []
    if accom_type in ('time', 'all', None):
        valid_accoms.append('time')
    if accom_type in ('attempts', 'all', None):
        valid_accoms.append('attempts')
    if accom_type in ('split_test', 'all', None):
        valid_accoms.append('split_test')
    if accom_type in ('spell_check', 'all', None):
        valid_accoms.append('spell_check')

    # Default quiz types
    quiz_types = ['classic', 'new'] if (quiz_type == 'both' or quiz_type is None) else [quiz_type]

    # Create all combinations for time/attempts
    if valid_accoms and set(valid_accoms) & {'time', 'attempts'}:
        from itertools import product
        for course_id, quiz_id, user_id, qt in product(course_ids, quiz_ids, user_ids, quiz_types):
            for check_type in ['time', 'attempts']:
                if check_type not in valid_accoms:
                    continue

                accom_data = is_accommodated(course_id, quiz_id, user_id, check_type)
                if accom_data[0]:
                    accom_date = accom_data[1]
                    if date_filter not in ('both', None) and accom_date != date_filter:
                        continue
                    acc_rows.append([str(course_id), str(quiz_id), str(user_id), check_type, accom_date, qt])

    # Vectorized split_test
    if 'split_test' in valid_accoms and quiz_df is not None and user_df is not None:
        quiz_subset = quiz_df[quiz_df['Course ID Quiz'].isin(course_ids) & quiz_df['Quiz ID'].isin(quiz_ids)]
        user_subset = user_df[user_df['User ID'].isin(user_ids)]

        # Merge all user-quiz combinations
        merged = user_subset.assign(key=1).merge(quiz_subset.assign(key=1), on='key', suffixes=('_user', '_quiz'))
        merged = merged[(merged['Course ID Quiz'].isin(course_ids)) & (merged['Quiz ID'].isin(quiz_ids))]
        merged = merged.drop(columns='key')

        # Extract last name safely
        merged['last_name'] = merged['Sortable Name'].str.split(',', n=1).str[0].str.strip()

        # Filter: last name exists AND title includes both "Part" and the last name
        split_mask = merged.apply(
            lambda row: (
                isinstance(row['last_name'], str)
                and row['last_name'] != ""
                and "Part" in str(row['Title'])
                and row['last_name'].lower() in str(row['Title']).lower()
            ),
            axis=1
        )
        
        for qt in quiz_types:
            split_rows = merged.loc[split_mask, ['Course ID Quiz', 'Quiz ID', 'User ID']].copy()
            split_rows['Accommodation Type'] = 'split_test'
            split_rows['Accommodation Date'] = 'past'                                                                                                               #TODO: fetch actual date
            split_rows['Quiz Type'] = qt
            acc_rows.extend(split_rows.values.tolist())

    # Vectorized spell_check
    if 'spell_check' in valid_accoms and question_df is not None:
        # Find quizzes that have spell_check
        spell_quizzes = question_df[question_df['Spell Check'] == 'True'][['Course ID Ques', 'Quiz ID Ques']].drop_duplicates()
        user_subset = user_df[user_df['User ID'].isin(user_ids)]
        merged = user_subset.assign(key=1).merge(spell_quizzes.assign(key=1), on='key').drop(columns='key')

        for qt in quiz_types:
            merged['Accommodation Type'] = 'spell_check'
            merged['Accommodation Date'] = 'past'                                                                                                                   #TODO: fetch actual date
            merged['Quiz Type'] = qt
            merged = merged.rename(columns={'Course ID Ques': 'Course ID Acc', 'Quiz ID Ques': 'Quiz ID Acc', 'User ID': 'User ID Acc'})
            acc_rows.extend(merged[['Course ID Acc', 'Quiz ID Acc', 'User ID Acc', 'Accommodation Type', 'Accommodation Date', 'Quiz Type']].values.tolist())

    acc_df = pd.DataFrame(acc_rows, columns=['Course ID Acc', 'Quiz ID Acc', 'User ID Acc', 'Accommodation Type', 'Accommodation Date', 'Quiz Type'])
    return acc_df


def normalize_all(data_frames, accommodation_df, question_df=None):
    normalize_map = {
        "submission": ["User ID Sub", "Course ID Sub", "Quiz ID Sub"],
        "course": ["Course ID Course", "User ID Course", "Quiz ID Course"],
        "user": ["User ID", "Course ID User"],
        "quiz": ["Quiz ID", "Course ID Quiz"],
        "accommodation": ["Course ID Acc", "Quiz ID Acc", "User ID Acc"],
    }

    def normalize_ids(df, cols):
        for col in cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df

    for key, df in [("submission", data_frames["submission"]),
                    ("course", data_frames["course"]),
                    ("user", data_frames["user"]),
                    ("quiz", data_frames["quiz"]),
                    ("accommodation", accommodation_df)]:
        normalize_ids(df, normalize_map[key])
    
    if question_df is not None:
        normalize_ids(question_df, ["Course ID Ques", "Quiz ID Ques", "Item ID Ques"])

def merge_all_data(data_frames, accommodation_df, question_df):
    final_df = (
        data_frames["submission"]
        .merge(data_frames["term"], left_on="Course ID Sub", right_on="Course ID Term", how="left")
        .merge(data_frames["course"], left_on="Course ID Sub", right_on="Course ID Course", how="left")
        .merge(data_frames["user"], left_on=["Course ID Sub", "User ID Sub"], right_on=["Course ID User", "User ID"], how="left")
        .merge(data_frames["quiz"], left_on=["Course ID Sub", "Quiz ID Sub"], right_on=["Course ID Quiz", "Quiz ID"], how="left")
        .merge(accommodation_df, left_on=["Course ID Sub", "Quiz ID Sub", "User ID Sub"], 
               right_on=["Course ID Acc", "Quiz ID Acc", "User ID Acc"], how="left")
    )
    if question_df is not None:
        final_df = final_df.merge(
            question_df,
            left_on=["Course ID Sub", "Quiz ID Sub"],
            right_on=["Course ID Ques", "Quiz ID Ques"],
            how="right"
        )
    return final_df

def clean_and_filter(final_df, course_ids, quiz_ids, user_ids, accom_type, quiz_type, date_filter, question_df=None):
    final_df["Extra Time"] = final_df["Extra Time"].fillna(0).astype(int)
    final_df["Extra Attempts"] = final_df["Extra Attempts"].fillna(0).astype(int)
    final_df["Accommodation Type"] = final_df["Accommodation Type"].fillna("None")

    if accom_type and accom_type != "all":
        final_df = final_df[final_df["Accommodation Type"] == accom_type]
    else:
        final_df = final_df[final_df["Accommodation Type"] != "None"]

    if quiz_type and quiz_type != "both":
        final_df = final_df[final_df["Type"] == quiz_type]
    if date_filter in ("past", "future"):
        final_df = final_df[final_df["Date"] == date_filter]

    if course_ids:
        final_df = final_df[final_df["Course ID Sub"].isin(course_ids)]
    if user_ids:
        final_df = final_df[final_df["User ID"].isin(user_ids)]
    if quiz_ids:
        final_df = final_df[final_df["Quiz ID"].isin(quiz_ids)]

    drop_cols = [
        "Course ID Term", "Course ID Course", "Course ID User", "Course ID Quiz",
        "Course ID Acc", "User ID Sub", "User ID Acc", "Quiz ID Sub", "Quiz ID Acc",
        "Accommodation Date", "Quiz Type"
    ]
    if question_df is not None:
        drop_cols += ["Course ID Ques", "Quiz ID Ques"]
    final_df.drop(columns=drop_cols, inplace=True)

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

def mark_split_test_accommodations(df):
    """
    Look for quizzes split into multiple parts (like Final Exam - John Doe Part 1/Part 2)
    and assign 'split_test' as the accommodation type.
    """
    if df.empty:
        return df

    df = df.copy()
    
    # Extract the student's last name from the Sortable Name column
    df['Last Name'] = (
        df['Sortable Name']
        .fillna('')  
        .str.split(',')
        .str[0]
        .str.strip()
    )

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