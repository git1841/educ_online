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
app = FastAPI(title="Educational Platform")

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

@app.get("/", response_model=None)
async def home(request: Request):
    """Home page"""
    user = get_current_user(request)
    if user:
        if user['user_type'] == 'pro':
            return RedirectResponse(url="/pg_pro")
        elif user['user_type'] == 'free':
            return RedirectResponse(url="/pg_gr")
    return templates.TemplateResponse("index.html", {"request": request})





@app.get("/inscription", response_class=HTMLResponse)
async def inscription_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("inscription.html", {"request": request})

@app.post("/inscription")
async def register(
    first_name: str = Form(...),
    last_name: str = Form(None),
    phone: str = Form(...),
    password: str = Form(...),
    class_level: str = Form(None),
    filiere: str = Form(None),
    profile_picture: UploadFile = File(None)
):
    """Register new user"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if admin name is being used
        cursor.execute("SELECT nom FROM admin WHERE nom = %s", (first_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ce nom est réservé aux administrateurs")
        
        # Check if phone already exists
        cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ce numéro de téléphone est déjà utilisé")
        
        # Hash password
        hashed_pwd = hash_password(password)
        
        # Upload profile picture if provided
        profile_pic_url = None
        if profile_picture and profile_picture.filename:
            file_bytes = await profile_picture.read()
            file_name = f"{uuid.uuid4()}_{profile_picture.filename}"
            result = drive_manager.upload_file_from_bytes(
                file_bytes, 
                file_name, 
                profile_picture.content_type,
                "profile_pictures"
            )
            if result:
                profile_pic_url = result['webContentLink']
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (first_name, last_name, phone, password, class_level, filiere, profile_picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, phone, hashed_pwd, class_level, filiere, profile_pic_url))
        
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Inscription réussie!"})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    phone: str = Form(...),
    password: str = Form(...),
    user_type: str = Form("user")
):
    """Login user or admin"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    response = JSONResponse({"success": False})
    
    try:
        if user_type == "admin":
            # Admin login
            cursor.execute("SELECT * FROM admin WHERE nom = %s", (phone,))
            admin = cursor.fetchone()
            
            if not admin or not verify_password(password, admin['mot_de_passe']):
                raise HTTPException(status_code=401, detail="Identifiants incorrects")
            
            session_id = create_session(admin['id'], 'admin', admin)
            response = JSONResponse({"success": True, "redirect": "/admin_panel"})
            response.set_cookie(key="admin_session_id", value=session_id, httponly=True)
        else:
            # User login
            cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
            user = cursor.fetchone()
            
            if not user or not verify_password(password, user['password']):
                raise HTTPException(status_code=401, detail="Identifiants incorrects")
            
            if not user['is_active']:
                raise HTTPException(status_code=403, detail="Votre compte est désactivé")
            
            session_id = create_session(user['id'], user['user_type'], user)
            
            redirect_url = "/pg_pro" if user['user_type'] == 'pro' else "/pg_gr"
            response = JSONResponse({"success": True, "redirect": redirect_url})
            response.set_cookie(key="session_id", value=session_id, httponly=True)
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/logout")
async def logout(request: Request):
    """Logout user"""
    session_id = request.cookies.get('session_id')
    admin_session_id = request.cookies.get('admin_session_id')
    
    if session_id:
        delete_session(session_id)
    if admin_session_id:
        delete_session(admin_session_id)
    
    response = RedirectResponse(url="/login")
    response.delete_cookie("session_id")
    response.delete_cookie("admin_session_id")
    return response

# ============================================================================
# USER PROFILE ROUTES
# ============================================================================

