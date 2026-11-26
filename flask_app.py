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
from werkzeug.security import generate_password_hash, check_password_hash

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


def message(titre, texte, code=200, lien='/livres'):
    return render_template('message.html', titre=titre, message=texte, lien=lien), code


def acces_refuse():
    return message('Accès refusé', 'Cette page est réservée aux administrateurs.', 403, '/')


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
        login = request.form.get('username', '').strip()
        mot_de_passe = request.form.get('password', '')
        conn = get_db()
        utilisateur = conn.execute('SELECT * FROM utilisateurs WHERE login = ?', (login,)).fetchone()
        conn.close()
        if utilisateur and check_password_hash(utilisateur['mot_de_passe_hash'], mot_de_passe):
            session.clear()
            session['authentifie'] = True
            session['utilisateur'] = utilisateur['login']
            session['utilisateur_id'] = utilisateur['id']
            session['role'] = utilisateur['role']
            return redirect('/livres')
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
#  Projet bibliothèque
# ---------------------------------------------------------------

REQUETE_LIVRES = '''SELECT livres.*,
                         livres.nb_exemplaires - COUNT(emprunts.id) AS nb_disponibles
                  FROM livres
                  LEFT JOIN emprunts ON emprunts.livre_id = livres.id AND emprunts.date_retour IS NULL'''


@app.route('/livres')
def liste_livres():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    q = request.args.get('q', '').strip()
    motif = '%' + q + '%'
    conn = get_db()
    livres = conn.execute(REQUETE_LIVRES + '''
                          WHERE livres.titre LIKE ? OR livres.auteur LIKE ?
                          GROUP BY livres.id
                          ORDER BY livres.titre''', (motif, motif)).fetchall()
    conn.close()
    return render_template('livres.html', livres=livres, q=q)


@app.route('/admin')
def admin():
    if not a_le_role('admin'):
        return acces_refuse()
    return render_template('admin.html')


def lire_formulaire_livre():
    livre = {
        'titre': request.form.get('titre', '').strip(),
        'auteur': request.form.get('auteur', '').strip(),
        'isbn': request.form.get('isbn', '').strip(),
        'annee': request.form.get('annee', '').strip(),
        'genre': request.form.get('genre', '').strip(),
        'nb_exemplaires': request.form.get('nb_exemplaires', '').strip(),
    }
    if not livre['titre'] or not livre['auteur']:
        return livre, "Le titre et l'auteur sont obligatoires."
    if livre['annee'] and not livre['annee'].isdigit():
        return livre, "L'année doit être un nombre."
    if not livre['nb_exemplaires'].isdigit():
        return livre, "Le nombre d'exemplaires doit être un nombre positif."
    livre['annee'] = int(livre['annee']) if livre['annee'] else None
    livre['nb_exemplaires'] = int(livre['nb_exemplaires'])
    return livre, None


@app.route('/admin/livres/ajouter', methods=['GET', 'POST'])
def ajouter_livre():
    if not a_le_role('admin'):
        return acces_refuse()
    if request.method == 'GET':
        return render_template('livre_form.html', titre_page='Ajouter un livre', livre={})

    livre, erreur = lire_formulaire_livre()
    if erreur:
        return render_template('livre_form.html', titre_page='Ajouter un livre', livre=livre, erreur=erreur), 400

    conn = get_db()
    conn.execute('INSERT INTO livres (titre, auteur, isbn, annee, genre, nb_exemplaires) VALUES (?, ?, ?, ?, ?, ?)',
                 (livre['titre'], livre['auteur'], livre['isbn'], livre['annee'], livre['genre'], livre['nb_exemplaires']))
    conn.commit()
    conn.close()
    return redirect('/livres')


@app.route('/admin/livres/<int:id>/modifier', methods=['GET', 'POST'])
def modifier_livre(id):
    if not a_le_role('admin'):
        return acces_refuse()
    conn = get_db()
    livre_actuel = conn.execute('SELECT * FROM livres WHERE id = ?', (id,)).fetchone()
    if livre_actuel is None:
        conn.close()
        return message('Livre introuvable', "Ce livre n'existe pas.", 404)

    if request.method == 'GET':
        conn.close()
        return render_template('livre_form.html', titre_page='Modifier un livre', livre=livre_actuel)

    livre, erreur = lire_formulaire_livre()
    if not erreur:
        en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE livre_id = ? AND date_retour IS NULL', (id,)).fetchone()[0]
        if livre['nb_exemplaires'] < en_cours:
            erreur = f"Impossible : {en_cours} exemplaire(s) de ce livre sont en cours d'emprunt."
    if erreur:
        conn.close()
        return render_template('livre_form.html', titre_page='Modifier un livre', livre=livre, erreur=erreur), 400

    conn.execute('UPDATE livres SET titre = ?, auteur = ?, isbn = ?, annee = ?, genre = ?, nb_exemplaires = ? WHERE id = ?',
                 (livre['titre'], livre['auteur'], livre['isbn'], livre['annee'], livre['genre'], livre['nb_exemplaires'], id))
    conn.commit()
    conn.close()
    return redirect('/livres')


