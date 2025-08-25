import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://franciscan.instructure.com"
BETA_URL = "https://franciscan.beta.instructure.com"
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_2 = os.getenv('ACCESS_TOKEN_2')
ACCESS_TOKEN_EL = os.getenv('ACCESS_TOKEN_EL')

 
API_URL = f'{BASE_URL}/api'
BETA_API_URL = f'{BETA_URL}/api'
FUS_ACCOUNT = '/accounts/1'
HEADERS = {
    "Authorization": "Bearer " + ACCESS_TOKEN_EL
    }

TERMS = {
    115: 'Summer 2025',
    114: 'Spring 2025',
    120: 'Fall 2024',
    119: 'Summer 2024',
    113: 'Spring 2024',
    112: 'Fall 2023',
    111: 'Summer 2023',
    110: 'Spring 2023',
    109: 'Fall 2022',
    }

ACCOMMODATIONS = ['time', 'attempts']