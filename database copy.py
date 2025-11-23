import mysql.connector
from mysql.connector import Error
#from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "math1"

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
    


def init_database():
    """Initialize database with all required tables"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        # Users table
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
        
        # Admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                mot_de_passe VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Contents table
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
        
        connection.commit()
        print("Database initialized successfully!")
        
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_database()