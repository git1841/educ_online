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