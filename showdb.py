import mysql.connector

def afficher_admins():
    connection = None
    cursor = None
    
    try:
        # Connexion à la base de données
        connection = mysql.connector.connect(
            host="mysql-math-educ-zonantenainasecondraymond-9b74.j.aivencloud.com",
            port=12706,
            user="avnadmin",
            password="AVNS_F4tkvhaLIHxULm3dcZ1",
            database="math_educV2",
            ssl_ca="ca.pem"
        )
        
        cursor = connection.cursor()
        print("✅ Connexion réussie!")
        
        # Sélection de tous les admins
        query = "SELECT * FROM admin"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        
        print("\n📌 Contenu de la table :")
        if len(rows) == 0:
            print("⚠️ Aucun admin trouvé.")
        else:
            for row in rows:
                print(row)
                
    except mysql.connector.Error as e:
        print(f"❌ Erreur MySQL: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Connexion fermée.")

afficher_admins()
