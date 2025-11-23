from flask import Flask
import requests
import os

app = Flask(__name__)

API_URL = "https://fastapi-blog-zonantenainasecondraymond9003-uclkvshl.leapcell.dev/personnes"

def get_html_content(personnes):
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Liste des Personnes</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ 
            color: #333; 
            text-align: center;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }}
        th {{ 
            background-color: #4CAF50; 
            color: white; 
        }}
        tr:nth-child(even) {{ 
            background-color: #f9f9f9; 
        }}
        tr:hover {{ 
            background-color: #f1f1f1; 
        }}
        .success {{ 
            color: #4CAF50; 
            font-weight: bold; 
            text-align: center;
        }}
        .error {{ 
            color: #f44336; 
            font-weight: bold; 
            text-align: center;
        }}
        .count {{
            background: #e7f3ff;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Liste des Personnes</h1>
        
        <div class="count">
            ✅ {len(personnes)} personne(s) trouvée(s)
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nom</th>
                    <th>Prénom</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f"""
                <tr>
                    <td>{p['id']}</td>
                    <td>{p['nom']}</td>
                    <td>{p['prenom']}</td>
                </tr>
                """ for p in personnes])}
            </tbody>
        </table>
    </div>
</body>
</html>
'''

@app.route('/')
def afficher_personnes():
    try:
        # Faire la requête à l'API FastAPI
        response = requests.get(API_URL)
        data = response.json()
        
        # Vérifier si la requête a réussi
        if data.get("status") == "success":
            personnes = data.get("data", [])
            return get_html_content(personnes)
        else:
            return f'''
            <div style="text-align: center; margin: 50px;">
                <h1 style="color: #f44336;">❌ Erreur</h1>
                <p>Erreur API: {data.get('message', 'Erreur inconnue')}</p>
            </div>
            '''
            
    except Exception as e:
        return f'''
        <div style="text-align: center; margin: 50px;">
            <h1 style="color: #f44336;">❌ Erreur de connexion</h1>
            <p>{str(e)}</p>
        </div>
        '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
