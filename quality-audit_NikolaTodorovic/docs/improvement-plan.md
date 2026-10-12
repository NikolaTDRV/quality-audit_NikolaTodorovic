# Plan d'amélioration — QuickOrder V3.1

Ce plan transforme les constats de la campagne (`execution-report.md`, `bug-reports/`, `user-feedback.md`) en actions **priorisées et justifiées**. Le brief demande 6 améliorations au minimum : le plan en propose 13.

## 1. Méthode de priorisation

Chaque amélioration est classée selon :

- **Risque traité** : score de la matrice de risques (probabilité × impact) des risques qu'elle réduit ;
- **Effort** : S (< 1 jour), M (1 à 3 jours), L (> 3 jours) ;
- **MoSCoW** : **Must** (obligatoire avant mise en production), **Should** (important, juste après), **Could** (confort, backlog).

Ordre de réalisation : d'abord ce qui protège l'argent et la livrabilité, puis la sécurité, puis l'expérience, puis la dette technique.

## 2. Vue d'ensemble

| ID | Amélioration | Traite | Risque (score) | Effort | MoSCoW |
|---|---|---|---|---|---|
| AM-01 | Fiabiliser le paiement (idempotence, fin du doublon PayPal, validation des espèces) | BUG-001, 003 | R01 (20), R04 (16) | S–M | **Must** |
| AM-02 | Centraliser les règles de commande (restaurant ouvert, stock, minimum, quantités) | BUG-002, 004, 005, 019, 029 | R02 (20), R03 (16), R08 (12), R09 (12) | M–L | **Must** |
| AM-03 | Rendre l'API robuste et son contrat fiable (validation, erreurs JSON, OpenAPI) | BUG-009, 010, 011, 012 | R11 (12) | M | **Must** |
| AM-04 | Durcir la sécurité (debug, secret, CSRF, redirection, déconnexion, tentatives) | BUG-015, 023 | R06 (15) | M | **Must** |
| AM-05 | Réparer l'installation Docker et sécuriser le démarrage | BUG-025 | R13 (9) | S | **Must** |
| AM-06 | Garantir la cohérence des promotions et des coupons | BUG-007, 008, 009 | R05 (16) | S–M | **Should** |
| AM-07 | Modéliser le cycle de vie d'une commande (états, annulation complète, libellés) | BUG-016, 017, 027 | R12 (12), R16 (9) | M | **Should** |
| AM-08 | Améliorer le panier et le checkout (retour visuel, retrait, conservation des saisies, libellés) | BUG-020, 022, 028 | R15 (8), R17 (6) | S–M | **Should** |
| AM-09 | Rendre la découverte fiable (filtre, recherche, restaurants fermés) | BUG-006, 013 | R14 (8) | S | **Should** |
| AM-10 | Compléter avis, favoris et gestion des adresses | BUG-014, 018, 022 | R10 (12), R19 (6) | M | **Should** |
| AM-11 | Automatiser la qualité (tests de non-régression, tests d'API, CI) | Tous (dont BUG-026) | Tous | M | **Should** (commencer avec AM-01) |
| AM-12 | Fiabiliser les données saisies et le temps (validation, fuseaux) | BUG-021, 024 | R17 (6), R18 (6) | S–M | **Could** |
| AM-13 | Améliorer l'observabilité et l'autonomie hors ligne (logs, Swagger local) | — | R13 (9) | S | **Could** |

## 3. Détail des améliorations

### AM-01 — Fiabiliser le paiement · **Must** · effort S–M

- **Problème** : un paiement PayPal crée deux commandes (BUG-001, Critique) ; les espèces acceptent n'importe quel montant (BUG-003) ; les trois personas évoquent la peur d'un double paiement (O2).
- **Proposition** : supprimer la seconde création de commande ; générer une **clé d'idempotence** par tentative de paiement ; refuser `cash_received < total` côté serveur (400 avec message) et rendre le champ obligatoire pour « Espèces » ; afficher un récapitulatif avec le numéro de commande.
- **Justification** : risque R01 (20) et R04 (16), perte financière directe et impact sur la confiance.
- **Critères d'acceptation** : un paiement = une commande et un décrément de stock ; `cash_received` < total → 400 ; un test automatisé échoue si le bug réapparaît.

### AM-02 — Centraliser les règles de commande · **Must** · effort M–L

- **Problème** : restaurant fermé, stock, minimum et quantités sont contrôlés de façon partielle, différemment entre web et API (BUG-002, 004, 005, 019).
- **Proposition** : un service unique `place_order(...)` qui vérifie dans l'ordre : produits existants et disponibles, restaurant ouvert, un seul restaurant, quantités (1 à N), stock suffisant, minimum de commande, coupon, paiement ; il est appelé par le web **et** l'API. Le stock est décrémenté par une mise à jour atomique (`UPDATE … WHERE stock >= :q`). Les contrôles d'ajout au panier et de mise à jour du panier appliquent les mêmes règles.
- **Justification** : cause racine commune de 7 anomalies ; risques R02 (20), R03 (16), R09 (12).
- **Critères d'acceptation** : restaurant fermé → 409 ; quantité > stock → 409 ; sous-total < minimum → 400/409 avec le montant manquant ; stock jamais négatif, y compris en commandes simultanées.

### AM-03 — Rendre l'API robuste et son contrat fiable · **Must** · effort M

- **Problème** : erreurs 500 sur entrées mal formées (BUG-010), 404 en HTML (BUG-011), coupon expiré accepté et coupon inconnu ignoré (BUG-009), validation de coupon fondée sur le sous-total du client (BUG-012).
- **Proposition** : validation de schéma systématique des corps de requête (types, bornes, nombres finis) ; gestionnaires d'erreurs JSON (400, 404, 405, 500) ; statuts cohérents (par exemple 422 pour un coupon invalide) ; calcul du coupon à partir du panier serveur ; mise à jour d'`openapi.yaml` ; tests de contrat sur la spécification.
- **Justification** : R11 (12) ; une API publique qui renvoie des 500 est perçue comme non fiable.
- **Critères d'acceptation** : aucune entrée invalide ne produit de 500 ; toutes les erreurs ont un corps `{"error": …}` ; l'API et le web renvoient la même remise pour le même panier.

### AM-04 — Durcir la sécurité · **Must** · effort M

- **Problème** : redirection ouverte (BUG-015), débogueur actif et écoute sur toutes les interfaces par défaut, secrets par défaut, pas de CSRF, déconnexion en GET, aucune limitation des tentatives (BUG-023).
- **Proposition** : `FLASK_DEBUG=0` et hôte `127.0.0.1` par défaut ; `SECRET_KEY` et clé API obligatoires hors développement ; Flask-WTF pour les jetons CSRF ; déconnexion en POST ; validation de `next` (chemins relatifs uniquement) ; limitation de débit sur la connexion ; en-têtes de sécurité et cookies `HttpOnly`, `SameSite`, `Secure`.
- **Justification** : R06 (15), impact maximal ; correctifs peu coûteux.
- **Critères d'acceptation** : `/login?next=https://…` redirige vers l'accueil ; chaque formulaire POST contient un jeton valide ; un lancement sans variable `SECRET_KEY` hors développement échoue explicitement.

### AM-05 — Réparer l'installation Docker · **Must** · effort S

- **Problème** : `docker-entrypoint.sh` est versionné sans bit exécutable ; `docker compose up` échoue sous Linux/macOS (BUG-025). La voie « recommandée pour débuter » est donc inutilisable pour une partie des étudiants.
- **Proposition** : `git update-index --chmod=+x docker-entrypoint.sh` ou `command: ["sh", "docker-entrypoint.sh"]` ; ajouter un `healthcheck` sur `/api/health` ; documenter l'attente du démarrage.
- **Justification** : R13 (9), mais bloque tous les tests ; effort minimal.
- **Critères d'acceptation** : `docker compose up --build` fonctionne sous Linux, macOS et Windows ; l'application répond sur `/api/health`.

### AM-06 — Cohérence des promotions et des coupons · **Should** · effort S–M

- **Problème** : ATLAS15 annoncé à 15 % et appliqué à 10 % (BUG-007) ; TOKYO30 appliqué partout et supérieur aux frais de livraison (BUG-008) ; règle d'éligibilité de WELCOME10 non définie.
- **Proposition** : une **source unique** pour le texte promo et la remise (le texte est généré à partir du coupon) ; `restaurant_id` et type de remise (« livraison offerte » plafonnée aux frais réels) dans le modèle de coupon ; usage unique par client pour les coupons de bienvenue ; affichage de l'économie réalisée au récapitulatif.
- **Justification** : R05 (16), risque juridique (publicité) et financier.
- **Critères d'acceptation** : pour chaque coupon, le pourcentage affiché est celui appliqué ; TOKYO30 refusé hors Tokyo Bowl ; la remise « livraison offerte » ne dépasse jamais les frais.

### AM-07 — Cycle de vie d'une commande · **Should** · effort M

- **Problème** : l'annulation ne rend ni le stock ni le paiement (BUG-016) ; l'administrateur peut revenir de « delivered » à « confirmed » (BUG-017) ; les statuts sont affichés en codes techniques (O3).
- **Proposition** : machine à états (`confirmed → preparing → out_for_delivery → delivered`, annulation avant livraison) ; annulation qui restitue le stock et passe le paiement à « refunded » ; historique des changements ; libellés français et frise de progression.
- **Justification** : R12 (12), R16 (9) ; cohérence des données et clarté pour le client.
- **Critères d'acceptation** : transitions interdites → refus ; stock restitué ; paiement cohérent avec le statut.

### AM-08 — Panier et checkout · **Should** · effort S–M

- **Problème** : pas de compteur de panier (O6), pas de bouton « Retirer » (O7), « Appliquer » réinitialise le formulaire (BUG-020), libellés de paiement déroutants (O4).
- **Proposition** : compteur sur « Panier » ; bouton « Retirer » et boutons « − / + » ; conservation des saisies après « Appliquer » ; libellés « Carte bancaire », « PayPal », « Espèces à la livraison » et bandeau « paiement simulé » ; correction du HTML (pas de formulaire imbriqué).
- **Justification** : 3 retours sur 3 sur le retour visuel ; réduit les erreurs de commande.
- **Critères d'acceptation** : un test utilisateur sans aide réussit S1 sans hésitation sur l'ajout ; après « Appliquer », adresse, note et paiement conservés.

### AM-09 — Découverte fiable · **Should** · effort S

- **Problème** : filtre de livraison inversé (BUG-006), recherche limitée au nom (BUG-013), restaurants fermés présentés comme les autres.
- **Proposition** : corriger l'opérateur, rechercher dans le nom, la cuisine et la description (avec échappement des jokers), afficher le nombre de résultats et les filtres actifs, option « Ouvert maintenant », cartes de restaurants fermés grisées avec bouton d'ajout désactivé.
- **Justification** : 3 retours sur 3 (O1) ; correctif de quelques lignes.
- **Critères d'acceptation** : `max_delivery=2.00` ne renvoie que des frais ≤ 2,00 € ; « japonais » renvoie Tokyo Bowl et Night Sushi.

### AM-10 — Avis, favoris et adresses · **Should** · effort M

- **Problème** : avis publiables sans commande, jamais affichés (BUG-018) ; favoris et suppression d'adresse inaccessibles (BUG-022) ; adresse vide créée à l'inscription (BUG-014).
- **Proposition** : avis réservés aux commandes livrées (un par commande), liste et note moyenne sur la fiche ; bouton Favori sur carte et fiche ; adresse saisie à l'inscription ou au premier checkout (aucune adresse vide ni adresse de repli) ; modification et suppression d'adresse.
- **Justification** : R10 (12) et R19 (6) ; fonctionnalités annoncées au README mais inutilisables.
- **Critères d'acceptation** : une adresse incomplète ne peut pas être sélectionnée pour livrer ; un avis apparaît sur la fiche et modifie la moyenne.

### AM-11 — Automatiser la qualité · **Should** · effort M

- **Problème** : seuls 6 tests de fumée existent ; aucune anomalie n'est protégée contre la régression.
- **Proposition** : pour chaque bug corrigé, un test `pytest` qui échoue avant le correctif ; tests d'API paramétrés (limites de quantité, coupons, entrées invalides) ; vérification du contrat OpenAPI ; **intégration continue** (GitHub Actions) exécutant les tests à chaque Pull Request ; mesure de la couverture.
- **Justification** : sans cela, les 29 anomalies reviendront ; prérequis d'un Go durable.
- **Critères d'acceptation** : pipeline vert obligatoire pour fusionner ; chaque `BUG-xxx` corrigé référencé par au moins un test.

### AM-12 — Données saisies et gestion du temps · **Could** · effort S–M

- **Problème** : champs peu validés (BUG-024) ; heures affichées en UTC (BUG-021).
- **Proposition** : validation de schéma (longueurs, formats d'email, de téléphone et de code postal, politique de mot de passe) ; horodatages avec fuseau, conversion à l'affichage, ISO 8601 avec `Z` dans l'API.
- **Justification** : R17 (6) et R18 (6) ; améliore la qualité des données et prépare un changement de SGBD.
- **Critères d'acceptation** : nom de 121 caractères refusé ; heure affichée = heure locale du client.

### AM-13 — Observabilité et autonomie · **Could** · effort S

- **Problème** : aucune trace des paiements ni des erreurs ; Swagger UI dépend d'un CDN externe (page vide hors ligne).
- **Proposition** : journalisation structurée des commandes, paiements et erreurs ; embarquer les fichiers de Swagger UI dans l'application.
- **Justification** : facilite le diagnostic en production et le travail en salle sans accès réseau.
- **Critères d'acceptation** : `/docs/` fonctionne sans Internet ; chaque commande produit une ligne de journal exploitable.

## 4. Feuille de route proposée

| Étape | Contenu | Livrable de sortie |
|---|---|---|
| **Sprint 1 — Débloquer et protéger l'argent** | AM-05, AM-01, AM-02 (règles restaurant ouvert et stock en premier), AM-11 (tests des correctifs) | Les 5 anomalies P1 fermées ; premier Go conditionnel |
| **Sprint 2 — Sécurité et API** | AM-04, AM-03, AM-06 | Anomalies P2 de sécurité et d'API fermées |
| **Sprint 3 — Expérience** | AM-07, AM-08, AM-09, AM-10 | Retours utilisateurs O1 et O3 à O8 traités (O2, O9, O10 le sont dès le sprint 1) |
| **Sprint 4 — Qualité durable** | AM-12, AM-13, couverture et CI complètes | Backlog P3 fermé |

## 5. Revalidation des corrections

Les corrections sont proposées **dans une branche séparée** (`fix/<bug-id>` ou `improve/<AM-id>`), jamais dans la branche de campagne.

1. Chaque correctif référence sa fiche (`BUG-xxx`) et son amélioration (`AM-xx`).
2. Rejeu des cas liés (colonne « Bug lié » de `test-cases.xlsx`), puis des cas P1 du même module.
3. Mise à jour du statut de la fiche : **Corrigé → Fermé** ou **Rouvert** avec la preuve.
4. Rejeu complet des cas P1 avant toute décision Go ; mise à jour de `execution-report.md` (chiffres, décision) et de `risk-matrix.md`.
5. Seconde série de tests utilisateurs sur S1, S2 et S3 après les sprints 1 et 3.

## 6. Indicateurs de succès

| Indicateur | Aujourd'hui | Cible avant mise en production |
|---|---|---|
| Taux de réussite des cas P1 | 48,5 % | ≥ 95 % |
| Taux de réussite global | 52,7 % | ≥ 90 % |
| Anomalies Critiques / Majeures ouvertes | 1 / 14 | 0 / 0 sur J1 à J3 |
| Erreurs 500 sur entrées invalides (API) | 4 familles | 0 |
| Scénarios S1 à S3 réussis intégralement, sans aide ni erreur (3 personas × 3 scénarios, à mesurer ensuite avec de vrais utilisateurs) | 3 / 9 (S2 uniquement) | ≥ 8 / 9 |
| Régressions protégées par un test automatisé | 0 | 100 % des anomalies corrigées |