@app.route('/admin/livres/<int:id>/supprimer', methods=['POST'])
def supprimer_livre(id):
    if not a_le_role('admin'):
        return acces_refuse()
    conn = get_db()
    try:
        en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE livre_id = ? AND date_retour IS NULL', (id,)).fetchone()[0]
        if en_cours > 0:
            return message('Suppression impossible', f"Ce livre a {en_cours} exemplaire(s) en cours d'emprunt.", 409)
        conn.execute('DELETE FROM livres WHERE id = ?', (id,))
        conn.commit()
    except sqlite3.IntegrityError:
        return message('Suppression impossible', "Ce livre a un historique d'emprunts. Mettez plutôt son nombre d'exemplaires à 0.", 409)
    finally:
        conn.close()
    return redirect('/livres')


MAX_EMPRUNTS = 3


@app.route('/emprunter/<int:livre_id>', methods=['POST'])
def emprunter(livre_id):
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    utilisateur_id = session['utilisateur_id']
    conn = get_db()
    try:
        livre = conn.execute(REQUETE_LIVRES + '''
                             WHERE livres.id = ?
                             GROUP BY livres.id''', (livre_id,)).fetchone()
        if livre is None:
            return message('Livre introuvable', "Ce livre n'existe pas.", 404)
        if livre['nb_disponibles'] <= 0:
            return message('Emprunt impossible', f"Tous les exemplaires de « {livre['titre']} » sont déjà empruntés.", 409)

        nb_en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE utilisateur_id = ? AND date_retour IS NULL',
                                   (utilisateur_id,)).fetchone()[0]
        if nb_en_cours >= MAX_EMPRUNTS:
            return message('Emprunt impossible', f"Vous avez déjà {MAX_EMPRUNTS} livres en cours d'emprunt. Rendez-en un avant d'en emprunter un autre.", 409, '/mes_emprunts')

        deja = conn.execute('SELECT COUNT(*) FROM emprunts WHERE utilisateur_id = ? AND livre_id = ? AND date_retour IS NULL',
                            (utilisateur_id, livre_id)).fetchone()[0]
        if deja:
            return message('Emprunt impossible', f"Vous avez déjà emprunté « {livre['titre']} ».", 409, '/mes_emprunts')

        conn.execute("INSERT INTO emprunts (livre_id, utilisateur_id, date_retour_prevue) VALUES (?, ?, date('now', '+14 days'))",
                     (livre_id, utilisateur_id))
        conn.commit()
    finally:
        conn.close()
    return redirect('/mes_emprunts')


@app.route('/mes_emprunts')
def mes_emprunts():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    requete = '''SELECT emprunts.*, livres.titre, livres.auteur
                 FROM emprunts
                 JOIN livres ON emprunts.livre_id = livres.id
                 WHERE emprunts.utilisateur_id = ? AND emprunts.date_retour IS {} NULL
                 ORDER BY emprunts.date_emprunt DESC'''
    en_cours = conn.execute(requete.format(''), (session['utilisateur_id'],)).fetchall()
    historique = conn.execute(requete.format('NOT'), (session['utilisateur_id'],)).fetchall()
    conn.close()
    return render_template('mes_emprunts.html', en_cours=en_cours, historique=historique)