@app.get("/pg_pro", response_class=HTMLResponse)
async def page_pro(request: Request):
    """Pro user page"""
    user = require_auth(request, ['pro', 'admin'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get contents for pro users
    cursor.execute("""
        SELECT * FROM contents 
        WHERE access_type IN ('free', 'pro')
        ORDER BY created_at DESC
    """)
    contents = cursor.fetchall()
    
    # Get publications
    cursor.execute("""
        SELECT * FROM admin_publications 
        WHERE target_audience IN ('all', 'pro')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    publications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("pg_pro.html", {
        "request": request,
        "user": user,
        "contents": contents,
        "publications": publications
    })

@app.get("/pg_gr", response_class=HTMLResponse)
async def page_free(request: Request):
    """Free user page"""
    user = require_auth(request, ['free'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get free contents only
    cursor.execute("""
        SELECT * FROM contents 
        WHERE access_type = 'free'
        ORDER BY created_at DESC
    """)
    contents = cursor.fetchall()
    
    # Get publications
    cursor.execute("""
        SELECT * FROM admin_publications 
        WHERE target_audience IN ('all', 'free')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    publications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("pg_gr.html", {
        "request": request,
        "user": user,
        "contents": contents,
        "publications": publications
    })

@app.post("/update_profile")
async def update_profile(
    request: Request,
    first_name: str = Form(None),
    last_name: str = Form(None),
    phone: str = Form(None),
    class_level: str = Form(None),
    filiere: str = Form(None),
    profile_picture: UploadFile = File(None)
):
    """Update user profile"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if first_name:
            updates.append("first_name = %s")
            params.append(first_name)
        if last_name:
            updates.append("last_name = %s")
            params.append(last_name)
        if phone:
            updates.append("phone = %s")
            params.append(phone)
        if class_level:
            updates.append("class_level = %s")
            params.append(class_level)
        if filiere:
            updates.append("filiere = %s")
            params.append(filiere)
        
        # Handle profile picture
        if profile_picture and profile_picture.filename:
            file_bytes = await profile_picture.read()
            file_name = f"{uuid.uuid4()}_{profile_picture.filename}"
            result = drive_manager.upload_file_from_bytes(
                file_bytes,
                file_name,
                profile_picture.content_type,
                "profile_pictures"
            )
            if result:
                updates.append("profile_picture = %s")
                params.append(result['webContentLink'])
        
        if updates:
            params.append(user['id'])
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
        
        return JSONResponse({"success": True, "message": "Profil mis à jour"})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/change_password")
async def change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...)
):
    """Change user password"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT password FROM users WHERE id = %s", (user['id'],))
        result = cursor.fetchone()
        
        if not verify_password(old_password, result['password']):
            raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
        
        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, user['id']))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Mot de passe changé"})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/delete_account")
async def delete_account(request: Request):
    """Soft delete user account"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user['id'],))
        conn.commit()
        
        # Logout user
        session_id = request.cookies.get('session_id')
        if session_id:
            delete_session(session_id)
        
        response = JSONResponse({"success": True, "message": "Compte supprimé"})
        response.delete_cookie("session_id")
        return response
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()
        
        
        





#####################################################################################"
# ============================================================================
# MESSAGING ROUTES
# ============================================================================

@app.get("/message_pro", response_class=HTMLResponse)
async def message_pro_page(request: Request):
    """Pro messaging page"""
    user = require_auth(request, ['pro', 'admin'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user's conversations
    cursor.execute("""
        SELECT DISTINCT c.*, 
               (SELECT COUNT(*) FROM conversation_participants WHERE conversation_id = c.id) as participant_count
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = %s
        ORDER BY c.created_at DESC
    """, (user['id'],))
    conversations = cursor.fetchall()
    
    # Get all users for starting new chats
    cursor.execute("""
        SELECT id, first_name, last_name, profile_picture 
        FROM users 
        WHERE id != %s AND is_active = TRUE
    """, (user['id'],))
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("message_pro.html", {
        "request": request,
        "user": user,
        "conversations": conversations,
        "users": users
    })

@app.get("/message_prive", response_class=HTMLResponse)
async def message_prive_page(request: Request):
    """Free user messaging page"""
    user = require_auth(request, ['free'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user's conversations
    cursor.execute("""
        SELECT DISTINCT c.*
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = %s AND c.conversation_type = 'private'
        ORDER BY c.created_at DESC
    """, (user['id'],))
    conversations = cursor.fetchall()
    
    # Get all users for starting new chats
    cursor.execute("""
        SELECT id, first_name, last_name, profile_picture 
        FROM users 
        WHERE id != %s AND is_active = TRUE
    """, (user['id'],))
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("message_prive.html", {
        "request": request,
        "user": user,
        "conversations": conversations,
        "users": users
    })

@app.post("/start_private_chat")
async def start_private_chat(request: Request, other_user_id: int = Form(...)):
    """Start or get existing private conversation"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if conversation already exists
        cursor.execute("""
            SELECT c.id FROM conversations c
            JOIN conversation_participants cp1 ON c.id = cp1.conversation_id
            JOIN conversation_participants cp2 ON c.id = cp2.conversation_id
            WHERE c.conversation_type = 'private'
            AND cp1.user_id = %s AND cp2.user_id = %s
        """, (user['id'], other_user_id))
        
        existing = cursor.fetchone()
        if existing:
            return JSONResponse({"success": True, "conversation_id": existing['id']})
        
        # Create new conversation
        cursor.execute("""
            INSERT INTO conversations (conversation_type, created_by)
            VALUES ('private', %s)
        """, (user['id'],))
        conversation_id = cursor.lastrowid
        
        # Add participants
        cursor.execute("""
            INSERT INTO conversation_participants (conversation_id, user_id, role)
            VALUES (%s, %s, 'member'), (%s, %s, 'member')
        """, (conversation_id, user['id'], conversation_id, other_user_id))
        
        conn.commit()
        
        # Add to manager
        manager.add_to_conversation(conversation_id, user['id'])
        manager.add_to_conversation(conversation_id, other_user_id)
        
        return JSONResponse({"success": True, "conversation_id": conversation_id})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/send_private_message")
