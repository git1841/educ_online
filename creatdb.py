import mysql.connector

def ex():
    connection = None
    cursor = None
    
    try:
        # Connexion à la base de données "math_educ"
        connection = mysql.connector.connect(
            host="mysql-math-educ-zonantenainasecondraymond-9b74.j.aivencloud.com",
            port=12706,
            user="avnadmin",
            password="AVNS_F4tkvhaLIHxULm3dcZ1",
            database="math_educV2",
            ssl_ca="ca.pem"
        )
        
        cursor = connection.cursor()
        print('✅ Connexion à la base de données "math_educ" réussie!')
        
        # Création de la table admin
        query = """
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(100) NOT NULL UNIQUE,
            mot_de_passe VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(query)
        connection.commit()
        print("📌 Table 'admin' créée (ou déjà existante).")

        # -----------------------------
        # 🔥 INSERTION DE L'ADMIN ICI
        # -----------------------------
        nom = "admin0"
        mot_de_passe = "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"
        email = "zonantenainasecondraymond123@gmail.com"

        # Vérifier si l'admin existe déjà
        check_query = "SELECT * FROM admin WHERE nom = %s"
        cursor.execute(check_query, (nom,))
        result = cursor.fetchone()

        if result:
            print("ℹ️ L'admin existe déjà, aucune insertion effectuée.")
        else:
            insert_query = """
                INSERT INTO admin (nom, mot_de_passe, email)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (nom, mot_de_passe, email))
            connection.commit()
            print("✅ Nouvel admin inséré avec succès !")

    except mysql.connector.Error as e:
        print(f"❌ Erreur MySQL: {e}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print('\n🔌 Connexion fermée.')

ex()
