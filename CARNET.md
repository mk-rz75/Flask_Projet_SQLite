# 📒 Mon carnet de bord

**Nom :KASDI

**Prénom : Mohamed

**Adresse de mon site : https://mkrz75.pythonanywhere.com/

**Adresse de mon dépôt GitHub : https://github.com/mk-rz75/Flask_Projet_SQLite

> Modifiez ce fichier directement sur GitHub (icône crayon ✏️) pour répondre aux questions de chaque exercice.
> Écrivez avec vos propres mots : une réponse courte et juste vaut mieux qu'un long copier-coller ! 🙂

---

## 🟢 Exercice 1 — Explorer la base en SQL

1. Expliquez avec vos mots la différence entre une **table**, une **colonne** et une **ligne**.

   > _Ma réponse :_ Une table est tableau qui regroupe les information. Une colonne c'est les informations de chaque personne tels que : nom,. prenom, adresse. Une ligne c'est une recherche précise de la personne.

2. À quoi sert la clé primaire `id` ? Pourquoi ne pas simplement identifier un client par son nom ?

   > _Ma réponse : Car l'id est une identification unique n'ayant pas de doublon. On peux identifier un client par son nom mais son nom n'est pas unique il peux en exister plusieurs.

3. Pourquoi votre client ajouté en console est-il apparu sur le site ?

   > _Ma réponse : Le client apparaît sur le site parce que le site et la console SQL utilisent la même base de données.

4. Que signifie `NOT NULL` dans `schema.sql` ? Quelle erreur avez-vous obtenue avec `INSERT INTO clients (nom) VALUES ('TEST');` ?

   > _Ma réponse : NOT NULL signifie qu'on n'accepte pas de case vide. NOT NULL constraint failed: clients.prenom

🧩 **Défi** — mes requêtes / ma solution :

   > 

---

## 🟢 Exercice 2 — Afficher les données proprement

1. Décrivez avec vos mots le trajet d'une requête, du navigateur jusqu'à la base de données, puis le retour.

   > _Ma réponse : Quand je vais sur consultation, le navigateur envoie une demande à Flask. Flask regarde quelle fonction correspond à cette adresse, et va chercher les clients dans la base SQLite avec une requête SQL. La base renvoie les lignes, Flask les met dans le template HTML, et mon navigateur reçoit une page toute prête.

2. Pourquoi faut-il **fermer** la connexion (`conn.close()`) après chaque requête ?

   > _Ma réponse : Si on laisse les connexions ouvertes, elles s'accumulent et prennent des ressources pour rien.

3. Quel est l'avantage d'écrire `row['nom']` plutôt que `row[2]` ? (Pensez à ce qui arriverait si on ajoutait une colonne au milieu de la table.)

   > _Ma réponse : D'abord c'est plus clair, en lisant row['nom'], on sait tout de suite ce qu'on affiche. Ensuite, si un jour on ajoute une colonne au milieu de la table, toutes les positions changent et row[2] n'afficherait plus le nom, alors que row['nom'] marcherait toujours.

4. Pourquoi est-il préférable de trier avec `ORDER BY` dans la requête SQL plutôt qu'en Python ?

   > _Ma réponse : La base de données est faite pour ça, elle trie plus vite. Comme ça les données arrivent déjà dans le bon ordre et on n'a pas besoin d'écrire du code en plus dans Python.

---

## 🟢 Exercice 3 — Rechercher un client

1. Quelle est la différence entre `WHERE nom = 'DUPONT'` et `WHERE nom LIKE '%DUP%'` ?

   > _Ma réponse : Le = est très strict, il faut écrire le nom exactement. Par exemple, si je tape dupont en minuscules, il ne trouve rien. Le LIKE est plus simple : il cherche tous les noms qui contiennent "DUP" quelque part, et il ne fait pas attention aux majuscules.

2. Expliquez avec vos mots ce qu'est une **injection SQL**. Qu'est-ce qu'un pirate pourrait faire de pire qu'afficher tous les clients ?

   > _Ma réponse : C'est quand quelqu'un réussit à glisser son propre bout de SQL dans la requête du site, parce que le développeur a collé directement ce que l'utilisateur tape. En testant x' OR '1'='1, j'ai vu que tous les clients s'affichaient, alors qu'aucun ne s'appelle "x".

3. Pourquoi la version avec `?` est-elle protégée contre l'injection ?

   > _Ma réponse : : Avec le ?, ce que l'utilisateur tape est toujours pris comme du texte, jamais comme du code SQL. Donc même si quelqu'un essaie une injection, la base cherche juste un nom bizarre et ne trouve rien.

4. Pour la recherche, on a utilisé `method="get"`. Quel avantage pour l'utilisateur ? (Indice : favoris, partage de lien.)

   > _Ma réponse : Avec GET, la recherche s'affiche directement dans l'URL, par exemple /recherche?q=ma. C'est pratique, on peut envoyer le lien à quelqu'un, ou revenir en arrière et retrouver la même recherche.

🧩 **Défi** — mes requêtes / ma solution :

   > 

---

## 🔵 Exercice 4 — Enregistrer un client

