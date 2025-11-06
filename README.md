# _IN PROGRESS_
## Inputs are currently hard-coded for testing

# Canvas Accommodations Reporting

_This project provides tools for reporting student accommodations on Canvas quizzes. It supports both manual and batch processing._

## 1. Project Overview

_Automate the process of managing quiz accommodations (extra time or attempts) in Canvas using API access._

---

## 2. Key Features / Deliverables

- Main outputs: report

---

## 3. Features

- Fetches Canvas course, quiz, and enrollment data via the Canvas API
- Checks for student accommodations (extra time/attempts) on quizzes
- Input via Excel file or GUI form
- Outputs results as a DataFrame (exported to Excel)

---

## 4. Tools & Technologies

- Languages: Python
- Software: Excel, Canvas LMS
- Libraries: pandas, asyncio & threading, SQLite, requests

---

## 5. Development Process

- Imported API calls that were similar from previous projects
- Retrieved data from endpoints for classic and new quizzes to check accommodations
- Added caching for efficiency
- Enabled file uploading through terminal for batch input
- Prototyped GUI for faster debugging
- Added logging for debugging
- Refactored all code to use controller.py
  - Needed to handle cases for multiple combinations of input
  - Continued debugging 16 input combos for which fields are provided or blank (term, course, quiz id, user id)
  - Aiming for optimal searches. A few example cases: - if user id provided, search user's enrollments (short list of courses) - if no user id, but term id, search only term's courses - if no user id or quiz id, process all users' accommodation per quiz
    (instead of cycling through all quizzes for each user)
- (6/18) Debugged cases when no course ID is provided
- (6/30) Wrote and complete unit testing
- Began integration testing
- Decided to simplify cache structure for maintainability and readability while debugging integration
- (7/1) Restructured cache and created transient vs persistent caches (edited api_endpoints.py)
- Clarified cache loading/writing when partial input is entered (resolvers.py)
- (8/28) Debugged dataframe merges and column names

- Decided to implement control flow initially without cache lookups (still writing to caches though)
- Implemented multithreading for api calls (populate_cache sub routines)
  - Placed locks at the endpoint functions so api calls still run in parallel, but writing happens sequentially
- Implemented split_test accommodation search
  - Compared user's last name to quiz titles
  - Added the filter to the final dataframe
  - Waiting for gui update

- Made design decisions for spelling_check accommodation search
  - Spell check is only possible for new quizzes
  - The url to fetch names the assignment_id as required
    - This is the same as the quiz_id for new quizzes
    - It does not apply here, but worth noting: The two ids are not the same for classic quizzes
  - Made an endpoint function to check each question in a given quiz
    - The function searches the question type to filter essay questions (the only type of question that allows spell check)
    - Then, the function checks the spell_check flag
  - This data is added to a question cache
    - The cache persists between calls
    - Course id, quiz id, question id can be used in later calls to quickly check the spell check flag
    - No need to look up every question to find essays

Detailed task flow for spell check accommodation search:
  - Add option to GUI
  - Add condition for 'spell_check' and 'all' selections: to populate_cache, to create_df
  - Establish cache structure/persistence
  - Review the control flow of api_params with the new endpoint
  - endpoint_items to cache
    - Only add if essay type
    - Check spell_check flag
  - Create question df in fetch
  - Integrate question df with final conditionally
  - Implement multithreading

Debugged spell check:
  - Extra time for new quizzes (endpoint?) - ti fix later, no endpoint exists
  - Fixed control flow, merging, and filters

Added handling of string input:
- GUI fields update
- Process data: to lowercase, fuzzy
- Term search using dict
- Course search with SIS ID, name, course code  
- Student search with SIS ID, login ID, name
- Quiz search with name
- Fetch endpoints (order of operations) for each
- Handle multiple user/quiz/course results

Decided to shift cache system to an SQLite backing
- Influenced by partial updates and gets


<details>
<summary>Future Features</summary>

- Expiry time for DB entries
- Clear option for tables
- Simplicity report upload for confirmation search
- PUT/POST accommodations

</details>
