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

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

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
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Fonction pour savoir si l'utilisateur s'est authentifié
def est_authentifie():
    return session.get('authentifie')
def a_le_role(*roles):
    return session.get('role') in roles


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


COMPTES = {
    'admin': {'mot_de_passe': 'password', 'role': 'admin'},
    'user': {'mot_de_passe': '12345', 'role': 'user'},
}

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        compte = COMPTES.get(request.form['username'])
        if compte and request.form['password'] == compte['mot_de_passe']:
            session['authentifie'] = True
            session['utilisateur'] = request.form['username']
            session['role'] = compte['role']
            return redirect(url_for('lecture'))
        return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
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
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients ORDER BY nom;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    return render_template('formulaire.html')  # afficher le formulaire


@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
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
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/recherche')
def recherche():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
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
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    conn = get_db()
    try:
        conn.execute('DELETE FROM clients WHERE id = ?', (id,))
        conn.commit()
    except sqlite3.IntegrityError:
        return "<h2>Impossible de supprimer ce client : il a des commandes.</h2>", 409
    finally:
        conn.close()
    return redirect('/consultation/')

@app.route('/modifier_client/<int:id>', methods=['GET', 'POST'])
def modifier_client(id):
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
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

@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect('/')

@app.get('/api/clients')
def api_liste_clients():
    conn = get_db()
    rows = conn.execute('SELECT * FROM clients ORDER BY nom').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.get('/api/clients/<int:id>')
def api_un_client(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({'erreur': 'Client introuvable'}), 404
    return jsonify(dict(row))

@app.post('/api/clients')
def api_creer_client():
    if not a_le_role('admin'):
        return jsonify({'erreur': 'Authentification administrateur requise'}), 401
    donnees = request.get_json(silent=True) or {}
    nom = str(donnees.get('nom', '')).strip().upper()
    prenom = str(donnees.get('prenom', '')).strip()
    adresse = str(donnees.get('adresse', '')).strip()

    if not nom or not prenom or not adresse:
        return jsonify({'erreur': 'Les champs nom, prenom et adresse sont obligatoires'}), 400

    conn = get_db()
    cursor = conn.execute('INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)',
                          (nom, prenom, adresse))
    conn.commit()
    nouvel_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': nouvel_id, 'nom': nom, 'prenom': prenom, 'adresse': adresse}), 201

# ---------------------------------------------------------------
#  Ne pas modifier : utile seulement pour lancer le site
#  sur votre propre ordinateur (python flask_app.py)
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
