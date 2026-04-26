import requests
import json

class APIFetcher:
    def __init__(self, base_url=None, headers=None, auth=None):
        """
        Initialize the API fetcher.

        Args:
            base_url (str): Base URL for the API.
            headers (dict): Default headers for requests.
            auth (dict): Authentication info, e.g., {'token': 'value', 'cookies': {...}}
        """
        self.base_url = base_url
        self.default_headers = headers or {}
        self.auth = auth or {}

    def set_auth(self, auth_type, value):
        """
        Set authentication info.

        Args:
            auth_type (str): Type of auth, e.g., 'bearer_token', 'cookies'.
            value: The auth value.
        """
        if auth_type == 'bearer_token':
            self.auth['bearer_token'] = value
        elif auth_type == 'cookies':
            self.auth['cookies'] = value
        # Add more auth types as needed

    def fetch(self, endpoint, method='GET', headers=None, body=None, params=None):
        """
        Fetch data from the API.

        Args:
            endpoint (str): API endpoint.
            method (str): HTTP method (GET, POST, etc.).
            headers (dict): Additional headers.
            body (dict): Request body for POST/PUT.
            params (dict): Query parameters.

        Returns:
            dict or list: JSON response data, or None if error.
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        request_headers = {**self.default_headers, **(headers or {})}

        # Add auth to headers
        if 'bearer_token' in self.auth:
            request_headers['Authorization'] = f"Bearer {self.auth['bearer_token']}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, params=params, cookies=self.auth.get('cookies'))
            elif method.upper() == 'POST':
                response = requests.post(url, headers=request_headers, json=body, params=params, cookies=self.auth.get('cookies'))
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {url}: {e}")
            return None