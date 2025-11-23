# import os
# from dotenv import load_dotenv

# # load_dotenv()

# # # MySQL Configuration
# # MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
# # MYSQL_USER = os.getenv("MYSQL_USER", "root")
# # MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
# # MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "math1")

# # Google Drive Configuration
# # CREDENTIALS_FILE = "conf.json"
# # TOKEN_FILE = "token.json"
# # SCOPES = ['https://www.googleapis.com/auth/drive.file']
# # REDIRECT_URI = "http://127.0.0.1:8000/callback"  # ← CHANGÉ de 8080 à 8000



# CREDENTIALS_FILE = "conf.json"  # Ton fichier OAuth2 téléchargé depuis Google Cloud 
# TOKEN_FILE = "token.json"
# SCOPES = ['https://www.googleapis.com/auth/drive.file']
# REDIRECT_URI = "http://127.0.0.1:8000/callback"


# # Application Configuration
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# UPLOAD_FOLDER = "uploads"
# MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# # Session Configuration
# SESSION_LIFETIME = 24 * 60 * 60  # 24 hours

# # Google Drive Folders
# DRIVE_FOLDERS = {
#     "profile_pictures": "profile_pictures",
#     "group_avatars": "group_avatars",
#     "educational_content": "educational_content",
#     "pdf": "educational_content/pdf",
#     "videos": "educational_content/videos",
#     "images": "educational_content/images",
#     "books": "educational_content/books",
#     "shared_files": "shared_files",
#     "call_recordings": "call_recordings"
# }







import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "math1")

# Google Drive Configuration - UTILISEZ localhost au lieu de 127.0.0.1
CREDENTIALS_FILE = "conf.json"
TOKEN_FILE = "token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Application Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
UPLOAD_FOLDER = "uploads"
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Session Configuration
SESSION_LIFETIME = 24 * 60 * 60  # 24 hours

# Google Drive Folders
DRIVE_FOLDERS = {
    "profile_pictures": "profile_pictures",
    "group_avatars": "group_avatars",
    "educational_content": "educational_content",
    "pdf": "educational_content/pdf",
    "videos": "educational_content/videos",
    "images": "educational_content/images",
    "books": "educational_content/books",
    "shared_files": "shared_files",
    "call_recordings": "call_recordings"
}




