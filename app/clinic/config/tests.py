from datetime import time
from os import getenv

from dotenv import load_dotenv

load_dotenv('app/.env')

PASSWORD = getenv('TEST_USER_PASSWORD', 'test_password')
WORK_START_TIME = time(9, 0)
WORK_END_TIME = time(17, 0)
OVERLAP_START_TIME = time(11, 0)
OVERLAP_END_TIME = time(13, 0)
DAY_OF_WEEK_ONE = 1
DAY_OF_WEEK_TWO = 2
SUPERUSER_USERNAME = 'superuser'
SUPERUSER_EMAIL = 'superuser@example.com'
SUPERUSER_PHONE = '+10000000001'
ADMIN_PHONE = '+10000000002'
HOME_URL = '/'
PHONE_THREE = '+10000000003'
DOCTOR_USERNAME = 'doctor'
PATIENT_USERNAME = 'patient'
DOCTOR_EMAIL = 'doctor@example.com'