from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
import json
import os
import shutil

app = FastAPI(title="HUST Monitoring Dashboard")

PROFILE_FILE = 'data/user_profile.json'

class UserProfile(BaseModel):
    self_description: Optional[str] = ""
    timetable: Optional[str] = ""
    target_email: Optional[str] = ""
    user_code: Optional[str] = ""
    user_name: Optional[str] = ""
    hust_cookies: Optional[Dict] = {}
    qldt_cookies: Optional[Dict] = {}

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    dashboard_path = 'src/web/dashboard.html'
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Dashboard file not found</h1>"

@app.get("/api/profile")
async def get_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return UserProfile().dict()

@app.post("/api/profile")
async def save_profile(profile: UserProfile):
    try:
        os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
        # Load existing profile to merge if needed, but here we just overwrite with the full object from UI
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile.dict(), f, ensure_ascii=False, indent=4)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync-auth")
async def sync_auth(auth_data: Dict):
    """
    Endpoint to receive auth data from the bookmarklet.
    Expected format: { "hust_cookies": {...}, "qldt_cookies": {...}, "user_code": "...", "user_name": "..." }
    """
    try:
        current_data = await get_profile()
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
async def upload_cookies(type: str, file: UploadFile = File(...)):
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
        profile = await get_profile()
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
