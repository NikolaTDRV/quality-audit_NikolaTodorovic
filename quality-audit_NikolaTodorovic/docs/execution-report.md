# Rapport d'exécution de la campagne — QuickOrder V3.1

| | |
|---|---|
| Équipe | Quality audit |
| Date de campagne | 12/10/2026 |
| Version testée | QuickOrder V3.1 (base seedée) |
| Environnement | Chromium (Playwright), requêtes HTTP scriptées, Swagger UI, Python 3.13, SQLite, http://127.0.0.1:5000 |

## 1. Recommandation : **NO-GO**

QuickOrder **ne peut pas être mis en production en l'état**. La campagne a exécuté 94 des 99 cas prévus ; 46 échouent. Les cinq raisons principales :

1. **Argent** : un paiement PayPal crée deux commandes identiques (BUG-001, Critique) ; un paiement en espèces est accepté pour 1 € sur 14,89 € (BUG-003).
2. **Livrabilité** : on peut commander chez un restaurant fermé (BUG-002), des produits hors stock ou en quantité supérieure au stock, avec un stock qui devient négatif (BUG-004), et sous le minimum de commande (BUG-005).
3. **Promesse commerciale** : l'offre ATLAS15 est annoncée à 15 % et appliquée à 10 % (BUG-007) ; un coupon expiré est accepté par l'API (BUG-009).
4. **Sécurité** : redirection ouverte après connexion (BUG-015), débogueur actif par défaut, secret par défaut, aucune protection CSRF (BUG-023).
5. **Fiabilité de l'API** : des entrées mal formées provoquent des erreurs 500 (BUG-010).

Les parcours « sains » (inscription, connexion, calcul d'un panier, contrôles d'accès) fonctionnent, ce qui rend les corrections réalistes : la plupart des défauts sont des **contrôles manquants côté serveur**, faciles à localiser (voir §5).

## 2. Résultats chiffrés

### 2.1 Vue d'ensemble

| Indicateur | Valeur |
|---|---|
| Cas de test prévus | **99** |
| **Pass** | **48** |
| **Fail** | **46** |
| **Blocked** | **4** |
| **Skipped** | **1** |
| Cas exécutés (Pass + Fail) | 94 (94.9 % des prévus) |
| Taux de réussite (Pass / exécutés) | 51.1 % |
| Cas P1 | 33 dont 16 Pass, 17 Fail, 0 Blocked, 0 Skipped |
| Taux de réussite P1 | 48.5 % |

### 2.2 Par catégorie

| Catégorie | Total | Pass | Fail | Blocked | Skipped | Taux de réussite |
|---|---|---|---|---|---|---|
| Nominal | 16 | 14 | 0 | 2 | 0 | 100.0 % |
| Limite | 13 | 6 | 7 | 0 | 0 | 46.2 % |
| Erreur | 23 | 13 | 9 | 1 | 0 | 59.1 % |
| Règle métier | 25 | 6 | 18 | 0 | 1 | 25.0 % |
| Complémentaire | 22 | 9 | 12 | 1 | 0 | 42.9 % |
| **Total** | 99 | 48 | 46 | 4 | 1 | 51.1 % |

Exigence du brief : 6 cas nominaux, 6 limites, 6 erreurs et 6 règles métier au minimum. La campagne en compte respectivement 16, 13, 23 et 25, plus 22 cas complémentaires (environnement et robustesse).

### 2.3 Par priorité et par canal

| Priorité | Total | Pass | Fail | Blocked | Skipped | Taux de réussite |
|---|---|---|---|---|---|---|
| P1 | 33 | 16 | 17 | 0 | 0 | 48.5 % |
| P2 | 40 | 23 | 17 | 0 | 0 | 57.5 % |
| P3 | 26 | 9 | 12 | 4 | 1 | 42.9 % |

| Canal | Total | Pass | Fail | Blocked | Skipped | Taux de réussite |
|---|---|---|---|---|---|---|
| UI | 67 | 34 | 29 | 3 | 1 | 54.0 % |
| API | 28 | 14 | 13 | 1 | 0 | 51.9 % |
| Env | 4 | 0 | 4 | 0 | 0 | 0.0 % |

### 2.4 Par module (cas en échec)

