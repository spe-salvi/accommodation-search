import time
import config.config as config
from utils.paginate import paginatedGet

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds

def retry_get(url, params):
    if not url or not isinstance(url, str) or not isinstance(params, dict):
        logger.error("Invalid URL or parameters")
        return None

    retry_count = 0
    while retry_count < MAX_RETRIES:
<<<<<<< HEAD
        # logger.info(f"retry_get called with {url}")
=======
        logger.info(f"retry_get called with URL: {url}")
        logger.info(f"Parameters: {params}")
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59

        try:
            data = paginatedGet(url, config.HEADERS, params)
            if data:
                logger.info(f"Success - received {len(data)} items")
                logger.debug(f"First item preview: {str(data[0])[:200] if data else 'No data'}")
            else:
                logger.warning("Received empty response")
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"Attempt {retry_count} failed: {str(e)}")
            if retry_count == MAX_RETRIES:
                logger.error(f"Failed to fetch data after {MAX_RETRIES} attempts")
                return None
            delay = INITIAL_RETRY_DELAY * (2 ** (retry_count - 1))
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            continue
    return data