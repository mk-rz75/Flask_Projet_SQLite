# ---------------------------------------------------------------
#  Atelier Flask + SQLite
# ---------------------------------------------------------------
#  Ce fichier est le "cerveau" de votre application : il reçoit
#  les demandes des navigateurs, interroge la base de données
#  et fabrique les réponses.
#
#  Vous allez le compléter petit à petit, exercice après exercice.
#  Les consignes sont dans le dossier "exercices/".
# ---------------------------------------------------------------

import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour signer les sessions (à cacher par la suite)

# Chemin ABSOLU vers la base de données.
# Sur PythonAnywhere, le serveur ne démarre pas forcément dans le dossier
# du projet : un simple 'database.db' créerait une base vide ailleurs !
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db():
    """Ouvre une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour savoir si l'utilisateur s'est authentifié
def est_authentifie():
    return session.get('authentifie')


@app.route('/')
def hello_world():
    return render_template('hello.html')


@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

    # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"


@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password':  # password à cacher par la suite
            session['authentifie'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM commandes WHERE client_id = ? ORDER BY date_commande DESC', (post_id,))
    commandes = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    if not data:
        return "<h2>Client introuvable</h2>", 404

    return render_template('read_data.html', data=data, commandes=commandes)


@app.route('/consultation/')
def ReadBDD():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients ORDER BY nom;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire


@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form.get('nom', '').strip().upper()
    prenom = request.form.get('prenom', '').strip()
    adresse = request.form.get('adresse', '').strip()
    telephone = request.form.get('telephone', '').strip()

    if not nom or not prenom or not adresse:
        return render_template('formulaire.html', erreur="Tous les champs sont obligatoires."), 400

    # Connexion à la base de données
    conn = get_db()
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (nom, prenom, adresse, telephone) VALUES (?, ?, ?, ?)', (nom, prenom, adresse, telephone))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la liste des clients après l'enregistrement


# ---------------------------------------------------------------
#  Ajoutez vos nouvelles routes ci-dessous 👇
# ---------------------------------------------------------------
@app.route('/fiche_nom/<nom>')
def fiche_nom(nom):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/recherche')
def recherche():
    q = request.args.get('q', '').strip()
    data = []
    if q:
        conn = get_db()
        cursor = conn.cursor()
        motif = '%' + q + '%'
        cursor.execute('SELECT * FROM clients WHERE nom LIKE ? OR prenom LIKE ? ORDER BY nom',
                       (motif, motif))
        data = cursor.fetchall()
        conn.close()
    return render_template('recherche.html', q=q, data=data)


@app.route('/supprimer_client/<int:id>', methods=['POST'])
def supprimer_client(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

@app.route('/modifier_client/<int:id>', methods=['GET', 'POST'])
def modifier_client(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute('UPDATE clients SET nom = ?, prenom = ?, adresse = ?, telephone = ? WHERE id = ?',
                (request.form['nom'].strip().upper(),
                request.form['prenom'].strip(),
                request.form['adresse'].strip(),
                request.form.get('telephone', '').strip(),
                id))
        conn.commit()
        conn.close()
        return redirect('/consultation/')

    cursor.execute('SELECT * FROM clients WHERE id = ?', (id,))
    client = cursor.fetchone()
    conn.close()
    if client is None:
        return "<h2>Client introuvable</h2>", 404
    return render_template('modifier_client.html', client=client)

@app.route('/commandes/')
def liste_commandes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT commandes.id, clients.nom, clients.prenom, commandes.produit, commandes.montant
                      FROM commandes
                      JOIN clients ON commandes.client_id = clients.id''')
    commandes = cursor.fetchall()
    conn.close()
    return render_template('commandes.html', commandes=commandes)

@app.route('/statistiques/')
def statistiques():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT clients.nom, COUNT(commandes.id) AS nb_commandes, COALESCE(SUM(commandes.montant), 0) AS total
                      FROM clients
                      LEFT JOIN commandes ON commandes.client_id = clients.id
                      GROUP BY clients.id
                      ORDER BY total DESC''')
    stats = cursor.fetchall()
    conn.close()
    return render_template('statistiques.html', stats=stats)

# ---------------------------------------------------------------
#  Ne pas modifier : utile seulement pour lancer le site
#  sur votre propre ordinateur (python flask_app.py)
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