@app.route('/rendre/<int:emprunt_id>', methods=['POST'])
def rendre(emprunt_id):
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    try:
        emprunt = conn.execute('SELECT * FROM emprunts WHERE id = ? AND date_retour IS NULL', (emprunt_id,)).fetchone()
        if emprunt is None:
            return message('Retour impossible', "Cet emprunt n'existe pas ou le livre a déjà été rendu.", 404, '/mes_emprunts')
        if emprunt['utilisateur_id'] != session['utilisateur_id'] and not a_le_role('admin'):
            return message('Accès refusé', "Cet emprunt ne vous appartient pas.", 403, '/mes_emprunts')
        conn.execute('UPDATE emprunts SET date_retour = CURRENT_TIMESTAMP WHERE id = ?', (emprunt_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(request.referrer or '/mes_emprunts')


def page_utilisateurs(erreur=None, form=None, code=200):
    conn = get_db()
    utilisateurs = conn.execute('''SELECT utilisateurs.*, COUNT(emprunts.id) AS nb_en_cours
                                  FROM utilisateurs
                                  LEFT JOIN emprunts ON emprunts.utilisateur_id = utilisateurs.id AND emprunts.date_retour IS NULL
                                  GROUP BY utilisateurs.id
                                  ORDER BY utilisateurs.login''').fetchall()
    conn.close()
    return render_template('utilisateurs.html', utilisateurs=utilisateurs, erreur=erreur, form=form or {}), code


@app.route('/admin/utilisateurs')
def liste_utilisateurs():
    if not a_le_role('admin'):
        return acces_refuse()
    return page_utilisateurs()


@app.route('/admin/utilisateurs/ajouter', methods=['POST'])
def ajouter_utilisateur():
    if not a_le_role('admin'):
        return acces_refuse()
    login = request.form.get('login', '').strip()
    nom = request.form.get('nom', '').strip().upper()
    prenom = request.form.get('prenom', '').strip()
    mot_de_passe = request.form.get('mot_de_passe', '')
    role = request.form.get('role', 'user')

    if not login or not nom or not prenom or not mot_de_passe:
        return page_utilisateurs('Tous les champs sont obligatoires.', request.form, 400)
    if role not in ('user', 'admin'):
        return page_utilisateurs('Rôle invalide.', request.form, 400)

    conn = get_db()
    try:
        conn.execute('INSERT INTO utilisateurs (login, nom, prenom, mot_de_passe_hash, role) VALUES (?, ?, ?, ?, ?)',
                     (login, nom, prenom, generate_password_hash(mot_de_passe), role))
        conn.commit()
    except sqlite3.IntegrityError:
        return page_utilisateurs(f"Le login « {login} » existe déjà.", request.form, 409)
    finally:
        conn.close()
    return redirect('/admin/utilisateurs')


@app.route('/admin/utilisateurs/<int:id>/supprimer', methods=['POST'])
def supprimer_utilisateur(id):
    if not a_le_role('admin'):
        return acces_refuse()
    if id == session.get('utilisateur_id'):
        return message('Suppression impossible', 'Vous ne pouvez pas supprimer votre propre compte.', 409, '/admin/utilisateurs')
    conn = get_db()
    try:
        en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE utilisateur_id = ? AND date_retour IS NULL', (id,)).fetchone()[0]
        if en_cours > 0:
            return message('Suppression impossible', f"Cet utilisateur a encore {en_cours} livre(s) en cours d'emprunt.", 409, '/admin/utilisateurs')
        conn.execute('DELETE FROM utilisateurs WHERE id = ?', (id,))
        conn.commit()
    except sqlite3.IntegrityError:
        return message('Suppression impossible', "Cet utilisateur a un historique d'emprunts.", 409, '/admin/utilisateurs')
    finally:
        conn.close()
    return redirect('/admin/utilisateurs')


@app.route('/admin/emprunts')
def admin_emprunts():
    if not a_le_role('admin'):
        return acces_refuse()
    conn = get_db()
    emprunts = conn.execute('''SELECT emprunts.*, livres.titre, utilisateurs.login, utilisateurs.nom, utilisateurs.prenom
                              FROM emprunts
                              JOIN livres ON emprunts.livre_id = livres.id
                              JOIN utilisateurs ON emprunts.utilisateur_id = utilisateurs.id
                              WHERE emprunts.date_retour IS NULL
                              ORDER BY emprunts.date_retour_prevue''').fetchall()
    conn.close()
    return render_template('admin_emprunts.html', emprunts=emprunts)


def livre_en_json(livre):
    donnees = dict(livre)
    donnees['disponible'] = livre['nb_disponibles'] > 0
    return donnees


@app.get('/api/livres')
def api_liste_livres():
    q = request.args.get('q', '').strip()
    motif = '%' + q + '%'
    conn = get_db()
    livres = conn.execute(REQUETE_LIVRES + '''
                          WHERE livres.titre LIKE ? OR livres.auteur LIKE ?
                          GROUP BY livres.id
                          ORDER BY livres.titre''', (motif, motif)).fetchall()
    conn.close()
    return jsonify([livre_en_json(livre) for livre in livres])


@app.get('/api/livres/<int:id>')
def api_un_livre(id):
    conn = get_db()
    livre = conn.execute(REQUETE_LIVRES + '''
                         WHERE livres.id = ?
                         GROUP BY livres.id''', (id,)).fetchone()
    conn.close()
    if livre is None:
        return jsonify({'erreur': 'Livre introuvable'}), 404
    return jsonify(livre_en_json(livre))


# ---------------------------------------------------------------
#  Ne pas modifier : utile seulement pour lancer le site
#  sur votre propre ordinateur (python flask_app.py)
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
