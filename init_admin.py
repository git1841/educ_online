"""
Script pour créer un administrateur initial
"""
from database import get_db_connection
from auth import hash_password

def create_admin():
    """Créer un compte administrateur"""
    print("=== Création d'un administrateur ===\n")
    
    nom = input("Nom d'administrateur: ")
    mot_de_passe = input("Mot de passe: ")
    email = input("Email (optionnel): ")
    
    conn = get_db_connection()
    if not conn:
        print("❌ Erreur de connexion à la base de données")
        return
    
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'admin existe déjà
        cursor.execute("SELECT id FROM admin WHERE nom = %s", (nom,))
        if cursor.fetchone():
            print(f"❌ Un administrateur avec le nom '{nom}' existe déjà")
            return
        
        # Hasher le mot de passe
        hashed_pwd = hash_password(mot_de_passe)
        
        # Insérer l'admin
        cursor.execute("""
            INSERT INTO admin (nom, mot_de_passe, email)
            VALUES (%s, %s, %s)
        """, (nom, hashed_pwd, email if email else None))
        
        conn.commit()
        
        print(f"\n✅ Administrateur '{nom}' créé avec succès!")
        print(f"🔐 Vous pouvez maintenant vous connecter sur /login")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur: {e}")
    finally:
        cursor.close()
        conn.close()

def list_admins():
    """Lister tous les administrateurs"""
    conn = get_db_connection()
    if not conn:
        print("❌ Erreur de connexion à la base de données")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, nom, email, created_at FROM admin")
        admins = cursor.fetchall()
        
        if not admins:
            print("\n📋 Aucun administrateur dans la base de données")
            return
        
        print("\n📋 Administrateurs existants:")
        print("-" * 70)
        for admin in admins:
            print(f"ID: {admin['id']}")
            print(f"Nom: {admin['nom']}")
            print(f"Email: {admin['email']}")
            print(f"Créé le: {admin['created_at']}")
            print("-" * 70)
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║     GESTION DES ADMINISTRATEURS                      ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    
    while True:
        print("\nOptions:")
        print("1. Créer un nouvel administrateur")
        print("2. Lister les administrateurs")
        print("3. Quitter")
        
        choice = input("\nVotre choix: ")
        
        if choice == "1":
            create_admin()
        elif choice == "2":
            list_admins()
        elif choice == "3":
            print("\n👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")