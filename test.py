# test_auth_simple.py
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES, REDIRECT_URI

def manual_auth():
    print("🔐 Authentification manuelle Google Drive...")
    
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ Fichier credentials introuvable")
        return
    
    # Supprimer l'ancien token
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("🗑️ Ancien token supprimé")
    
    try:
        # Créer le flow d'authentification
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            SCOPES, 
            redirect_uri=REDIRECT_URI
        )
        
        # Générer l'URL d'authentification
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print(f"\n🌐 Veuillez visiter cette URL dans votre navigateur:")
        print(f"🔗 {auth_url}")
        print("\nAprès autorisation, copiez le code de retour et collez-le ici:")
        
        # Demander le code à l'utilisateur
        code = input("Code: ").strip()
        
        # Échanger le code contre un token
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Sauvegarder le token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print("✅ Authentification réussie!")
        print(f"📄 Token sauvegardé dans: {TOKEN_FILE}")
        
        # Tester le service
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=creds)
        
        # Lister les fichiers pour vérifier
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        print(f"\n📁 {len(files)} fichiers trouvés dans Google Drive:")
        for file in files:
            print(f"  - {file['name']} ({file['id']})")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_auth()