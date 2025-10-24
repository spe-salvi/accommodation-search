import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def paginatedGet(url, headers, inputdata):
    perPageData = {"per_page": 100}
    mergedData = {**inputdata, **perPageData}
<<<<<<< HEAD
    response = requests.get(url, data=mergedData, headers=headers)
=======
    response = requests.get(url, params=mergedData, headers=headers)
>>>>>>> 9059c6760f645c197a81fac1cde3d8b3a00b9d59
    # logger.info(f'URL: {url}')
    # logger.info(f"GET Response: {response.status_code}")
    data = response.json()
    if 'next' in response.links:
        data = data + paginatedGet(response.links['next']['url'], headers, inputdata)
 
    return data
 