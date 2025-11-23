import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES, REDIRECT_URI
import pickle

class GoogleDriveManager:
    def __init__(self):
        self.service = None
        self.folder_ids = {}
        
    def authenticate(self):
        """Authenticate with Google Drive API using web flow"""
        creds = None
        
        # Token file stores user's access and refresh tokens
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If no valid credentials, return None (user needs to auth via web)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed credentials
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    return None
            else:
                return None
        
        self.service = build('drive', 'v3', credentials=creds)
        return self.service
    
    def get_auth_url(self):
        """Get authorization URL for web flow"""
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES, redirect_uri=REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def handle_callback(self, code):
        """Handle OAuth callback and save credentials"""
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES, redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        return True

    # ... (le reste de vos méthodes reste identique)
    def create_folder(self, folder_name, parent_id=None):
        """Create a folder in Google Drive"""
        if not self.service:
            if not self.authenticate():
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

    # ... (autres méthodes)
    def get_or_create_folder(self, folder_path):
        """Get folder ID or create if doesn't exist"""
        if not self.service:
            self.authenticate()
        
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
    
    
    def upload_file(self, file_path, folder_name=None, file_name=None):
        """Upload a file to Google Drive"""
        if not self.service:
            self.authenticate()
        
        if not file_name:
            file_name = os.path.basename(file_path)
        
        file_metadata = {'name': file_name}
        
        # Add to specific folder if provided
        if folder_name:
            folder_id = self.get_or_create_folder(folder_name)
            if folder_id:
                file_metadata['parents'] = [folder_id]
        
        try:
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Make file shareable
            file_id = file.get('id')
            self.make_file_public(file_id)
            
            return {
                'id': file_id,
                'webViewLink': file.get('webViewLink'),
                'webContentLink': file.get('webContentLink')
            }
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def upload_file_from_bytes(self, file_bytes, file_name, mime_type, folder_name=None):
        """Upload a file from bytes to Google Drive"""
        if not self.service:
            self.authenticate()
        
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
        if not self.service:
            self.authenticate()
        
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
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive"""
        if not self.service:
            self.authenticate()
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_link(self, file_id):
        """Get shareable link for a file"""
        if not self.service:
            self.authenticate()
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink, webContentLink'
            ).execute()
            
            return {
                'webViewLink': file.get('webViewLink'),
                'webContentLink': file.get('webContentLink')
            }
        except Exception as e:
            print(f"Error getting file link: {e}")
            return None


# Global instance
drive_manager = GoogleDriveManager()


