import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))

conn.executescript('''
DROP TABLE IF EXISTS emprunts;
DROP TABLE IF EXISTS livres;
DROP TABLE IF EXISTS utilisateurs;
CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    isbn TEXT,
    annee INTEGER,
    genre TEXT,
    nb_exemplaires INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    mot_de_passe_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);
CREATE TABLE emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER NOT NULL,
    utilisateur_id INTEGER NOT NULL,
    date_emprunt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_retour_prevue DATE NOT NULL,
    date_retour TIMESTAMP,
    FOREIGN KEY (livre_id) REFERENCES livres (id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id)
);
''')

livres = [
    ('Le Petit Prince', 'Antoine de Saint-Exupéry', '9782070612758', 1943, 'Conte', 3),
    ('Les Misérables', 'Victor Hugo', '9782253096344', 1862, 'Roman', 2),
    ('1984', 'George Orwell', '9782070368228', 1949, 'Science-fiction', 2),
    ("L'Étranger", 'Albert Camus', '9782070360024', 1942, 'Roman', 1),
    ('Harry Potter à l\'école des sorciers', 'J.K. Rowling', '9782070584628', 1997, 'Fantasy', 4),
    ('Le Seigneur des anneaux', 'J.R.R. Tolkien', '9782266282369', 1954, 'Fantasy', 1),
    ('Germinal', 'Émile Zola', '9782253004226', 1885, 'Roman', 2),
    ('Fondation', 'Isaac Asimov', '9782070360536', 1951, 'Science-fiction', 1),
    ('Le Comte de Monte-Cristo', 'Alexandre Dumas', '9782253098058', 1844, 'Aventure', 2),
    ('Madame Bovary', 'Gustave Flaubert', '9782253004868', 1857, 'Roman', 1),
]
conn.executemany('INSERT INTO livres (titre, auteur, isbn, annee, genre, nb_exemplaires) VALUES (?, ?, ?, ?, ?, ?)', livres)

utilisateurs = [
    ('admin', 'ADMIN', 'Admin', generate_password_hash('password'), 'admin'),
    ('user', 'DUPONT', 'Emilie', generate_password_hash('12345'), 'user'),
    ('user2', 'MARTIN', 'Lucas', generate_password_hash('12345'), 'user'),
]
conn.executemany('INSERT INTO utilisateurs (login, nom, prenom, mot_de_passe_hash, role) VALUES (?, ?, ?, ?, ?)', utilisateurs)

conn.commit()
conn.close()
print("Tables de la bibliothèque créées")
