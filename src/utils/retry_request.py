import time
import config as config
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
        logger.info(f"retry_get called with URL: {url}")
        logger.info(f"Parameters: {params}")

        try:
            data = paginatedGet(url, config.HEADERS, params)
            print(f'DATA: {data}')
                        # Normalize single object to list
            if isinstance(data, dict):
                data = [data]
            # Handle Canvas "empty" responses gracefully
            if not isinstance(data, list):
                logger.warning(f"Unexpected data type {type(data)} from {url}: {data}")
                return []
            logger.info(f"Success - received {len(data)} items")
            if data:
                logger.debug(f"First item preview: {str(data[0])[:200]}")
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