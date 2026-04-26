import requests
import json

def run_test_request():
    url = "https://ctsv.hust.edu.vn/api-t/Criteria/GetCriteriaTypeDetails"
    
    headers = {
        "authority": "ctsv.hust.edu.vn",
        "accept": "application/json",
        "accept-language": "en,vi-VN;q=0.9,vi;q=0.8,fr-FR;q=0.7,fr;q=0.6,en-US;q=0.5",
        "authorization": "Bearer null",
        "content-type": "application/json",
        "origin": "https://ctsv.hust.edu.vn",
        "referer": "https://ctsv.hust.edu.vn/",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    }

    cookies = {
        "x-student-portal-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiWmI1SUowUGc1UDFidENWcmlyaWxzcjNFc3RyaWNtd1EvdVFFcVRoVDRkQlVxTmdmQXZjRXFmMmFXV3lONjBZcDc4RDVNZzl3Zm9tVzJDNlBKRXZxa2RpZEhkS3doMmxRYTVDOWR1YndHT1RmaEh0cXdMUllBYVd2ZWZ6VU11M3kiLCJpYXQiOjE3NzcxNzI3NTEsImV4cCI6MTc3NzE3NjM1MX0.91iCxcz2FkwzQ8JWGov2317CD7D9FUqjglH86BckTZw",
        "x-access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiVTJGc2RHVmtYMThndUt3UDk5YjhwRlJGQVJLeHdaeWhGbTNxOU1kalc0YWY4dEVCYXFIMjZQbUozbTZtckxNOWNTZSs5MTBjR0FUZTE1WUNjMmNQTHl6T011ZW9OMDNVNjhCcHkySUpSTWM9IiwiaWF0IjoxNzc3MTcyNzUxLCJleHAiOjE3NzcyNTkxNTF9.6NRkg4-xfOQjpo_RzOBSqJZ18ORe1Y9IPufsDs4PeEc",
        "TokenCode": "184306BEAB7FD30F3CC3A3241B22E872",
        "UserName": "20235008",
        "name": "PH%E1%BA%A0M%20%C4%90%E1%BB%A8C%20ANH",
        "UType": "0",
        "sidebarStatus": "0"
    }

    # Common body for this endpoint
    body = {
        "UserCode": "20235008",
        "Semester": "2025-2",
        "UserName": "20235008",
        "TokenCode": "184306BEAB7FD30F3CC3A3241B22E872"
    }

    print(f"Sending POST request to {url}...")
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=body)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        try:
            data = response.json()
            print("Response Data (truncated):")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
        except:
            print("Response Content (not JSON):")
            print(response.text[:1000])
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    run_test_request()