| Module | Total | Pass | Fail | Blocked | Skipped |
|---|---|---|---|---|---|
| Commande | 18 | 10 | 8 | 0 | 0 |
| Complémentaire | 18 | 9 | 8 | 1 | 0 |
| Coupons | 13 | 6 | 6 | 0 | 1 |
| API | 11 | 6 | 4 | 1 | 0 |
| Paiement | 5 | 1 | 4 | 0 | 0 |
| Environnement | 3 | 0 | 3 | 0 | 0 |
| Authentification | 7 | 5 | 2 | 0 | 0 |
| Avis | 2 | 0 | 2 | 0 | 0 |
| Catalogue | 6 | 4 | 2 | 0 | 0 |
| Panier | 6 | 4 | 2 | 0 | 0 |
| Stock | 3 | 1 | 2 | 0 | 0 |
| Administration | 2 | 1 | 1 | 0 | 0 |
| Robustesse | 1 | 0 | 1 | 0 | 0 |
| Sécurité | 1 | 0 | 1 | 0 | 0 |
| Favoris | 1 | 0 | 0 | 1 | 0 |
| Profil | 2 | 1 | 0 | 1 | 0 |

## 3. Anomalies

| Sévérité | P1 | P2 | P3 | Total |
|---|---|---|---|---|
| Critique | 1 | 0 | 0 | 1 |
| Majeure | 4 | 11 | 0 | 15 |
| Mineure | 0 | 0 | 13 | 13 |
| **Total** | 5 | 11 | 13 | 29 |

29 fiches reproductibles dans `docs/bug-reports/` (le brief en exige 8 au minimum). Les anomalies de priorité P1 :

| ID | Titre | Sévérité | Canal |
|---|---|---|---|
| [BUG-001](bug-reports/BUG-001.md) | Le paiement PayPal crée deux commandes identiques (web et API) | Critique | UI + API |
| [BUG-002](bug-reports/BUG-002.md) | Un restaurant fermé peut recevoir des commandes (web et API) | Majeure | UI + API |
| [BUG-003](bug-reports/BUG-003.md) | Le paiement en espèces accepte un montant inférieur au total (monnaie négative) | Majeure | UI + API |
| [BUG-004](bug-reports/BUG-004.md) | Contrôles de stock et de quantité défaillants (stock négatif, hors-stock commandable) | Majeure | UI + API |
| [BUG-025](bug-reports/BUG-025.md) | `docker compose up` échoue sous Linux/macOS : docker-entrypoint.sh n'est pas exécutable | Majeure | Env |

## 4. Risques principaux (état à l'issue de la campagne)

| Risque | Description | Score | Constat | État |
|---|---|---|---|---|
| R01 | Double encaissement / commande | 20 | **Confirmé** (BUG-001) | Ouvert |
| R02 | Survente, stock négatif | 20 | **Confirmé** (BUG-004) | Ouvert |
| R03 | Commande chez un restaurant fermé | 16 | **Confirmé** (BUG-002) | Ouvert |
| R04 | Paiement en espèces incohérent | 16 | **Confirmé** (BUG-003) | Ouvert |
| R05 | Promotions et coupons erronés | 16 | **Confirmé** (BUG-007, 008, 009) | Ouvert |
| R06 | Sécurité de configuration et de session | 15 | **Confirmé** (BUG-015, 023) | Ouvert |
| R07 | Accès non autorisé aux données | 10 | Non confirmé : contrôles d'accès corrects | Maîtrisé |
| R08 | Concurrence sur le stock | 12 | **Confirmé** (BUG-029) : 4 commandes simultanées acceptées pour un stock de 2, stock final 1 | Ouvert |
| R20 | RGPD | 8 | Hors périmètre | Inconnu |

## 5. Analyse

**Ce qui fonctionne.** Le parcours nominal (accueil, menu, panier, checkout par carte avec coupon, annulation) donne 14 réussites sur 16 cas nominaux ; les deux autres sont bloqués par des éléments d'interface manquants. L'authentification (messages génériques, doublons refusés), le contrôle d'accès (administration, commandes d'autrui, adresses d'autrui), les bornes de quantité de l'API (1 à 20) et le calcul des coupons aux bornes (minimum inclusif, plafond) sont conformes.

**Ce qui est fragile.** Les règles métier échouent à 75.0 % (18 échecs sur 24 cas exécutés). Quatre constats se répètent :

1. **Règles affichées mais non appliquées** : minimum de commande, bandeau HORS STOCK, badge FERMÉ, promotion à 15 %. L'interface promet, le serveur ne vérifie pas.
2. **Divergence entre canaux** : l'API et le web n'appliquent pas les mêmes règles (expiration des coupons, validation des entrées). La logique est dupliquée dans `orders.py` et `api.py`.
3. **Contrôles uniquement côté navigateur** : attributs `min`, `max`, `minlength` ; il suffit d'éditer le DOM ou d'appeler l'endpoint directement (BUG-004, BUG-019).
4. **Effets de bord oubliés** : l'annulation ne rend ni le stock ni le paiement (BUG-016) ; le doublon PayPal décrémente deux fois le stock (BUG-001).