1. Quelles étaient les deux anomalies du formulaire d'origine, et d'où venaient-elles ?

   > _Ma réponse :_ 

2. Pourquoi la validation côté **navigateur** (`required`) ne suffit-elle pas ? Pourquoi la garder quand même ?

   > _Ma réponse :_ 

3. À quoi sert `conn.commit()` ? Que se passe-t-il sans lui ?

   > _Ma réponse :_ 

4. Pourquoi redirige-t-on vers `/consultation/` après l'enregistrement, au lieu d'afficher directement une page ? (Indice : essayez d'appuyer sur F5 après l'envoi.)

   > _Ma réponse :_ 

---

## 🔵 Exercice 5 — Modifier et supprimer

1. Que signifie CRUD ? Donnez la requête SQL correspondant à chaque lettre.

   > _Ma réponse :_ 

2. Que se passe-t-il si l'on oublie le `WHERE` dans un `UPDATE` ou un `DELETE` ? À quoi servent `BEGIN` et `ROLLBACK` ?

   > _Ma réponse :_ 

3. Pourquoi ne faut-il **jamais** supprimer des données avec une requête GET (un simple lien) ? (Indice : les moteurs de recherche et certains navigateurs « visitent » les liens à l'avance.)

   > _Ma réponse :_ 

4. Une fois un `id` supprimé, pourquoi est-il préférable qu'il ne soit jamais réattribué à un autre client ?

   > _Ma réponse :_ 

---

## 🟣 Exercice 6 — Faire évoluer la base

1. Quelle est la différence entre le **schéma** d'une base et ses **données** ? Où se trouve chacun ?

   > _Ma réponse :_ 

2. Pourquoi ne faut-il pas relancer `create_db.py` sur une application en production ?

   > _Ma réponse :_ 

3. Pourquoi est-il important de garder `schema.sql` à jour, même si on a modifié la base avec `ALTER TABLE` ?

   > _Ma réponse :_ 

4. Pour ajouter **une** information, combien de fichiers avez-vous dû modifier ? Lesquels ?

   > _Ma réponse :_ 

---

## 🟣 Exercice 7 — Relier deux tables

1. Qu'est-ce qu'une **clé étrangère** ? Dans quelle table se trouve-t-elle ici, et pourquoi pas dans l'autre ?

   > _Ma réponse :_ 

2. Pourquoi est-ce une mauvaise idée de créer des colonnes `commande1`, `commande2`… dans la table `clients` ?

   > _Ma réponse :_ 

3. À quoi sert un `JOIN` ? Et un `GROUP BY` ?

   > _Ma réponse :_ 

4. Pour la bibliothèque, quelles tables imaginez-vous ? Lesquelles contiendront des clés étrangères ?

   > _Ma réponse :_ 

---

## 🔴 Exercice 8 — Contrôle d'accès

1. Quelle est la différence entre **authentification** et **autorisation** ?

   > _Ma réponse :_ 

2. Où est stockée la session ? Comment le serveur sait-il qui vous êtes à chaque nouvelle requête ?

   > _Ma réponse :_ 

3. Pourquoi masquer un bouton dans le HTML ne suffit-il pas à protéger une action ?

   > _Ma réponse :_ 

4. Que signifient les codes `302` et `403` ? Dans quel cas votre application renvoie-t-elle chacun d'eux ?

   > _Ma réponse :_ 

5. Le mot de passe `password` est écrit en clair dans `flask_app.py`, sur un dépôt **public**. Quel est le risque ? Quelle solution avez-vous déjà rencontrée dans cet atelier pour cacher une information sensible ?

   > _Ma réponse :_ 

---

## 🔴 Exercice 9 — Créer une API

1. Quelle est la différence entre une page HTML et une réponse JSON ? À qui chacune est-elle destinée ?

   > _Ma réponse :_ 

2. Que signifient les codes `200`, `201`, `400`, `401` et `404` renvoyés par votre API ?

   > _Ma réponse :_ 

3. Pourquoi une API renvoie-t-elle une erreur JSON plutôt qu'une redirection vers la page de connexion ?

   > _Ma réponse :_ 

4. Citez une application de votre téléphone qui, selon vous, utilise une API. Quelles données échange-t-elle ?

   > _Ma réponse :_ 

---

## 📚 Projet bibliothèque

1. Pourquoi ne supprime-t-on pas un emprunt quand le livre est rendu ?

   > _Ma réponse :_ 

2. Pourquoi calculer la disponibilité d'un livre plutôt que de la stocker dans une colonne ?

   > _Ma réponse :_ 

3. Quelle a été la plus grande difficulté rencontrée pendant le projet, et comment l'avez-vous surmontée ?

   > _Ma réponse :_ 

4. Quelles fonctionnalités n'avez-vous pas eu le temps de réaliser ? Comment vous y prendriez-vous ?

   > _Ma réponse :_ 

---

## 🏁 Pour conclure

En quelques phrases, expliquez à un ami ce qui se passe entre le moment où il clique sur « Enregistrer » dans un formulaire et celui où l'information s'affiche dans une liste :

> _Ma réponse :_ 
