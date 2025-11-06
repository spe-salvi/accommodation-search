import asyncio
import logging
import input.input_api as input_api

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
    candidates = []

    tasks = []
    # If user_ids are present, get their enrolled courses
    if ctx.user_ids:
        logger.info("compute_course_candidates: scheduling user enrollments fetch")
        tasks.append(input_api.get_course_ids_by_users(ctx.user_ids, ctx.term_id))

    # If a course search string exists, search courses in term (or global if term missing)
    if ctx.course_input and ctx.course_input.strip():
        tasks.append(input_api.get_course_ids_by_term_and_search(ctx.term_id or "", ctx.course_input))

    # If no other filters but term is present, get all courses in term
    if not tasks and ctx.term_id:
        tasks.append(input_api.get_course_ids_by_term_and_search(ctx.term_id, ""))

    if not tasks:
        logger.info("compute_course_candidates: no candidate sources found")
        return []

    logger.info(f"compute_course_candidates: running {len(tasks)} source task(s)")
    results = await asyncio.gather(*tasks)

    # Flatten results; results correspond in order to tasks
    lists = [set(r or []) for r in results]

    # If we have multiple sources (e.g., user enrollments + course search), intersect them to narrow
    if len(lists) >= 2:
        intersection = set.intersection(*lists)
        logger.info(f"compute_course_candidates: intersection size={len(intersection)}")
        return list(intersection)

    # Otherwise return the single candidate source
    logger.info(f"compute_course_candidates: single source size={len(lists[0])}")
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
        tasks.append(input_api.get_user_ids_by_search(ctx.term_id, ctx.user_input))

    if ctx.course_ids:
        tasks.append(input_api.get_user_ids_by_courses(ctx.course_ids))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks)
    lists = [set(r or []) for r in results]

    if len(lists) >= 2:
        return list(set.intersection(*lists))
    return list(lists[0])


# -----------------------------
# Centralized strategy dictionary
# -----------------------------
STRATEGIES = {
    "term_id": [
        (lambda c: c.term_input, lambda c: input_api.get_term_id(c.term_input))
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
         lambda c: input_api.get_quiz_ids_from_courses(c.course_ids, c.quiz_name, c.quiz_type)),
        (lambda c: c.course_ids and not c.quiz_name,
         lambda c: input_api.get_quiz_ids_from_courses(c.course_ids, "", c.quiz_type)),
    ]
}

# -----------------------------
# Generic node resolver
# -----------------------------
async def resolve_node(ctx, node):
    logger.info(f"Resolving node '{node}'")
    logger.info(f"Context state: term_id={ctx.term_id}, user_ids={ctx.user_ids}, course_ids={ctx.course_ids}")
    logger.info(f"Input state: term_input={ctx.term_input}, course_input={repr(ctx.course_input)}, user_input={ctx.user_input}")
    
    rules = STRATEGIES.get(node, [])
    result = await resolve_by_priority(ctx, *rules)
    setattr(ctx, node, result or [])
    
    logger.info(f"Node '{node}' resolution complete. Result: {getattr(ctx, node)}")
    return ctx

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
    completed = set()

    def can_run(node):
        deps = PIPELINE[node]["deps"]
        for dep in deps:
            optional = dep.endswith("?")
            dep = dep.rstrip("?")

            if optional and not ctx.has(dep) and dep not in completed:
                continue
            if not optional and not ctx.has(dep) and dep not in completed:
                return False
        # Special-case: if a user_input was provided we should wait for user_ids to resolve before
        # attempting to resolve course_ids to avoid falling back to 'all courses in term'.
        if node == "course_ids" and ctx.user_input and not ctx.has("user_ids"):
            return False
        return True

    while not all(ctx.has(t) or t in completed for t in targets):
        runnable = [
            node for node in PIPELINE
            if node not in completed and can_run(node)
        ]

        if not runnable:
            unresolved = [t for t in targets if not ctx.has(t)]
            logger.warning(
                f"No runnable nodes left — unresolved targets: {unresolved}. "
                "Continuing gracefully (some data may be missing)."
            )
            break

        completed.update(runnable)
        logger.debug(f"Running DAG nodes concurrently: {runnable}")

        results = await asyncio.gather(
            *(PIPELINE[node]["func"](ctx) for node in runnable),
            return_exceptions=True
        )

        for node, result in zip(runnable, results):
            if isinstance(result, Exception):
                logger.error(f"Node {node} raised: {result}")
            else:
                logger.debug(f"Node {node} completed successfully")

    logger.info(f"DAG resolved. Completed nodes: {sorted(completed)}")
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
