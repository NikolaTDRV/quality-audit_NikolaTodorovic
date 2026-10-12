# Stratégie de test — QuickOrder V3.1

| | |
|---|---|
| **Produit** | QuickOrder V3.1 (application web Flask + API REST, SQLite) |
| **Équipe** | Quality audit |
| **Date** | 12/10/2026 |
| **Objectif de la mission** | Évaluer la qualité avant mise en production et recommander **Go / No-Go** |

## 1. Contexte et objectifs

QuickOrder est une plateforme de commande de repas déjà développée. La mission n'est pas de la reconstruire mais de **mesurer sa qualité** : trouver les anomalies, les prouver, mesurer le risque et décider si la mise en production est acceptable.

Objectifs de test, par ordre d'importance :

1. Protéger l'**argent** : paiement, remises, frais, totaux.
2. Garantir que ce qui est commandé **peut être livré** : restaurant ouvert, stock, adresse, minimum.
3. Protéger les **données et les comptes** : accès, session, configuration.
4. Vérifier la **fiabilité du contrat d'API** (statuts, erreurs, cohérence avec le web).
5. Évaluer la **facilité d'usage** des parcours principaux avec de vrais utilisateurs.

## 2. Périmètre

### 2.1 Dans le périmètre

| Domaine | Contenu testé |
|---|---|
| Catalogue | Liste des restaurants, recherche, filtres (catégorie, livraison max, végétarien), tris, fiche restaurant et menu |
| Panier | Ajout, modification, suppression, règle mono-restaurant, totaux |
| Checkout et paiement | Adresse, note, coupons, paiement carte / PayPal / espèces (simulé), création de commande |
| Coupons et promotions | WELCOME10, SAVE20, LUNCH5, TOKYO30, ATLAS15, EXPIRED10 (minimum, plafond, expiration, cohérence avec l'annonce) |
| Commandes | Liste, détail, filtre par statut, annulation, « Commander à nouveau » |
| Compte | Inscription, connexion, déconnexion, profil, adresses, favoris |
| Avis | Publication, affichage, note |
| Administration | Tableau de bord, changement de statut des commandes, contrôle d'accès |
| API REST | Tous les endpoints de `openapi.yaml` (santé, restaurants, produits, coupons, commandes, favoris) |
| Documentation et installation | Procédure venv et Docker, Swagger, collection Postman, tests automatisés fournis |
| Sécurité de base | Contrôle d'accès, redirections, validation d'entrées, configuration par défaut |

### 2.2 Hors périmètre

| Exclusion | Raison | Traitement |
|---|---|---|
| Performance et charge | Outillage non prévu dans la campagne ; SQLite local | Seul un cas de concurrence sur le stock est exécuté (TC-NFR-01, 4 requêtes parallèles) |
| Test d'intrusion approfondi | Hors compétences et durée de la mission | Seuls les contrôles de base sont réalisés ; un audit sécurité dédié est recommandé |
| RGPD / conformité juridique | Nécessite un audit spécifique | Signalé comme risque R20 |
| Vrai paiement bancaire | Le paiement est simulé | Seule la logique applicative est testée |
| Compatibilité multi-navigateurs et appareils réels | Un seul moteur (Chromium) et un viewport mobile émulé à 375 px | Reporté ; à planifier avant production |
| Accessibilité complète (RGAA / WCAG) | Hors durée | Observations opportunistes uniquement |
| Code source (revue de code) | La campagne est de type boîte noire ; le code n'est consulté qu'en phase d'analyse de cause | Aucune modification du code pendant la campagne |

## 3. Hypothèses et contraintes

- **Aucune modification du code** de QuickOrder pendant la campagne initiale ; les corrections seront proposées dans une branche séparée.
- Les résultats sont obtenus sur une **base fraîchement initialisée** (`python seed.py`) ; la base est réinitialisée entre deux séries de tests destructifs.
- L'API agit au nom du compte **alice@example.com** quelle que soit la clé fournie ; c'est un choix pédagogique et non une anomalie.
- Les règles métier non écrites sont déduites de l'interface (minimum, restaurant fermé, promotions affichées) ; quand elles sont ambiguës, la question est tracée (TC-RM-25) plutôt que supposée.

## 4. Parcours critiques

| ID | Parcours | Pourquoi critique | Cas principaux |
|---|---|---|---|
| J1 | Découvrir → menu → panier → checkout → confirmation (carte) | Cœur du chiffre d'affaires | TC-NOM-01 à 07, TC-LIM-08 à 10, TC-RM-01 à 05 |
| J2 | Paiement PayPal et espèces | Risque financier direct | TC-RM-06 à 10 |
| J3 | Coupons et promotions | Impact sur le prix et sur la promesse faite au client | TC-LIM-01 à 03, TC-RM-11 à 14, TC-ERR-13, TC-ERR-14 |
| J4 | Compte : inscription, connexion, profil, adresses | Porte d'entrée et données personnelles | TC-NOM-02, 03, 13, TC-ERR-01, 02, 16, TC-RM-22 |
| J5 | Suivi : liste, détail, annulation, recommande | Confiance et support | TC-NOM-08, 14, TC-RM-15, 16, 24 |
| J6 | Administration des statuts | Intégrité des données | TC-ERR-11, TC-RM-17 |
| J7 | API : restaurants → commande → annulation | Canal utilisé par des intégrations | TC-NOM-09, 10, TC-ERR-03 à 10, 14, 19, 20, 22 |
| J8 | Installation et démarrage (venv, Docker) | Sans cela, rien n'est testable | TC-ENV-01, TC-EXT-01, TC-EXT-20 |

## 5. Approche et types de tests

| Type | Objectif | Où | Outils |
|---|---|---|---|
| Fonctionnel nominal | Vérifier que les parcours marchent « au soleil » | UI, API | Navigateur, Swagger |
| Valeurs limites et partitions | Trouver les défauts aux bornes (minimum, plafonds, stock, longueurs) | UI, API | Swagger, requêtes scriptées, édition du DOM |
| Négatif / gestion d'erreurs | Entrées invalides, accès interdits, états impossibles | UI, API | Édition du DOM, requêtes scriptées |
| Règles métier | Vérifier les règles écrites ou affichées (restaurant fermé, minimum, coupons, annulation) | UI, API | Navigateur, Swagger |
| Contrat d'API | Statuts, formats d'erreur, cohérence avec `openapi.yaml` et avec le web | API | Swagger UI, collection Postman fournie, requêtes scriptées |
| Sécurité de base | Contrôle d'accès, redirection ouverte, CSRF, configuration | UI, API | Édition du DOM, requêtes scriptées |
| Exploratoire (sessions chronométrées) | Découvrir ce que les cas écrits n'anticipent pas | UI | Chartes ci-dessous |
| Utilisabilité | Mesurer les difficultés réelles de personnes non expertes | UI | Tests utilisateurs (voir `user-feedback.md`) |
| Non-régression | Rejouer les cas après correction | UI, API | Même plan, cas P1 d'abord |

### 5.1 Techniques de conception

- **Partitions d'équivalence et valeurs limites** : minimum de coupon (19,99 / 20,00), quantité (0, 1, 20, 21), stock (stock − 1, stock, stock + 1), mot de passe (7 / 8), longueur de nom (120 / 121).
- **Table de décision** pour les coupons : actif, expiré, minimum atteint, plafond atteint, restaurant concerné.
- **Transitions d'état** pour une commande : `confirmed → preparing → out_for_delivery → delivered`, annulation possible avant livraison.
- **Devinette d'erreurs** : valeurs spéciales (`NaN`, `%`, très grandes valeurs), types inattendus en JSON, édition du DOM (noms de champs, `max`, `value`).
- **Comparaison des canaux** : la même règle est testée via le web **et** via l'API ; une différence est une anomalie.

### 5.2 Chartes exploratoires (30 min chacune)

1. Explorer le checkout en essayant de payer moins que le prix.
2. Explorer le panier en cherchant à le rendre incohérent (autre restaurant, produit retiré, quantités extrêmes).
3. Explorer l'API en envoyant des entrées malformées (types, valeurs spéciales, corps vides).

## 6. Environnements et données

| Élément | Valeur |
|---|---|
| Application | http://127.0.0.1:5000 (lancement `python run.py`) ; Swagger http://127.0.0.1:5000/docs/ |
| Installation | Python 3.13 + venv, `pip install -r requirements.txt`, `python seed.py`, `python run.py`. Docker : démon indisponible dans l'environnement de test, le script d'entrée a été exécuté directement (TC-ENV-01) |
| Navigateur | Chromium piloté par Playwright (Python) : captures, vidéo, édition du DOM comme dans les DevTools, console et réseau |
| API | Swagger UI (chargé dans le navigateur), requêtes HTTP scriptées (`requests`, équivalent curl), collection `docs/quickorder-api.postman_collection.json` rejouée |
| Comptes | Alice et Bob (clients), Admin ; clé API `quickorder-demo-key` |
| Jeu de données | Détaillé dans l'onglet « Légende » de `test-cases.xlsx` (6 restaurants dont 1 fermé, produits à stock 0 et 2, 6 coupons dont 1 expiré, 1 commande livrée) |
| Réinitialisation | `python seed.py` (⚠ réinitialise la base) entre les séries destructives |

## 7. Organisation et planning

| Activité | Durée | Sortie |
|---|---|---|
| Prise en main du produit et cartographie des parcours | 1 h | Liste des parcours, jeu de données |
| Analyse des risques et priorisation | 1 h | `risk-matrix.md` |
| Rédaction des cas de test | 2 h | `test-cases.xlsx` |
| Exécution de la campagne (P1 puis P2 puis P3) | 3 h | Résultats, preuves |
| Rédaction des bug reports | 2 h | `bug-reports/` |
| Tests utilisateurs | 1 h 30 | `user-feedback.md` |
| Analyse, recommandation, plan d'amélioration | 1 h 30 | `execution-report.md`, `improvement-plan.md` |

Rôles : **responsable de campagne** (planning, synthèse), **testeur UI**, **testeur API**, **rédacteur des anomalies** ; chacun relit le travail d'un autre.

## 8. Priorisation « risque × impact »

La priorisation suit la matrice `risk-matrix.md` (score = probabilité × impact). Chaque cas de test porte une priorité :

| Priorité du cas | Signification | Règle |
|---|---|---|
| **P1** | Parcours critique ou règle financière | Rattaché à un risque de score ≥ 12 ; exécuté en premier |
| **P2** | Important | Risque de score 6 à 11 ; exécuté ensuite |
| **P3** | Confort, cas rare | Risque de score ≤ 5 ou exploratoire |

Ordre d'exécution : J1/J2/J3 (argent et livraison) → J7 (API) → J4/J6 (accès et sécurité) → J5 → J8 → exploration.

## 9. Gestion des anomalies

**Sévérité** (impact technique et métier)

| Niveau | Définition |
|---|---|
| Critique | Perte financière directe, perte de données, parcours principal inutilisable |
| Majeure | Règle métier violée, faille de sécurité, parcours dégradé sans contournement évident |
| Mineure | Gêne, incohérence d'affichage, contournement simple |

**Priorité de correction**

| Niveau | Définition |
|---|---|
| P1 | À corriger avant toute mise en production |
| P2 | À corriger avant la mise en production, ou immédiatement après si un risque est accepté |
| P3 | Backlog |

Cycle de vie : Ouvert → Corrigé → À revalider → Fermé (ou Rouvert). Chaque anomalie est reproductible, reliée à un cas de test et accompagnée d'une preuve (requête et réponse, capture, vidéo).

## 10. Critères d'entrée, de sortie et de décision Go / No-Go

**Entrée** : application démarrée, base seedée, comptes de démonstration opérationnels, `STUDENT_BRIEF.md` lu.

**Sortie de campagne** : tous les cas P1 exécutés ; tous les cas P2 exécutés ou justifiés ; cas P3 exécutés dans la limite du temps ; chaque échec rattaché à une fiche de bug.

**Décision Go** (toutes les conditions) :

1. Aucune anomalie **Critique** ouverte.
2. Aucune anomalie **Majeure** ouverte sur les parcours J1 à J3.
3. Taux de réussite ≥ 95 % sur les cas P1 et ≥ 90 % global.
4. Aucun cas P1 « Blocked ».
5. Risques résiduels connus, acceptés et tracés.

Sinon : **No-Go**, avec liste des conditions de levée.

## 11. Métriques suivies

Nombre de cas prévus / exécutés, Pass / Fail / Blocked / Skipped, taux d'exécution, taux de réussite (global, par catégorie, P1), anomalies par sévérité et priorité, densité d'anomalies par module, retours utilisateurs par fréquence.

## 12. Livrables et traçabilité

| Livrable | Fichier |
|---|---|
| Stratégie | `docs/test-strategy.md` |
| Risques | `docs/risk-matrix.md` |
| Cas de test et résultats | `docs/test-cases.xlsx` |
| Anomalies | `docs/bug-reports/` |
| Rapport de campagne et Go / No-Go | `docs/execution-report.md` |
| Retours utilisateurs | `docs/user-feedback.md` |
| Plan d'amélioration et revalidation | `docs/improvement-plan.md` |
| Preuves (captures, vidéo, traces requête/réponse) | `docs/evidence/` |
| Scripts de campagne exécutables (Playwright + requests) | `docs/automation/` |

Traçabilité : risque (R-xx) → cas de test (TC-…) → anomalie (BUG-…) → amélioration (AM-…).
