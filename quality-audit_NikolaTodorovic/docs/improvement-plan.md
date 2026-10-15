# Plan d'amélioration — QuickOrder V3.1

Ce plan transforme les constats de la campagne (`execution-report.md`, `bug-reports/`, `user-feedback.md`) en actions **priorisées et justifiées**. Le brief demande 6 améliorations au minimum : le plan en propose 7.

## 1. Méthode de priorisation

- **Risque traité** : score de la matrice de risques (probabilité × impact).
- **Effort** : S (< 1 jour), M (1 à 3 jours), L (> 3 jours).
- **MoSCoW** : **Must** (avant mise en production), **Should** (juste après), **Could** (backlog).

Ordre : argent et livrabilité d'abord, puis sécurité et API, puis fiabilité dans le temps, puis expérience.

## 2. Vue d'ensemble

| ID | Amélioration | Traite | Risque (score) | Effort | MoSCoW |
|---|---|---|---|---|---|
| AM-01 | Fiabiliser le paiement (une commande par paiement, validation des espèces) | BUG-001, BUG-003 · O1, O4 | R01 (20), R04 (16) | S–M | **Must** |
| AM-02 | Centraliser les règles de commande (restaurant ouvert, stock, minimum) | BUG-002, BUG-004, BUG-005 · O3, O5 | R02 (20), R03 (16), R08 (12) | M | **Must** |
| AM-03 | Rendre l'API robuste (validation, erreurs JSON, débogueur désactivé) | BUG-007 | R07 (12) | M | **Must** |
| AM-04 | Valider la redirection après connexion (`next`) | BUG-008 | R06 (12) | S | **Must** |
| AM-05 | Garantir la cohérence offre annoncée / coupon appliqué | BUG-006 · O2 | R05 (16) | S | **Should** |
| AM-06 | Automatiser la non-régression (24 cas + rejeu des 8 bugs en CI) | Tous | Tous | M | **Should** (à démarrer avec AM-01) |
| AM-07 | Améliorer le retour visuel des commandes (confirmation avec n° de commande, messages d'erreur explicites) | O1, O3, O4, O5 | R01 (20), R03 (16) | S | **Could** |

## 3. Détail

### AM-01 — Fiabiliser le paiement · Must · S–M

- **Problème** : PayPal crée deux commandes (BUG-001, Critique) ; les espèces acceptent n'importe quel montant (BUG-003).
- **Proposition** : une seule création de commande par paiement, protégée par une **clé d'idempotence** ; refuser `cash_received < total` (400 avec message) et rendre le champ obligatoire pour « Espèces ».
- **Justification** : perte financière directe (R01 = 20, R04 = 16) ; 3 / 3 personas inquiets (O1, O4).
- **Critères d'acceptation** : un paiement = une commande et un décrément de stock ; montant insuffisant → 400 ; TC-RM-03 et TC-RM-04 passent ; `reproduce_bugs.sh` affiche `NON REPRODUIT` pour BUG-001 et BUG-003.

### AM-02 — Centraliser les règles de commande · Must · M

- **Problème** : restaurant fermé, stock et minimum ne sont pas contrôlés par le serveur, ni par le web ni par l'API (BUG-002, 004, 005).
- **Proposition** : un service unique `place_order(...)` appelé par le web **et** l'API, qui vérifie dans l'ordre : produits disponibles, restaurant ouvert, quantités, stock suffisant, minimum, coupon, paiement. Décrément de stock atomique (`UPDATE … WHERE stock >= :q`) et plafond de quantité à l'ajout au panier.
- **Justification** : une cause racine pour trois anomalies ; R02 = 20, R03 = 16, R08 = 12.
- **Critères d'acceptation** : restaurant fermé → 409 ; quantité > stock ou produit à stock 0 → 409 ; sous-total < minimum → 400 avec le montant manquant ; stock jamais négatif ; TC-RM-01, TC-RM-02, TC-LIM-06 passent.

### AM-03 — Rendre l'API robuste · Must · M

- **Problème** : `subtotal = NaN` ou corps JSON de mauvais type → HTTP 500 avec traceback et débogueur Werkzeug exposés (BUG-007).
- **Proposition** : validation de schéma (types, valeurs finies, bornes), gestionnaires d'erreurs renvoyant du JSON 400 / 422, **mode debug désactivé** hors développement.
- **Critères d'acceptation** : aucune entrée ne produit de 500 ; TC-ERR-05 passe.

### AM-04 — Valider la redirection après connexion · Must · S

- **Problème** : `?next=https://example.org` redirige hors du site (BUG-008).
- **Proposition** : n'accepter que des chemins relatifs commençant par `/` (et pas `//`), sinon rediriger vers l'accueil.
- **Critères d'acceptation** : TC-ERR-06 passe ; un test couvre `//evil.com` et `https://…`.

### AM-05 — Cohérence offre / coupon · Should · S

- **Problème** : ATLAS15 annoncé à 15 %, stocké à 10 % (BUG-006).
- **Proposition** : une seule source de vérité : le texte de l'offre est généré à partir de `discount_percent`.
- **Critères d'acceptation** : TC-RM-05 passe (5,37 € sur 35,80 €).

### AM-06 — Automatiser la non-régression · Should · M

- **Problème** : aucun test ne détecte ces régressions aujourd'hui.
- **Proposition** : intégrer `docs/automation/` en intégration continue : exécution des 24 cas et de `reproduce_bugs.sh` à chaque Pull Request, base initialisée par `seed.py`.
- **Critères d'acceptation** : pipeline rouge si l'un des 8 bugs réapparaît.

### AM-07 — Retour visuel des commandes · Could · S

- **Problème** : l'utilisateur ne peut pas distinguer une commande valide d'un doublon, ni comprendre un refus (O1, O3, O4, O5).
- **Proposition** : écran de confirmation avec numéro de commande ; messages de refus explicites (« Restaurant fermé », « Minimum de 20 € non atteint », « Montant insuffisant »).
- **Critères d'acceptation** : chaque refus affiche un message précis ; validé en test avec 2 utilisateurs réels.

## 4. Feuille de route

| Sprint | Contenu | Sortie attendue |
|---|---|---|
| 1 | AM-01, AM-02 | Bugs P1 corrigés ; TC-RM-01, 02, 03, 04 et TC-LIM-06 passent |
| 2 | AM-03, AM-04, AM-05 | Bugs P2 corrigés ; 24 / 24 Pass |
| 3 | AM-06, AM-07 | Non-régression automatique ; retour visuel amélioré |

## 5. Revalidation

À chaque correction : rejouer le cas lié, puis les 24 cas, puis `reproduce_bugs.sh` (attendu : 8 × `NON REPRODUIT`). Mettre à jour `execution-report.md` et `risk-matrix.md`.