async def send_private_message(
    request: Request,
    conversation_id: int = Form(...),
    message_type: str = Form("text"),
    content: str = Form(None),
    file: UploadFile = File(None)
):
    """Send a message in a conversation"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify user is in conversation
        cursor.execute("""
            SELECT id FROM conversation_participants 
            WHERE conversation_id = %s AND user_id = %s
        """, (conversation_id, user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not in this conversation")
        
        file_url = None
        drive_file_id = None
        
        # Handle file upload
        if file and file.filename:
            file_bytes = await file.read()
            file_name = f"{uuid.uuid4()}_{file.filename}"
            
            # Determine folder based on file type
            folder = "shared_files"
            if message_type == "image":
                folder = "shared_files/images"
            elif message_type == "video":
                folder = "shared_files/videos"
            
            result = drive_manager.upload_file_from_bytes(
                file_bytes,
                file_name,
                file.content_type,
                folder
            )
            
            if result:
                file_url = result['webContentLink']
                drive_file_id = result['id']
        
        # Insert message
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_id, message_type, content, file_url, drive_file_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (conversation_id, user['id'], message_type, content, file_url, drive_file_id))
        
        message_id = cursor.lastrowid
        conn.commit()
        
        # Get full message data
        cursor.execute("""
            SELECT m.*, u.first_name, u.last_name, u.profile_picture
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.id = %s
        """, (message_id,))
        message_data = cursor.fetchone()
        
        # Broadcast to conversation participants
        await manager.broadcast_to_conversation({
            "type": "new_message",
            "message": message_data
        }, conversation_id)
        
        return JSONResponse({"success": True, "message": message_data})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/get_private_messages/{conversation_id}")
async def get_private_messages(request: Request, conversation_id: int):
    """Get messages for a conversation"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify user is in conversation
        cursor.execute("""
            SELECT id FROM conversation_participants 
            WHERE conversation_id = %s AND user_id = %s
        """, (conversation_id, user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not in this conversation")
        
        # Get messages
        cursor.execute("""
            SELECT m.*, u.first_name, u.last_name, u.profile_picture
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = %s
            ORDER BY m.created_at ASC
        """, (conversation_id,))
        
        messages = cursor.fetchall()
        return JSONResponse({"success": True, "messages": messages})
    
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# GROUP ROUTES
# ============================================================================

@app.get("/groupe_pro", response_class=HTMLResponse)
async def groupe_pro_page(request: Request):
    """Pro groups page"""
    user = require_auth(request, ['pro', 'admin'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user's groups
    cursor.execute("""
        SELECT c.*, cp.role,
               (SELECT COUNT(*) FROM conversation_participants WHERE conversation_id = c.id) as member_count
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = %s AND c.conversation_type = 'group'
        ORDER BY c.created_at DESC
    """, (user['id'],))
    groups = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("groupe_pro.html", {
        "request": request,
        "user": user,
        "groups": groups
    })

@app.get("/groupe_gr", response_class=HTMLResponse)
async def groupe_free_page(request: Request):
    """Free user groups page"""
    user = require_auth(request, ['free'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user's groups
    cursor.execute("""
        SELECT c.*, cp.role
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = %s AND c.conversation_type = 'group'
        ORDER BY c.created_at DESC
    """, (user['id'],))
    groups = cursor.fetchall()
    
    # Get pending requests
    cursor.execute("""
        SELECT * FROM group_requests 
        WHERE requested_by = %s AND status = 'pending'
        ORDER BY created_at DESC
    """, (user['id'],))
    pending_requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("groupe_gr.html", {
        "request": request,
        "user": user,
        "groups": groups,
        "pending_requests": pending_requests
    })

@app.post("/create_group_request")
async def create_group_request(
    request: Request,
    group_name: str = Form(...),
    description: str = Form(None),
    group_photo: UploadFile = File(None)
):
    """Create group or group request"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if user['user_type'] == 'pro':
            # Pro users can create groups directly
            group_photo_url = None
            if group_photo and group_photo.filename:
                file_bytes = await group_photo.read()
                file_name = f"{uuid.uuid4()}_{group_photo.filename}"
                result = drive_manager.upload_file_from_bytes(
                    file_bytes,
                    file_name,
                    group_photo.content_type,
                    "group_avatars"
                )
                if result:
                    group_photo_url = result['webContentLink']
            
            cursor.execute("""
                INSERT INTO conversations (name, conversation_type, created_by, group_photo, description)
                VALUES (%s, 'group', %s, %s, %s)
            """, (group_name, user['id'], group_photo_url, description))
            
            group_id = cursor.lastrowid
            
            # Add creator as admin
            cursor.execute("""
                INSERT INTO conversation_participants (conversation_id, user_id, role)
                VALUES (%s, %s, 'admin')
            """, (group_id, user['id']))
            
            conn.commit()
            
            return JSONResponse({"success": True, "message": "Groupe créé", "group_id": group_id})
        else:
            # Free users need approval
            cursor.execute("""
                INSERT INTO group_requests (group_name, description, requested_by)
                VALUES (%s, %s, %s)
            """, (group_name, description, user['id']))
            
            conn.commit()
            
            return JSONResponse({"success": True, "message": "Demande envoyée pour approbation"})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/group_chat/{group_id}", response_class=HTMLResponse)
async def group_chat_page(request: Request, group_id: int):
    """Group chat page"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify user is in group
    cursor.execute("""
        SELECT cp.role, c.*
        FROM conversation_participants cp
        JOIN conversations c ON cp.conversation_id = c.id
        WHERE cp.conversation_id = %s AND cp.user_id = %s
    """, (group_id, user['id']))
    
    group_data = cursor.fetchone()
    if not group_data:
        raise HTTPException(status_code=403, detail="Not in this group")
    
    # Get members
    cursor.execute("""
        SELECT u.id, u.first_name, u.last_name, u.profile_picture, cp.role
        FROM users u
        JOIN conversation_participants cp ON u.id = cp.user_id
        WHERE cp.conversation_id = %s
    """, (group_id,))
    members = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("group_chat.html", {
        "request": request,
        "user": user,
        "group": group_data,
        "members": members
    })

@app.post("/send_group_message")
async def send_group_message(
    request: Request,
    conversation_id: int = Form(...),
    message_type: str = Form("text"),
    content: str = Form(None),
    file: UploadFile = File(None)
):
    """Send message in group"""
    return await send_private_message(request, conversation_id, message_type, content, file)

@app.post("/invite_members")
async def invite_members(
    request: Request,
    group_id: int = Form(...),
    user_ids: str = Form(...)
):
    """Invite members to group"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user is group admin
        cursor.execute("""
            SELECT role FROM conversation_participants 
            WHERE conversation_id = %s AND user_id = %s
        """, (group_id, user['id']))
        
        result = cursor.fetchone()
        if not result or result['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Only admins can invite members")
        
        # Parse user IDs
        user_id_list = [int(uid) for uid in user_ids.split(',')]
        
        # Add members
        for uid in user_id_list:
            try:
                cursor.execute("""
                    INSERT INTO conversation_participants (conversation_id, user_id, role)
                    VALUES (%s, %s, 'member')
                """, (group_id, uid))
                manager.add_to_conversation(group_id, uid)
            except:
                pass  # Skip if already member
        
        conn.commit()
        return JSONResponse({"success": True, "message": "Membres invités"})
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()
###########################################################################################
# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin dashboard"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'pro'")
    pro_users = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM contents")
    total_contents = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM group_requests WHERE status = 'pending'")
    pending_groups = cursor.fetchone()['count']
    
    # Get all users
    cursor.execute("""
        SELECT id, first_name, last_name, phone, user_type, is_active, is_verified, created_at
        FROM users ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    
    # Get all contents
    cursor.execute("""
        SELECT c.*, a.nom as admin_name 
        FROM contents c
        LEFT JOIN admin a ON c.uploaded_by = a.id
        ORDER BY c.created_at DESC
    """)
    contents = cursor.fetchall()
    
    # Get group requests
    cursor.execute("""
        SELECT gr.*, u.first_name, u.last_name
        FROM group_requests gr
        JOIN users u ON gr.requested_by = u.id
        WHERE gr.status = 'pending'
        ORDER BY gr.created_at DESC
    """)
    group_requests = cursor.fetchall()
    
    # Get publications
    cursor.execute("""
        SELECT * FROM admin_publications ORDER BY created_at DESC LIMIT 20
    """)
    publications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("admin_panel.html", {
        "request": request,
        "admin": admin,
        "stats": {
            "total_users": total_users,
            "pro_users": pro_users,
            "total_contents": total_contents,
            "pending_groups": pending_groups
        },
        "users": users,
        "contents": contents,
        "group_requests": group_requests,
        "publications": publications
    })

@app.post("/admin/toggle_user_active/{user_id}")
async def toggle_user_active(request: Request, user_id: int):
    """Toggle user active status"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users SET is_active = NOT is_active WHERE id = %s
        """, (user_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Statut modifié"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/verify_user/{user_id}")
async def verify_user(request: Request, user_id: int):
    """Verify user manually"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users SET is_verified = TRUE WHERE id = %s
        """, (user_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Utilisateur vérifié"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/issue_warning")
async def issue_warning(
    request: Request,
    user_id: int = Form(...),
    reason: str = Form(...),
    warning_type: str = Form("minor")
):
    """Issue warning to user"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO warnings (user_id, admin_id, reason, warning_type)
            VALUES (%s, %s, %s, %s)
        """, (user_id, admin['id'], reason, warning_type))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Avertissement envoyé"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/upload_content")
async def admin_upload_content(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    content_type: str = Form(...),
    access_type: str = Form("free"),
    class_level: str = Form(None),
    subject: str = Form(None),
    file: UploadFile = File(...)
):
    """Admin upload educational content"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Upload to Drive
        file_bytes = await file.read()
        file_name = f"{uuid.uuid4()}_{file.filename}"
        
        # Determine folder
        folder = f"educational_content/{content_type}"
        
        result = drive_manager.upload_file_from_bytes(
            file_bytes,
            file_name,
            file.content_type,
            folder
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Upload failed")
        
        # Insert to database
        cursor.execute("""
            INSERT INTO contents (title, description, drive_file_id, drive_link, 
                                  content_type, access_type, class_level, subject, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, description, result['id'], result['webContentLink'], 
              content_type, access_type, class_level, subject, admin['id']))
        
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Contenu uploadé"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/delete_content/{content_id}")
async def delete_content(request: Request, content_id: int):
    """Delete content"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get file info
        cursor.execute("SELECT drive_file_id FROM contents WHERE id = %s", (content_id,))
        content = cursor.fetchone()
        
        if content and content['drive_file_id']:
            drive_manager.delete_file(content['drive_file_id'])
        
        # Delete from database
        cursor.execute("DELETE FROM contents WHERE id = %s", (content_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Contenu supprimé"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/toggle_content_access/{content_id}")
async def toggle_content_access(request: Request, content_id: int):
    """Toggle content access type"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE contents 
            SET access_type = CASE 
                WHEN access_type = 'free' THEN 'pro' 
                ELSE 'free' 
            END
            WHERE id = %s
        """, (content_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Accès modifié"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/create_publication")
async def create_publication(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    target_audience: str = Form("all")
):
    """Create publication"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO admin_publications (admin_id, title, content, target_audience)
            VALUES (%s, %s, %s, %s)
        """, (admin['id'], title, content, target_audience))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Publication créée"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/delete_publication/{pub_id}")
async def delete_publication(request: Request, pub_id: int):
    """Delete publication"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM admin_publications WHERE id = %s", (pub_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Publication supprimée"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/approve_group/{request_id}")
async def approve_group(request: Request, request_id: int):
    """Approve group creation request"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get request details
        cursor.execute("""
            SELECT * FROM group_requests WHERE id = %s AND status = 'pending'
        """, (request_id,))
        
        req = cursor.fetchone()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Create group
        cursor.execute("""
            INSERT INTO conversations (name, conversation_type, created_by, description)
            VALUES (%s, 'group', %s, %s)
        """, (req['group_name'], req['requested_by'], req['description']))
        
        group_id = cursor.lastrowid
        
        # Add creator as admin
        cursor.execute("""
            INSERT INTO conversation_participants (conversation_id, user_id, role)
            VALUES (%s, %s, 'admin')
        """, (group_id, req['requested_by']))
        
        # Update request status
        cursor.execute("""
            UPDATE group_requests SET status = 'approved', reviewed_at = NOW()
            WHERE id = %s
        """, (request_id,))
        
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Groupe approuvé"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/admin/reject_group/{request_id}")
async def reject_group(request: Request, request_id: int):
    """Reject group creation request"""
    admin = require_admin(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE group_requests SET status = 'rejected', reviewed_at = NOW()
            WHERE id = %s
        """, (request_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Demande rejetée"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# VIDEO CALL ROUTES
# ============================================================================

@app.post("/start_group_call")
async def start_group_call(
    request: Request,
    conversation_id: int = Form(...),
    call_type: str = Form("group")
):
    """Start a video call"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify user is in conversation
        cursor.execute("""
            SELECT id FROM conversation_participants 
            WHERE conversation_id = %s AND user_id = %s
        """, (conversation_id, user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not in this conversation")
        
        # Create call
        cursor.execute("""
            INSERT INTO video_calls (conversation_id, initiated_by, call_type)
            VALUES (%s, %s, %s)
        """, (conversation_id, user['id'], call_type))
        
        call_id = cursor.lastrowid
        conn.commit()
        
        # Get all participants
        cursor.execute("""
            SELECT user_id FROM conversation_participants WHERE conversation_id = %s
        """, (conversation_id,))
        
        participants = [row['user_id'] for row in cursor.fetchall()]
        
        # Send notifications
        await manager.broadcast_to_multiple({
            "type": "call_notification",
            "call_id": call_id,
            "conversation_id": conversation_id,
            "initiated_by": user['first_name'],
            "call_type": call_type
        }, participants)
        
        return JSONResponse({
            "success": True, 
            "call_id": call_id,
            "message": "Appel démarré"
        })
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/video_call/{call_id}", response_class=HTMLResponse)
async def video_call_page(request: Request, call_id: int):
    """Video call page"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get call info
    cursor.execute("""
        SELECT vc.*, c.name as conversation_name
        FROM video_calls vc
        JOIN conversations c ON vc.conversation_id = c.id
        WHERE vc.id = %s
    """, (call_id,))
    
    call = cursor.fetchone()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("video_call.html", {
        "request": request,
        "user": user,
        "call": call
    })

@app.websocket("/ws/call/{call_id}/{user_id}")
async def websocket_call_endpoint(websocket: WebSocket, call_id: int, user_id: int):
    """WebSocket for WebRTC signaling"""
    await manager.connect_call(websocket, call_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Broadcast signaling data to other participants
            await manager.broadcast_to_call(
                {
                    "from": user_id,
                    "type": data.get("type"),
                    "data": data.get("data")
                },
                call_id,
                exclude_user=user_id
            )
    except WebSocketDisconnect:
        manager.disconnect_call(call_id, user_id)
        await manager.broadcast_to_call({
            "type": "user_left",
            "user_id": user_id
        }, call_id)

@app.post("/end_call")
async def end_call(request: Request, call_id: int = Form(...)):
    """End a video call"""
    user = require_auth(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE video_calls SET status = 'ended', ended_at = NOW()
            WHERE id = %s
        """, (call_id,))
        conn.commit()
        
        return JSONResponse({"success": True, "message": "Appel terminé"})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# WEBSOCKET FOR NOTIFICATIONS
# ============================================================================

@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: int):
    """WebSocket for real-time notifications"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(f"pong: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)