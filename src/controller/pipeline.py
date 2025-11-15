import asyncio
import logging
import processors.course as course_processor
import processors.term as term_processor
import processors.user as user_processor
import processors.quiz as quiz_processor

logger = logging.getLogger(__name__)

# -----------------------------
# Context object
# -----------------------------
class Context:
    def __init__(self,
                 term_input=None,
                 course_input=None,
                 user_input=None,
                 quiz_name=None,
                 quiz_type=None):
        # raw inputs
        self.term_input = term_input
        self.course_input = course_input
        self.user_input = user_input
        self.quiz_name = quiz_name
        self.quiz_type = quiz_type

        # resolved outputs
        self.term_id = None
        self.course_ids = None
        self.user_ids = None
        self.quiz_ids = None

    def has(self, key):
        val = getattr(self, key, None)
        if val is None:
            return False
        if isinstance(val, (list, tuple, set, dict)):
            return len(val) > 0
        if isinstance(val, str):
            return val.strip() != ""
        return True

# -----------------------------
# Shared utility for strategy evaluation
# -----------------------------
async def resolve_by_priority(ctx, *rules):
    for condition, action in rules:
        if condition(ctx):
            result = action(ctx)
            if asyncio.iscoroutine(result):
                result = await result
            if result:
                print(f'Resolve By Priority: {result}')
                return result
    return []


# -----------------------------
# Aggregation helpers
# -----------------------------
async def compute_course_candidates(ctx):
    """Return course_ids by combining relevant sources based on inputs.

    Logic:
    - If user_input present (and user_ids resolved), fetch user enrollments (filtered by term if available)
    - If course_input provided, fetch courses by search+term
    - If term_id provided and no other filters, fetch all courses in term
    - Combine: when both user enrollments and course search exist, intersect them; otherwise union
    """
    tasks = []
    # If user_ids are present, get their enrolled courses
    if ctx.user_ids:
        print('COURSE IDS BY USERS')
        logger.info("compute_course_candidates: scheduling user enrollments fetch")
        tasks.append(course_processor.get_course_ids_by_users(ctx.user_ids, ctx.term_id))
        print(f'Course Candidates TASKS: {tasks}')


    # If a course search string exists, search courses in term (or global if term missing)
    if ctx.course_input and ctx.course_input.strip():
        print("COURSE IDS BY TERM/SEARCH")
        tasks.append(course_processor.get_course_ids_by_term_and_search(ctx.term_id or "", ctx.course_input))
        print(f'Course Candidates TASKS 2: {tasks}')


    # If no other filters but term is present, get all courses in term
    if not tasks and ctx.term_id:
        print('COURSE IFS BY TERM')
        tasks.append(course_processor.get_course_ids_by_term_and_search(ctx.term_id, ""))
        print(f'Course Candidates TASKS 3: {tasks}')


    if not tasks:
        logger.info("compute_course_candidates: no candidate sources found")
        return []

    logger.info(f"compute_course_candidates: running {len(tasks)} source task(s)")
    results = []
    for t in tasks:
        if asyncio.iscoroutine(t):
            results.append(await t)
        else:
            results.append(t)
    print(f'Course Candidates Tasks: {results}')
    flat_results = flatten_list(results)
    print(f'Course Candidates Flattened: {flat_results}')
    lists = [set(flat_results)]

    print(f'Courses Input: {lists}')

    # If we have multiple sources (e.g., user enrollments + course search), intersect them to narrow
    if len(lists) >= 2:
        intersection = set.intersection(*lists)
        print(f'Course Intersection: {intersection}')
        logger.info(f"compute_course_candidates: intersection size={len(intersection)}")
        return list(intersection)

    # Otherwise return the single candidate source
    logger.info(f"compute_course_candidates: single source size={len(lists[0])}")
    print(f'Course Candidates Final List: {list(lists[0])}')
    return list(lists[0])


async def compute_user_candidates(ctx):
    """Return user_ids by combining relevant sources.

    Logic:
    - If user_input provided, perform a user search (optionally filtered by term)
    - If course_ids available, fetch users from those courses
    - Combine: when both user search and course-derived users exist, intersect; otherwise union
    """
    tasks = []
    if ctx.user_input:
        print('USER IDS BY SEARCH')
        tasks.append(user_processor.get_user_ids_by_search(ctx.term_id, ctx.user_input))
        print(f'User Candidates TASKS: {tasks}')

    if ctx.course_ids:
        print('USER IDS BY COURSES')
        tasks.append(user_processor.get_user_ids_by_courses(ctx.course_ids))
        print(f'User Candidates TASKS 2: {tasks}')


    if not tasks:
        return []

    results = []
    for t in tasks:
        if asyncio.iscoroutine(t):
            results.append(await t)
        else:
            results.append(t)
    print(f'User Candidates Tasks: {results}')
    flat_results = flatten_list(results)
    unique_ids = list(set(flat_results))

    if len(results) >= 2:
        intersection = set.intersection(*(set(flatten_list(r)) for r in results if r))
        print(f'User Candidates Intersection: {intersection}')
        return list(intersection)

    print(f'User Candidates Final: {unique_ids}')
    return unique_ids


