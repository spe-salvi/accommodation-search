import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def paginatedGet(url, headers, inputdata):
    perPageData = {"per_page": 100}
    mergedData = {**inputdata, **perPageData}
    response = requests.get(url, data=mergedData, headers=headers)
    # logger.info(f'URL: {url}')
    logger.info(f"GET Response: {response.status_code}")
    data = response.json()
    if 'next' in response.links:
        data = data + paginatedGet(response.links['next']['url'], headers, inputdata)
 
    return data
 