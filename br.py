from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import os
import json
import uuid
from datetime import datetime
#from main_py_part2 import * 
#from main_py_part3 import * 


from database import get_db_connection, init_database
from google_drive import *

from auth import (
    hash_password, verify_password, create_session, 
    get_session, delete_session, get_current_user,
    require_auth, require_admin, cleanup_expired_sessions
)
from models import *
from websocket_manager import manager
from config import MAX_UPLOAD_SIZE

# Initialize FastAPI app
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    drive_manager.authenticate()
    print("Application started successfully!")

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     """Home page"""
#     user = get_current_user(request)
#     if user:
#         if user['user_type'] == 'pro':
#             return RedirectResponse(url="/pg_pro")
#         elif user['user_type'] == 'free':
#             return RedirectResponse(url="/pg_gr")
#     return templates.TemplateResponse("index.html", {"request": request})


@app.get("/")
async def home():
    return {'ok':'ok'}

