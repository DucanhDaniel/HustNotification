from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
import json
import os
import shutil
import secrets
from src import config

app = FastAPI(title="HUST Monitoring Dashboard")
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = config.DASHBOARD_USERNAME.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = config.DASHBOARD_PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

PROFILE_FILE = 'data/user_profile.json'

class UserProfile(BaseModel):
    self_description: Optional[str] = ""
    timetable: Optional[str] = ""
    target_email: Optional[str] = ""
    user_code: Optional[str] = ""
    user_name: Optional[str] = ""
    hust_cookies: Optional[Dict] = {}
    qldt_cookies: Optional[Dict] = {}
    qldt_cookie_path: Optional[str] = ""
    ctsv_cookie_path: Optional[str] = ""

def _load_profile_data():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return UserProfile().dict()

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(username: str = Depends(authenticate)):
    dashboard_path = 'src/web/dashboard.html'
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Dashboard file not found</h1>"

@app.get("/api/profile")
async def get_profile(username: str = Depends(authenticate)):
    return _load_profile_data()

@app.post("/api/profile")
async def save_profile(profile: UserProfile, username: str = Depends(authenticate)):
    try:
        os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
        current_data = _load_profile_data()
        
        # Merge new data into current data
        new_data = profile.dict()
        for key, value in new_data.items():
            # Update if value is not empty/default, or if it's a field we want to allow clearing
            if value is not None:
                if isinstance(value, str) and value == "" and key not in ["self_description", "timetable", "target_email"]:
                    continue
                if isinstance(value, dict) and value == {}:
                    continue
                current_data[key] = value
        
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync-auth")
async def sync_auth(auth_data: Dict, username: str = Depends(authenticate)):
    """
    Endpoint to receive auth data from the bookmarklet.
    Expected format: { "hust_cookies": {...}, "qldt_cookies": {...}, "user_code": "...", "user_name": "..." }
    """
    try:
        current_data = _load_profile_data()
        # Merge new auth data into profile
        for key in ["hust_cookies", "qldt_cookies", "user_code", "user_name"]:
            if key in auth_data:
                current_data[key] = auth_data[key]
        
        os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)
        
        return {"status": "success", "message": "Authentication synced successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-cookies")
async def upload_cookies(type: str, file: UploadFile = File(...), username: str = Depends(authenticate)):
    """
    type: 'ctsv' or 'qldt'
    """
    try:
        cookie_dir = os.path.join('data', 'cookies')
        os.makedirs(cookie_dir, exist_ok=True)
        
        file_path = os.path.join(cookie_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update profile with the new path
        profile = _load_profile_data()
        if type == 'ctsv':
            profile['ctsv_cookie_path'] = file_path
        else:
            profile['qldt_cookie_path'] = file_path
            
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)
            
        return {"status": "success", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 HUST Monitoring Dashboard is starting...")
    print("📍 URL: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