# -----------------------------
# Centralized strategy dictionary
# -----------------------------
STRATEGIES = {
    "term_id": [
        (lambda c: c.term_input, lambda c: term_processor.get_term_id(c.term_input))
    ],

    "user_ids": [
        (lambda c: True, lambda c: compute_user_candidates(c)),
    ],

    "course_ids": [
        # Aggregated course resolution - handled by helper below
        (lambda c: True, lambda c: compute_course_candidates(c)),
    ],

    "quiz_ids": [
        # Only valid when courses are known
        (lambda c: c.course_ids and c.quiz_name,
         lambda c: quiz_processor.get_quiz_ids_from_courses(c.course_ids, c.quiz_name, c.quiz_type)),
        (lambda c: c.course_ids and not c.quiz_name,
         lambda c: quiz_processor.get_quiz_ids_from_courses(c.course_ids, "", c.quiz_type)),
    ]
}

# -----------------------------
# Generic node resolver
# -----------------------------
async def resolve_node(ctx, node):
    logger.info(f"Resolving node '{node}'")
    logger.info(f"Context state: term_id={ctx.term_id}, user_ids={ctx.user_ids}, course_ids={ctx.course_ids}")
    logger.info(f"Input state: term_input={ctx.term_input}, course_input={repr(ctx.course_input)}, user_input={ctx.user_input}")
    
    rules = STRATEGIES.get(node, '')
    result = await resolve_by_priority(ctx, *rules)

    print(f'Resolve Node Returned: {result}')

    if isinstance(result, list):
        result = flatten_list(result)

    print(f'Resolve Node Flattened?: {result}')
    
    setattr(ctx, node, result or '')
    
    logger.info(f"Node '{node}' resolution complete. Result: {getattr(ctx, node)}")
    print(f'Resolve Node CTX: {ctx}')
    print(f'Resolve Node NODE: {node}')
    return getattr(ctx, node)

# Convenience wrappers for DAG
async def get_term_id(ctx):   return await resolve_node(ctx, "term_id")
async def get_course_ids(ctx): return await resolve_node(ctx, "course_ids")
async def get_user_ids(ctx):   return await resolve_node(ctx, "user_ids")
async def get_quiz_ids(ctx):   return await resolve_node(ctx, "quiz_ids")

# -----------------------------
# DAG definition (unchanged)
# -----------------------------
PIPELINE = {
    "term_id": {"deps": [], "func": get_term_id},
    "user_ids": {"deps": ["term_id?"], "func": get_user_ids},
    "course_ids": {"deps": ["term_id?", "user_ids?"], "func": get_course_ids},
    "quiz_ids": {"deps": ["course_ids"], "func": get_quiz_ids},
}

# -----------------------------
# DAG resolver (unchanged)
# -----------------------------
async def resolve_dependencies(ctx, targets=("quiz_ids",)):
    """
    Resolve DAG nodes using a fixpoint / convergence loop.

    - Respects dependency order from PIPELINE (which is already topological).
    - Runs multiple rounds until no node changes the context or max rounds hit.
    - Optional deps (like 'term_id?') are treated as "use it if present, but
      don't block execution if it's missing".
    """
    max_rounds = len(PIPELINE) * 3  # safety cap to avoid any weird infinite loops

    def deps_satisfied(node: str) -> bool:
        deps = PIPELINE[node]["deps"]
        for dep in deps:
            optional = dep.endswith("?")
            dep_name = dep.rstrip("?")

            # For optional deps, we don't require them to be present.
            if optional:
                continue

            # For required deps, ctx.must have a value.
            if not ctx.has(dep_name):
                return False

        return True

    for round_idx in range(max_rounds):
        logger.debug(f"resolve_dependencies: round {round_idx + 1}")
        progress = False

        # Iterate in insertion order (already term_id -> user_ids -> course_ids -> quiz_ids)
        for node, meta in PIPELINE.items():
            if not deps_satisfied(node):
                continue

            # Snapshot the "before" value
            before = getattr(ctx, node, None)

            try:
                # Node func (e.g. get_term_id, get_user_ids, etc.) is responsible
                # for updating ctx.<node> internally via resolve_node(...)
                result = await meta["func"](ctx)
            except Exception as e:
                logger.error(f"Node '{node}' raised an exception: {e}")
                continue

            # Read the "after" value from ctx (trust the node to have set it)
            after = getattr(ctx, node, None)

            # Normalize lists for comparison to avoid false positives from different list objects
            if isinstance(before, list):
                before_norm = flatten_list(before)
            else:
                before_norm = before

            if isinstance(after, list):
                after_norm = flatten_list(after)
            else:
                after_norm = after

            if before_norm != after_norm:
                logger.debug(f"Node '{node}' changed value: {before_norm} -> {after_norm}")
                progress = True

        # If nothing changed this round, we've converged
        if not progress:
            unresolved = [t for t in targets if not ctx.has(t)]
            if unresolved:
                logger.warning(
                    f"resolve_dependencies: converged with unresolved targets: {unresolved}. "
                    f"Some data may be missing."
                )
            break

    logger.info("DAG resolved.")
    logger.debug(
        f"Final context: term_id={ctx.term_id}, "
        f"course_ids={ctx.course_ids}, user_ids={ctx.user_ids}, quiz_ids={ctx.quiz_ids}"
    )
    return ctx


# -----------------------------
# Entry point
# -----------------------------
async def build_accommodation_context(
        term_input=None,
        course_input=None,
        user_input=None,
        quiz_name=None,
        quiz_type='both'):
    ctx = Context(
        term_input=term_input,
        course_input=course_input,
        user_input=user_input,
        quiz_name=quiz_name,
        quiz_type=quiz_type
    )
    await resolve_dependencies(ctx, targets=["quiz_ids"])
    return ctx

def flatten_list(seq):
    out = []
    for x in seq:
        if isinstance(x, list):
            out.extend(flatten_list(x))
        elif x is not None:
            out.append(x)
    return out