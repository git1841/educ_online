import mysql.connector
from mysql.connector import Error





# MYSQL_HOST = "localhost" 
# MYSQL_USER = "root" 
# MYSQL_PASSWORD = "" 
# MYSQL_DATABASE = "math1" 

# def get_db_connection():
#     """Create and return a database connection"""
#     try:
#         connection = mysql.connector.connect(
#             host=MYSQL_HOST,
#             user=MYSQL_USER,
#             password=MYSQL_PASSWORD,
#             database=MYSQL_DATABASE
#         )
#         return connection
#     except Error as e:
#         print(f"Error connecting to MySQL: {e}")
#         return None









# --- Paramètres de Connexion Aiven (Utilisation des variables Aiven) --- 
MYSQL_HOST = "mysql-math-educ-zonantenainasecondraymond-9b74.j.aivencloud.com" 
MYSQL_PORT = 12706
MYSQL_USER = "avnadmin"
MYSQL_PASSWORD = "AVNS_F4tkvhaLIHxULm3dcZ1"
MYSQL_DATABASE = "math_educV2"
MYSQL_SSL_CA = "ca.pem"

# ------------------------------------------------------------------------

# La fonction get_db_connection est simplifiée pour retourner la connexion Aiven si elle est nécessaire ailleurs.
def get_db_connection():
    """Create and return a database connection to math_educ."""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            ssl_ca=MYSQL_SSL_CA
        )
        return connection
    except Error as e:
        print(f"❌ Erreur de connexion à MySQL Aiven: {e}")
        return None






def init_database():
    """Initialize database with all required tables on the Aiven server."""
    connection = None
    cursor = None
    
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            ssl_ca=MYSQL_SSL_CA
        )
        
        cursor = connection.cursor()
    
        
        print("✅ Connexion réussie à la base de données 'math_educV2'.")
        
        # 2. Création des tables (la commande USE n'est plus nécessaire car 'database' est spécifié)
        
        # Admin table (créée en premier car 'contents' et 'warnings' y font référence)
        print("  - Création de la table 'admin'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                mot_de_passe VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users table (créée avant les tables de conversations et de requêtes qui y font référence)
        print("  - Création de la table 'users'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100),
                phone VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                user_type ENUM('free', 'pro', 'admin') DEFAULT 'free',
                class_level VARCHAR(50),
                filiere VARCHAR(100),
                profile_picture VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_phone (phone)
            )
        """)
        
        # Contents table
        print("  - Création de la table 'contents'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                drive_file_id VARCHAR(255),
                drive_link VARCHAR(500),
                content_type ENUM('pdf', 'video', 'image', 'book', 'audio') NOT NULL,
                access_type ENUM('free', 'pro') DEFAULT 'free',
                class_level VARCHAR(50),
                subject VARCHAR(100),
                uploaded_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES admin(id) ON DELETE SET NULL
            )
        """)
        
        # Conversations table
        print("  - Création de la table 'conversations'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                conversation_type ENUM('private', 'group') NOT NULL,
                created_by INT NOT NULL,
                group_photo VARCHAR(500),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Conversation participants
        print("  - Création de la table 'conversation_participants'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_participants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                user_id INT NOT NULL,
                role ENUM('admin', 'member') DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_participant (conversation_id, user_id)
            )
        """)
        
        # Messages table
        print("  - Création de la table 'messages'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                sender_id INT NOT NULL,
                message_type ENUM('text', 'image', 'video', 'audio', 'file') DEFAULT 'text',
                content TEXT,
                file_url VARCHAR(500),
                drive_file_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Video calls table
        print("  - Création de la table 'video_calls'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_calls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                initiated_by INT NOT NULL,
                call_type ENUM('group', 'private') NOT NULL,
                status ENUM('active', 'ended') DEFAULT 'active',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (initiated_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Admin publications table
        print("  - Création de la table 'admin_publications'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_publications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                target_audience ENUM('all', 'free', 'pro') DEFAULT 'all',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
            )
        """)
        
        # Group requests table
        print("  - Création de la table 'group_requests'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_name VARCHAR(255) NOT NULL,
                description TEXT,
                requested_by INT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP NULL,
                FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Warnings table
        print("  - Création de la table 'warnings'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                admin_id INT NOT NULL,
                reason TEXT NOT NULL,
                warning_type ENUM('minor', 'major', 'critical') DEFAULT 'minor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
            )
        """)
        
        
        
        
        # AJOUTER CETTE NOUVELLE TABLE DANS database.py (fonction init_database)

        # Pro upgrade requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pro_upgrade_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                operator VARCHAR(50) NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                transaction_id VARCHAR(100) NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                proof_image VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP NULL,
                reviewed_by INT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (reviewed_by) REFERENCES admin(id) ON DELETE SET NULL
            )
        """)

        # Group invite requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_invite_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id INT NOT NULL,
                invited_user_id INT NOT NULL,
                invited_by INT NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP NULL,
                FOREIGN KEY (group_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (invited_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_invite (group_id, invited_user_id, status)
            )
        """)

        print("✅ Nouvelles tables créées: pro_upgrade_requests, group_invite_requests")
                
                
        
        
        connection.commit()
        print("\n🎉 Toutes les tables ont été initialisées avec succès dans 'math_educ'!")
        
    except Error as e:
        print(f"\n❌ Erreur lors de l'initialisation de la base de données: {e}")
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Connexion fermée.")

if __name__ == "__main__":
    init_database()