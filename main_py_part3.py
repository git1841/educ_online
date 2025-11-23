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