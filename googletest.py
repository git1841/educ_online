from flask import Flask, request, redirect, session, url_for, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import tempfile

app = Flask(__name__)
app.secret_key = "votre_secret_key"

# Configuration OAuth2
CLIENT_CONFIG = {
    "web": {
        "client_id": "372217163447-2fovic97mbfdjm6cs9p76i5bgoimjfo9.apps.googleusercontent.com",
        "project_id": "math-educ",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["https://math-educ.onrender.com/oauth2callback"]
    }
}

SCOPES = ['https://www.googleapis.com/auth/drive.file']

@app.route('/')
def index():
    return '''
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png">
        <input type="submit" value="Upload to Google Drive">
    </form>
    '''

@app.route('/auth')
def auth():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri='https://math-educ.onrender.com/oauth2callback'
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        state=session['state'],
        redirect_uri='https://math-educ.onrender.com/oauth2callback'
    )
    
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect('/upload')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'credentials' not in session:
        return redirect('/auth')
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        
        if file:
            # Sauvegarder le fichier temporairement
            temp_path = os.path.join(tempfile.gettempdir(), file.filename)
            file.save(temp_path)
            
            # Upload vers Google Drive
            credentials_dict = session['credentials']
            credentials = Credentials(
                token=credentials_dict['token'],
                refresh_token=credentials_dict['refresh_token'],
                token_uri=credentials_dict['token_uri'],
                client_id=credentials_dict['client_id'],
                client_secret=credentials_dict['client_secret'],
                scopes=credentials_dict['scopes']
            )
            
            service = build('drive', 'v3', credentials=credentials)
            
            file_metadata = {
                'name': file.filename,
                'mimeType': file.mimetype
            }
            
            media = MediaFileUpload(temp_path, mimetype=file.mimetype)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_path)
            
            return f'File uploaded successfully! File ID: {uploaded_file.get("id")}'
    
    return '''
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png">
        <input type="submit" value="Upload">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
