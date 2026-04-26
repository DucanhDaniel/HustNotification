# File: src/config.py
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

PROFILE_FILE = os.path.join('data', 'user_profile.json')

def load_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def load_cookies_from_file(file_path, domain_filter=None):
    """Load Netscape format cookies from file into a dict, optionally filtering by domain."""
    if not file_path:
        return {}
    cookies = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    domain = parts[0]
                    if domain_filter and domain_filter not in domain:
                        continue
                    cookies[parts[5]] = parts[6]
    return cookies

def get_token_from_cookies_txt():
    """Extract x-access-token from configured ctsv cookie file."""
    path = get_conf('ctsv_cookie_path', 'cookies.txt')
    cookies = load_cookies_from_file(path, domain_filter='hust.edu.vn')
    return cookies.get('x-access-token')

_profile = load_profile()

# Helper to get config with proper fallback
def get_conf(key, default=None):
    val = _profile.get(key)
    if val is not None and val != "" and val != {}:
        return val
    env_val = os.getenv(key.upper())
    if not env_val:
        env_val = os.getenv(key.upper() + '_JSON')
        
    if env_val:
        try: return json.loads(env_val)
        except: return env_val
    return default

# HUST CTSV Config
_hust_cookie_file = get_conf('ctsv_cookie_path', 'cookies.txt')
HUST_COOKIES = load_cookies_from_file(_hust_cookie_file, domain_filter='hust.edu.vn')
HUST_COOKIES.update(_profile.get('hust_cookies', {}))

HUST_USER_CODE = get_conf('user_code', "20235008")
HUST_TOKEN = get_conf('hust_token', get_token_from_cookies_txt() or HUST_COOKIES.get('TokenCode', ''))

HUST_HEADERS = {
    'authority': 'ctsv.hust.edu.vn',
    'accept': 'application/json',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
}

# QLDT Config
_qldt_cookie_file = get_conf('qldt_cookie_path', 'qldt.hust.edu.vn_cookies.txt')
QLDT_COOKIES = load_cookies_from_file(_qldt_cookie_file, domain_filter='hust.edu.vn')
QLDT_COOKIES.update(_profile.get('qldt_cookies', {}))

# Cross-platform token sharing (SSO)
for token_key in ['x-access-token', 'x-student-portal-token']:
    if token_key not in HUST_COOKIES and token_key in QLDT_COOKIES:
        HUST_COOKIES[token_key] = QLDT_COOKIES[token_key]
    if token_key not in QLDT_COOKIES and token_key in HUST_COOKIES:
        QLDT_COOKIES[token_key] = HUST_COOKIES[token_key]

QLDT_USER_ID = get_conf('qldt_user_id', '108219')
QLDT_HEADERS = {
    'authority': 'student.hust.edu.vn',
    'accept': 'application/json',
    'content-type': 'application/json',
    'origin': 'https://qldt.hust.edu.vn',
    'referer': 'https://qldt.hust.edu.vn/',
    'x-student-portal-token': QLDT_COOKIES.get('x-student-portal-token', ''),
    'x-access-token': QLDT_COOKIES.get('x-access-token', ''),
    'x-check-sum': '2fa8883318d2ef2bde77eaa221a1a71920ae3ab4f79bf9933de9a3ad82adf31e'
}

# User Info
USER_CODE = HUST_USER_CODE
USER_NAME = get_conf('user_name', USER_CODE)
CURRENT_SEMESTER = get_conf('current_semester', '2025-2')
TARGET_EMAIL = get_conf('target_email', 'ducanh.opendb@gmail.com')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DASHBOARD_USERNAME = os.getenv('DASHBOARD_USERNAME')
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD')

# Intervals
SCHOLARSHIP_INTERVAL = int(get_conf('scholarship_interval', 1))
ACTIVITY_INTERVAL = int(get_conf('activity_interval', 1))
AWARD_INTERVAL = int(get_conf('award_interval', 1))
TRAINING_POINTS_INTERVAL = int(get_conf('training_points_interval', 6))