La cause racine commune est l'**absence d'une couche de règles de commande unique** (restaurant ouvert, stock, minimum, coupon, paiement) partagée par le web et l'API : c'est le premier chantier du plan d'amélioration (AM-02).

## 6. Cas bloqués ou non tranchés

| Cas | Titre | Statut | Motif |
|---|---|---|---|
| TC-NOM-15 | Ajouter un restaurant aux favoris depuis l'interface | Blocked | Aucun bouton « favori » dans l'interface : la route POST /favorite/<id> existe mais n'est reliée à aucun écran. Cas non exécutable par l'UI. |
| TC-NOM-16 | Supprimer une adresse depuis l'interface | Blocked | Aucun bouton « Supprimer » dans l'interface : la route /profile/address/<id>/delete n'est reliée à aucun écran. |
| TC-ERR-21 | API : produit indisponible (available = false) | Blocked | Les 25 produits du jeu de données sont disponibles et aucune interface ne permet d'en rendre un indisponible : cas non exécutable sans modifier la base. |
| TC-RM-25 | WELCOME10 réservé à la première commande | Skipped | Le code « WELCOME10 » est accepté à chaque commande (réductions ['2.38', '2.38']). Aucune spécification ne dit s'il est limité à la première commande : règle à clarifier avec le métier avant de conclure. |
| TC-EXT-07 | Filtre par catégorie sur le menu d'un restaurant | Blocked | La route accepte ?category= et ?q= mais aucun contrôle de filtre n'est affiché sur la page du restaurant : filtrage inaccessible depuis l'interface. |

## 7. Limites de la campagne

- Un seul moteur de navigateur (Chromium) ; mobile émulé à 375 px, pas d'appareil réel.
- **Docker Compose non exécuté** : le démon Docker n'est pas disponible dans l'environnement de test ; TC-ENV-01 est établi par l'exécution directe de `docker-entrypoint.sh` (Permission denied) et par le mode Git du fichier (100644).
- Pas de test de charge ; un seul test de concurrence (4 requêtes parallèles, TC-NFR-01).
- Sécurité limitée aux contrôles de base ; pas de test d'intrusion.
- Règles ambiguës non tranchées (éligibilité de WELCOME10, TC-RM-25) : à clarifier avec le Product Owner.
- Les retours utilisateurs reposent sur un petit échantillon (voir `user-feedback.md`) ; ils orientent, ils ne prouvent pas.

## 8. Décision Go / No-Go

| Critère | Seuil | Résultat | Verdict |
|---|---|---|---|
| Aucune anomalie Critique ouverte | 0 | 1 | ❌ |
| Aucune anomalie Majeure ouverte sur J1 à J3 | 0 | 8 (BUG-002, 003, 004, 005, 007, 009, 014, 019) | ❌ |
| Taux de réussite P1 | ≥ 95 % | 48.5 % | ❌ |
| Taux de réussite global | ≥ 90 % | 51.1 % | ❌ |
| Aucun cas P1 Blocked | 0 | 0 | ✅ |
| Risques résiduels acceptés et tracés | Oui | Registre dans `risk-matrix.md` | ✅ |

**Verdict : NO-GO.**

### Conditions de levée du No-Go

1. Corriger et revalider les 5 anomalies **P1** : BUG-001, 002, 003, 004, 025.
2. Corriger ou accepter formellement, avec décision écrite, les 11 anomalies **P2** (BUG-5, 6, 7, 9, 10, 14, 15, 16, 19, 23, 29). Les points de sécurité (BUG-015, 023) ne devraient pas être acceptés.
3. Rejouer l'ensemble des cas P1 et les cas liés aux bugs corrigés ; viser 95 % de réussite P1.
4. Rejouer le test de concurrence sur le stock (TC-NFR-01) après correction, élargir à un vrai test de charge, et décider du traitement du risque RGPD (R20).
5. Mettre en place des tests automatisés de non-régression sur chaque anomalie corrigée (AM-11).

## 9. Plan de revalidation

| Étape | Contenu |
|---|---|
| 1. Corrections | Branche `fix/<bug-id>` par anomalie, sans toucher à la branche principale ; une Pull Request par correctif |
| 2. Retest ciblé | Rejouer les cas liés (colonne « Bug lié » de `test-cases.xlsx`) ; statut du bug : Corrigé → Fermé ou Rouvert |
| 3. Non-régression | Rejouer tous les cas P1 et les cas Pass qui touchent le même module |
| 4. Revue | Mettre à jour ce rapport (chiffres, décision) et la matrice de risques |

