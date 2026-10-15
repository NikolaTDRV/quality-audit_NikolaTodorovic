# Rapport d'exécution de la campagne — QuickOrder V3.1

| | |
|---|---|
| **Date** | 13/10/2026 |
| **Version testée** | QuickOrder V3.1, base initialisée par `python seed.py` |
| **Environnement** | http://127.0.0.1:5000 · Chromium (Playwright) · requêtes HTTP · Python 3.13 · SQLite |
| **Périmètre** | 24 cas de test, 8 anomalies |

## 1. Recommandation : **NO-GO**

La mise en production n'est pas recommandée. 8 cas sur 24 échouent, et les 8 anomalies sont **reproductibles** (`docs/automation/reproduce_bugs.sh` : 8 / 8 `REPRODUIT`). Une anomalie est **Critique** : le paiement PayPal crée deux commandes (BUG-001). Les règles de commande (restaurant fermé, stock, minimum) et le paiement en espèces ne sont pas contrôlés par le serveur.

## 2. Résultats chiffrés

| Indicateur | Valeur |
|---|---|
| Cas prévus / exécutés | 24 / 24 (100 %) |
| Pass | 16 |
| Fail | 8 |
| Blocked / Skipped | 0 / 0 |
| Taux de réussite global | **66,7 %** |
| Taux de réussite P1 | **61,1 %** (11 / 18) |
| Taux de réussite P2 | 83,3 % (5 / 6) |

### 2.1 Par catégorie

| Catégorie | Cas | Pass | Fail | Réussite |
|---|---|---|---|---|
| Nominal | 6 | 6 | 0 | 100,0 % |
| Limite | 6 | 5 | 1 | 83,3 % |
| Erreur | 6 | 4 | 2 | 66,7 % |
| Règle métier | 6 | 1 | 5 | 16,7 % |
| **Total** | 24 | 16 | 8 | 66,7 % |

### 2.2 Par canal

| Canal | Cas | Pass | Fail |
|---|---|---|---|
| UI | 15 | 8 | 7 |
| API | 9 | 8 | 1 |

### 2.3 Cas en échec par module

| Module | Échecs | Cas |
|---|---|---|
| Commande | 2 | TC-RM-01, TC-RM-02 |
| Paiement | 2 | TC-RM-03, TC-RM-04 |
| Stock | 1 | TC-LIM-06 |
| API | 1 | TC-ERR-05 |
| Authentification | 1 | TC-ERR-06 |
| Coupons | 1 | TC-RM-05 |

## 3. Anomalies

| Sévérité | P1 | P2 | Total |
|---|---|---|---|
| Critique | 1 | 0 | 1 |
| Majeure | 3 | 4 | 7 |
| **Total** | 4 | 4 | 8 |

| Bug | Titre | Sévérité | Priorité | Cas (statut) |
|---|---|---|---|---|
| [BUG-001](bug-reports/BUG-001.md) | Le paiement PayPal crée deux commandes identiques (web et API) | Critique | P1 | TC-RM-04 (Fail) |
| [BUG-002](bug-reports/BUG-002.md) | Un restaurant fermé peut recevoir des commandes (web et API) | Majeure | P1 | TC-RM-01 (Fail) |
| [BUG-003](bug-reports/BUG-003.md) | Le paiement en espèces accepte un montant inférieur au total (monnaie négative) | Majeure | P1 | TC-RM-03 (Fail) |
| [BUG-004](bug-reports/BUG-004.md) | Contrôles de stock défaillants : quantité supérieure au stock et produit en rupture commandables | Majeure | P1 | TC-LIM-06 (Fail) |
| [BUG-005](bug-reports/BUG-005.md) | Le minimum de commande du restaurant n'est pas appliqué (web et API) | Majeure | P2 | TC-RM-02 (Fail) |
| [BUG-006](bug-reports/BUG-006.md) | ATLAS15 est annoncé à 15 % mais appliqué à 10 % | Majeure | P2 | TC-RM-05 (Fail) |
| [BUG-007](bug-reports/BUG-007.md) | API : des entrées mal formées provoquent des erreurs 500 (traceback exposé) | Majeure | P2 | TC-ERR-05 (Fail) |
| [BUG-008](bug-reports/BUG-008.md) | Redirection ouverte après connexion (paramètre `next`) | Majeure | P2 | TC-ERR-06 (Fail) |

## 4. Analyse

