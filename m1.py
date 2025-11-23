from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from fastapi.responses import Response # Import nécessaire
import json, os, io

app = FastAPI()

CREDENTIALS_FILE = "conf.json"  # Ton fichier OAuth2 téléchargé depuis Google Cloud 
TOKEN_FILE = "token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
REDIRECT_URI = "http://127.0.0.1:8000/callback"


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Google Drive FastAPI</h2>
    <a href='/auth'> Se connecter avec Google</a><br><br>
    <a href='/upload_form'> Envoyer un fichier</a><br><br>
    <a href='/files'> Voir les fichiers</a>
    """


# ----------------------  Authentification Google ----------------------
@app.get("/auth")
def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, SCOPES, redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(code: str):
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, SCOPES, redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    creds = flow.credentials

    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

    return RedirectResponse("/")


# ----------------------  Upload de fichier ----------------------
@app.get("/upload_form", response_class=HTMLResponse)
def upload_form():
    return """
    <h2>Upload un fichier vers Google Drive</h2>
    <form action="/upload_file" enctype="multipart/form-data" method="post">
        <input name="file" type="file" required>
        <button type="submit">Envoyer</button>
    </form>
    <a href="/"> Retour</a>
    """


@app.post("/upload_file")
async def upload_file_to_drive(file: UploadFile = File(...)):
    if not os.path.exists(TOKEN_FILE):
        return {"error": "Connecte-toi d'abord via /auth"}

    creds_data = json.load(open(TOKEN_FILE))
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    file_metadata = {'name': file.filename}
    media = MediaFileUpload(temp_path, mimetype=file.content_type)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields='id, name'
    ).execute()

    os.remove(temp_path)
    return {"uploaded_file": uploaded}


# ----------------------  Liste des fichiers ----------------------
@app.get("/files", response_class=HTMLResponse)
def list_files():
    if not os.path.exists(TOKEN_FILE):
        return RedirectResponse("/auth")

    creds_data = json.load(open(TOKEN_FILE))
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(pageSize=1000, fields="files(id, name)").execute()
    files = results.get('files', [])

    html = "<h2> Fichiers Google Drive :</h2><ul>"
    for f in files:
        html += f"<li>{f['name']} — <a href='/download/{f['id']}'> Télécharger</a></li>"
    html += "</ul><a href='/'> Retour</a>"
    return HTMLResponse(html)


# ---------------------- Téléchargement ----------------------
@app.get("/download/{file_id}")
def download_file(file_id: str):
    if not os.path.exists(TOKEN_FILE):
        return RedirectResponse("/auth")

    creds_data = json.load(open(TOKEN_FILE))
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    # 1. Obtenir les métadonnées (nom et type MIME)
    file = service.files().get(fileId=file_id, fields="name, mimeType").execute()
    file_name = file["name"]
    mime_type = file["mimeType"]

    # 2. Utiliser io.BytesIO pour stocker les données en MÉMOIRE
    request = service.files().get_media(fileId=file_id)
    file_content = io.BytesIO() 
    downloader = MediaIoBaseDownload(file_content, request)

    done = False
    while not done:
        # Le téléchargement se fait dans le buffer file_content
        status, done = downloader.next_chunk()

    # 3. Préparer et renvoyer la réponse binaire
    file_content.seek(0) # Ramène le pointeur au début du buffer
    
    # Retourne le contenu binaire (stocké en mémoire) au client via FastAPI Response
    return Response(
        content=file_content.read(),
        media_type=mime_type,
        headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    )

"""  

uvicorn m1:app --host 127.0.0.1 --port 8000 --reload

"""