## 10. Annexe : traçabilité anomalie ↔ cas de test

| Bug | Sévérité | Priorité | Cas associés (statut) |
|---|---|---|---|
| [BUG-001](bug-reports/BUG-001.md) | Critique | P1 | TC-RM-09 (Fail), TC-RM-10 (Fail) |
| [BUG-002](bug-reports/BUG-002.md) | Majeure | P1 | TC-RM-02 (Fail), TC-RM-03 (Fail) |
| [BUG-003](bug-reports/BUG-003.md) | Majeure | P1 | TC-RM-06 (Fail), TC-RM-07 (Fail) |
| [BUG-004](bug-reports/BUG-004.md) | Majeure | P1 | TC-LIM-08 (Fail), TC-LIM-09 (Fail), TC-LIM-10 (Fail), TC-LIM-13 (Fail) |
| [BUG-005](bug-reports/BUG-005.md) | Majeure | P2 | TC-RM-04 (Fail), TC-RM-05 (Fail) |
| [BUG-006](bug-reports/BUG-006.md) | Majeure | P2 | TC-LIM-07 (Fail) |
| [BUG-007](bug-reports/BUG-007.md) | Majeure | P2 | TC-RM-11 (Fail) |
| [BUG-008](bug-reports/BUG-008.md) | Mineure | P3 | TC-RM-13 (Fail) |
| [BUG-009](bug-reports/BUG-009.md) | Majeure | P2 | TC-ERR-14 (Fail), TC-ERR-20 (Fail) |
| [BUG-010](bug-reports/BUG-010.md) | Majeure | P2 | TC-ERR-08 (Fail), TC-ERR-09 (Fail), TC-ERR-10 (Fail) |
| [BUG-011](bug-reports/BUG-011.md) | Mineure | P3 | TC-ERR-05 (Fail), TC-EXT-16 (Fail) |
| [BUG-012](bug-reports/BUG-012.md) | Mineure | P3 | TC-ERR-22 (Fail) |
| [BUG-013](bug-reports/BUG-013.md) | Mineure | P3 | TC-LIM-11 (Fail), TC-EXT-14 (Fail) |
| [BUG-014](bug-reports/BUG-014.md) | Majeure | P2 | TC-RM-22 (Fail) |
| [BUG-015](bug-reports/BUG-015.md) | Majeure | P2 | TC-ERR-16 (Fail) |
| [BUG-016](bug-reports/BUG-016.md) | Majeure | P2 | TC-RM-16 (Fail) |
| [BUG-017](bug-reports/BUG-017.md) | Mineure | P3 | TC-RM-17 (Fail) |
| [BUG-018](bug-reports/BUG-018.md) | Mineure | P3 | TC-RM-18 (Fail), TC-RM-19 (Fail), TC-EXT-17 (Fail) |
| [BUG-019](bug-reports/BUG-019.md) | Majeure | P2 | TC-RM-20 (Fail) |
| [BUG-020](bug-reports/BUG-020.md) | Mineure | P3 | TC-RM-23 (Fail) |
| [BUG-021](bug-reports/BUG-021.md) | Mineure | P3 | TC-RM-24 (Fail) |
| [BUG-022](bug-reports/BUG-022.md) | Mineure | P3 | TC-NOM-15 (Blocked), TC-NOM-16 (Blocked), TC-ERR-21 (Blocked), TC-EXT-07 (Blocked), TC-EXT-18 (Fail) |
| [BUG-023](bug-reports/BUG-023.md) | Majeure | P2 | TC-ERR-23 (Fail), TC-EXT-19 (Fail), TC-EXT-20 (Fail) |
| [BUG-024](bug-reports/BUG-024.md) | Mineure | P3 | TC-LIM-12 (Fail), TC-EXT-15 (Fail) |
| [BUG-025](bug-reports/BUG-025.md) | Majeure | P1 | TC-ENV-01 (Fail) |
| [BUG-026](bug-reports/BUG-026.md) | Mineure | P3 | TC-EXT-01 (Fail) |
| [BUG-027](bug-reports/BUG-027.md) | Mineure | P3 | TC-EXT-10 (Fail) |
| [BUG-028](bug-reports/BUG-028.md) | Mineure | P3 | TC-EXT-03 (Fail) |
| [BUG-029](bug-reports/BUG-029.md) | Majeure | P2 | TC-NFR-01 (Fail) |