- **Les parcours nominaux et les contrôles d'accès sont sains** : les 6 cas nominaux, la sécurité des accès (TC-ERR-01, 02, 03, 04), les bornes du coupon WELCOME10 et les quantités API passent. La base fonctionnelle est correcte.
- **Les règles métier sont le point faible** : 5 cas sur 6 échouent. Le serveur ne contrôle pas ce que l'interface annonce (restaurant « Fermé », « Commande minimum », offre ATLAS15, montant remis en espèces).
- **Le web et l'API partagent les mêmes défauts** : BUG-001 à 006 se reproduisent par l'interface et par l'API. La cause est dans la logique commune de commande, pas dans l'affichage.
- **Une même cause racine** pour BUG-002, 004 et 005 : absence d'un contrôle unique des règles de commande côté serveur (voir AM-02).
- **Deux points de robustesse et de sécurité** : l'API répond 500 avec le débogueur Werkzeug visible sur des entrées malformées (BUG-007) et la connexion redirige vers un site externe (BUG-008).

## 5. Risques principaux (état à l'issue de la campagne)

| Risque | Score | Constat |
|---|---|---|
| R01 — Double commande (et double encaissement) lors du paiement PayPal | 20 | BUG-001 |
| R02 — Survente : quantité supérieure au stock, produit en rupture, stock négatif | 20 | BUG-004 |
| R03 — Commande acceptée chez un restaurant fermé | 16 | BUG-002 |
| R04 — Paiement en espèces incohérent (montant remis inférieur au total) | 16 | BUG-003 |
| R05 — Coupons et promotions erronés ou incohérents avec l'annonce | 16 | BUG-006 |
| R06 — Redirection ouverte après connexion (hameçonnage) | 12 | BUG-008 |
| R07 — API fragile : erreur 500 et débogueur exposé sur entrées mal formées | 12 | BUG-007 |
| R08 — Commande sous le minimum du restaurant | 12 | BUG-005 |

Détail dans `risk-matrix.md`.

## 6. Limites de la campagne

- Campagne **ciblée de 24 cas** : elle ne prétend pas couvrir toute l'application (favoris, avis, profil, administration des statuts, installation Docker non évalués).
- Un seul navigateur (Chromium), pas d'appareil réel, pas de test de charge ni de concurrence.
- Paiement simulé : seule la logique applicative est testée.
- Résultats obtenus sur une base fraîchement initialisée avant chaque cas.

## 7. Décision Go / No-Go

| Critère | Seuil | Résultat | Verdict |
|---|---|---|---|
| Aucune anomalie Critique ouverte | 0 | 1 (BUG-001) | ❌ |
| Aucune anomalie Majeure ouverte sur J1 à J3 | 0 | 5 (BUG-002, 003, 004, 005, 006) | ❌ |
| Taux de réussite P1 | ≥ 95 % | 61,1 % | ❌ |
| Taux de réussite global | ≥ 90 % | 66,7 % | ❌ |
| Aucun cas P1 Blocked | 0 | 0 | ✅ |
| Risques résiduels acceptés et tracés | Oui | Registre dans `risk-matrix.md` | ✅ |

**Verdict : NO-GO.**

### Conditions de levée du No-Go

1. Corriger et revalider les 4 anomalies **P1** : BUG-001, 002, 003, 004.
2. Corriger les 4 anomalies **P2** (BUG-005, 006, 007, 008) ou les accepter par une décision écrite ; BUG-007 et BUG-008 (sécurité) ne devraient pas être acceptés.
3. Rejouer les 24 cas et `reproduce_bugs.sh` : attendu 24 / 24 Pass et 8 / 8 `NON REPRODUIT`.
4. Ajouter à la suite automatisée un test de non-régression par anomalie (AM-06).

## 8. Plan de revalidation

| Étape | Contenu |
|---|---|
| 1. Corrections | Une branche `fix/<bug-id>` par anomalie ; une Pull Request par correctif |
| 2. Retest ciblé | Rejouer le cas lié (colonne « Bug lié » de `test-cases.xlsx`) et la section du bug dans `reproduce_bugs.sh` |
| 3. Non-régression | Rejouer les 24 cas (`python run_campaign.py`) |
| 4. Revue | Mettre à jour ce rapport et la matrice de risques |

## 9. Preuves

- Captures, traces requête / réponse et vidéo du double paiement PayPal : `docs/evidence/`.
- Rejeu en ligne de commande des 8 bugs : `docs/evidence/reproduction-curl.txt`.
- Résultats bruts de la campagne : `docs/automation/results.json`.
