-- TERM STORE
CREATE TABLE IF NOT EXISTS term_store (
    term_id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS term_courses (
    term_id TEXT,
    course_id TEXT,
    PRIMARY KEY (term_id, course_id)
);

-- COURSE STORE
CREATE TABLE IF NOT EXISTS course_store (
    course_id TEXT PRIMARY KEY,
    code TEXT,
    name TEXT,
    term_id TEXT
);

CREATE TABLE IF NOT EXISTS course_users (
    course_id TEXT,
    user_id TEXT,
    PRIMARY KEY (course_id, user_id)
);

CREATE TABLE IF NOT EXISTS course_quizzes (
    course_id TEXT,
    quiz_id TEXT,
    PRIMARY KEY (course_id, quiz_id)
);

-- USER STORE
CREATE TABLE IF NOT EXISTS user_store (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    sis_id TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS user_courses (
    user_id TEXT,
    course_id TEXT,
    PRIMARY KEY (user_id, course_id)
);

-- QUIZ STORE
CREATE TABLE IF NOT EXISTS quiz_store (
    quiz_id TEXT PRIMARY KEY,
    title TEXT,
    time_limit TEXT,
    acc_type TEXT,
    course_id TEXT
);

-- SUBMISSION STORE
CREATE TABLE IF NOT EXISTS submission_store (
    user_id TEXT,
    course_id TEXT,
    quiz_id TEXT,
    extra_time REAL,
    extra_attempts INTEGER,
    date TEXT,
    PRIMARY KEY (user_id, course_id, quiz_id)
);

-- QUESTION STORE
CREATE TABLE IF NOT EXISTS question_store (
    course_id TEXT,
    quiz_id TEXT,
    item_id TEXT,
    question_type TEXT,
    spell_check BOOLEAN,
    PRIMARY KEY (course_id, quiz_id, item_id)
);
