import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES

class GoogleDriveManager:
    def __init__(self):
        self.service = None
        self.folder_ids = {}
        
    def authenticate(self):
        """Authenticate with Google Drive API using web flow"""
        creds = None
        
        # Token file stores user's access and refresh tokens
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                print("✅ Token loaded from file")
            except Exception as e:
                print(f"❌ Error loading token: {e}")
                return None
        
        # If no valid credentials, return None (user needs to auth via web)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed credentials
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    print("✅ Token refreshed")
                except Exception as e:
                    print(f"❌ Error refreshing token: {e}")
                    return None
            else:
                print("❌ No valid credentials - need web authentication")
                return None
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive service built successfully")
            return self.service
        except Exception as e:
            print(f"❌ Failed to build service: {e}")
            return None
    
    def get_auth_url(self):
        """Get authorization URL for web flow"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, 
                SCOPES, 
                redirect_uri="http://127.0.0.1:8000/callback"
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url
        except Exception as e:
            print(f"❌ Error getting auth URL: {e}")
            return None
    
    def handle_callback(self, code):
        """Handle OAuth callback and save credentials"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, 
                SCOPES, 
                redirect_uri="http://127.0.0.1:8000/callback"
            )
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Save credentials
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ OAuth callback handled successfully")
            return True
        except Exception as e:
            print(f"❌ Error handling callback: {e}")
            return False

    def ensure_authenticated(self):
        """Ensure service is authenticated before any operation"""
        if not self.service:
            return self.authenticate()
        return True
    
    def create_folder(self, folder_name, parent_id=None):
        """Create a folder in Google Drive"""
        if not self.ensure_authenticated():
            return None
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            self.folder_ids[folder_name] = folder_id
            return folder_id
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
    
    def get_or_create_folder(self, folder_path):
        """Get folder ID or create if doesn't exist"""
        if not self.ensure_authenticated():
            return None
        
        # Check if folder exists in cache
        if folder_path in self.folder_ids:
            return self.folder_ids[folder_path]
        
        # Search for folder
        try:
            query = f"name='{folder_path}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                folder_id = files[0]['id']
                self.folder_ids[folder_path] = folder_id
                return folder_id
            else:
                # Create folder if doesn't exist
                return self.create_folder(folder_path)
        except Exception as e:
            print(f"Error getting/creating folder: {e}")
            return None
    
    def upload_file_from_bytes(self, file_bytes, file_name, mime_type, folder_name=None):
        """Upload a file from bytes to Google Drive"""
        if not self.ensure_authenticated():
            return None
        
        file_metadata = {'name': file_name}
        
        if folder_name:
            folder_id = self.get_or_create_folder(folder_name)
            if folder_id:
                file_metadata['parents'] = [folder_id]
        
        try:
            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            file_id = file.get('id')
            self.make_file_public(file_id)
            
            return {
                'id': file_id,
                'webViewLink': file.get('webViewLink'),
                'webContentLink': file.get('webContentLink')
            }
        except Exception as e:
            print(f"Error uploading file from bytes: {e}")
            return None
    
    def make_file_public(self, file_id):
        """Make a file publicly accessible"""
        if not self.ensure_authenticated():
            return False
        
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()
            return True
        except Exception as e:
            print(f"Error making file public: {e}")
            return False
    
    def get_direct_image_url(self, file_id, size='w500'):

        return f"https://drive.google.com/thumbnail?id={file_id}&sz={size}"

    def get_direct_download_url(self, file_id):
        """Get direct download URL for files"""
        return f"https://drive.google.com/uc?id={file_id}&export=download"

# Global instance
drive_manager = GoogleDriveManager()