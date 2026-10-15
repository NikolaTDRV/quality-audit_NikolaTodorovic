# Stratégie de test — QuickOrder V3.1

| | |
|---|---|
| **Produit** | QuickOrder V3.1 (application web Flask + API REST, SQLite) |
| **Équipe** | Quality audit |
| **Date** | 13/10/2026 |
| **Objectif** | Évaluer la qualité avant mise en production et recommander **Go / No-Go** |
| **Périmètre de cette campagne** | **24 cas de test** (6 nominaux, 6 limites, 6 erreurs, 6 règles métier) et **8 bug reports reproductibles** |

## 1. Contexte et objectifs

QuickOrder est une plateforme de commande de repas déjà développée. La mission n'est pas de la reconstruire mais de **mesurer sa qualité** : trouver des anomalies, les prouver, évaluer le risque et décider si la mise en production est acceptable. Le code source n'est **pas modifié**.

Objectifs, par ordre d'importance :

1. Protéger l'**argent** : paiement, remises, totaux.
2. Garantir que ce qui est commandé **peut être livré** : restaurant ouvert, stock, minimum.
3. Protéger les **comptes et la session** : accès, redirections.
4. Vérifier la **fiabilité du contrat d'API** (statuts, erreurs).

## 2. Périmètre

### 2.1 Dans le périmètre

| Domaine | Contenu testé |
|---|---|
| Authentification | Connexion valide / invalide, redirection après connexion |
| Panier et commande | Ajout au panier, commande par carte, annulation, minimum, restaurant fermé, stock |
| Paiement | Carte, PayPal, espèces (simulés) |
| Coupons | WELCOME10 (minimum, plafond), ATLAS15, TOKYO30 |
| Contrôle d'accès | Accès admin, commande d'un autre client, API sans clé |
| API REST | Restaurants, commandes, coupons, quantités, entrées mal formées |

### 2.2 Hors périmètre

| Exclusion | Raison |
|---|---|
| Performance et charge | Outillage non prévu ; SQLite local |
| Test d'intrusion approfondi | Hors durée de la mission ; seuls des contrôles de base sont faits |
| RGPD / conformité | Nécessite un audit dédié |
| Vrai paiement bancaire | Paiement simulé |
| Multi-navigateurs, appareils réels | Chromium uniquement |
| Fonctionnalités non ciblées par les 24 cas | Favoris, avis, profil et adresses, administration des statuts, installation Docker : non évalués ici |

## 3. Hypothèses et contraintes

- Aucune modification du code de QuickOrder.
- Chaque cas démarre sur une **base réinitialisée** (`python seed.py`).
- L'API agit au nom de `alice@example.com` quelle que soit la clé : choix pédagogique, pas une anomalie.
- Les règles métier non écrites sont déduites de l'interface (restaurant « Fermé », « Commande minimum », offre ATLAS15 affichée).

## 4. Parcours critiques

| ID | Parcours | Pourquoi critique | Cas principaux |
|---|---|---|---|
| J1 | Menu → panier → checkout → confirmation (carte) | Cœur du chiffre d'affaires | TC-NOM-02, 03, TC-LIM-06, TC-RM-01, 02 |
| J2 | Paiement PayPal et espèces | Risque financier direct | TC-RM-03, 04 |
| J3 | Coupons et promotions | Prix et promesse faite au client | TC-LIM-01 à 03, TC-RM-05, 06 |
| J4 | Compte et accès | Porte d'entrée, protection des données | TC-NOM-01, TC-ERR-01, 03, 04, 06 |
| J5 | API | Canal utilisé par des intégrations | TC-NOM-05, 06, TC-LIM-04, 05, TC-ERR-02, 05 |

## 5. Approche et conception des cas

| Catégorie | Nb | Objectif | Cas |
|---|---|---|---|
| Nominal | 6 | Le parcours fonctionne « au soleil » | TC-NOM-01 à TC-NOM-06 |
| Limite | 6 | Bornes des règles : minimum, plafond, quantité, stock | TC-LIM-01 à TC-LIM-06 |
| Erreur | 6 | Entrées invalides, accès interdits, API mal utilisée | TC-ERR-01 à TC-ERR-06 |
| Règle métier | 6 | Règles annoncées : restaurant ouvert, minimum, paiement, coupons | TC-RM-01 à TC-RM-06 |

Techniques :

- **Valeurs limites** : sous-total 19,99 / 20,00 pour le minimum de WELCOME10 ; plafond de réduction à 8 € ; quantité 0, 1, 20, 21 ; stock − 1, stock, stock + 1.
- **Table de décision** (coupons) : actif, expiré, minimum atteint, plafond atteint, restaurant concerné.
- **Partitions d'équivalence** : connexion valide / invalide ; clé API valide / absente.
- **Devinette d'erreurs** : `NaN`, `Infinity`, `1e999`, corps JSON de mauvais type, paramètre `next` externe, édition du DOM (suppression de `max`).
- **Comparaison web / API** : la même règle est vérifiée sur les deux canaux ; une différence est une anomalie.

## 6. Environnements et données

| Élément | Valeur |
|---|---|
| Application | http://127.0.0.1:5000 (`python run.py`) |
| Navigateur | Chromium piloté par Playwright : captures, vidéo, édition du DOM comme dans les DevTools |
| API | Requêtes HTTP (`requests`, équivalent curl) avec `X-API-Key: quickorder-demo-key` |
| Comptes | alice@example.com / Password123! · bob@example.com / Password123! · admin@quickorder.local / Admin123! |
| Jeu de données | Onglet « Légende » de `test-cases.xlsx` (6 restaurants dont Night Sushi fermé, Salmon Bowl stock 2, Veggie Burger stock 0, coupons dont ATLAS15) |
| Réinitialisation | `python seed.py` avant chaque cas (fait par le script de campagne) |

## 7. Priorisation « risque × impact »

Voir `risk-matrix.md` (score = probabilité × impact).

| Priorité du cas | Règle |
|---|---|
| **P1** | Parcours critique ou règle financière ; risque de score ≥ 12 ; exécuté en premier |
| **P2** | Important ; risque de score 6 à 11 |
| **P3** | Confort ou cas rare (aucun dans cette campagne) |

Répartition : 18 cas P1, 6 cas P2.

## 8. Gestion des anomalies

| Sévérité | Définition |
|---|---|
| Critique | Perte financière directe, perte de données, parcours principal inutilisable |
| Majeure | Règle métier violée, faille de sécurité, parcours dégradé |
| Mineure | Gêne, incohérence d'affichage, contournement simple |

| Priorité | Définition |
|---|---|
| P1 | À corriger avant toute mise en production |
| P2 | À corriger avant la mise en production, ou juste après si le risque est accepté |
| P3 | Backlog |

Chaque fiche contient : **titre, contexte, préconditions, étapes, résultat attendu, résultat obtenu, preuve, sévérité, priorité**. Une anomalie n'est retenue que si elle est **rejouée avec succès** : le script `docs/automation/reproduce_bugs.sh` affiche `REPRODUIT` ou `NON REPRODUIT` pour chacune des 8.

## 9. Critères d'entrée, de sortie et de décision

**Entrée** : application démarrée, base seedée, comptes de démonstration opérationnels.

**Sortie** : les 24 cas exécutés ; chaque échec rattaché à une fiche de bug avec preuve.

**Décision Go** (toutes les conditions) :

1. Aucune anomalie **Critique** ouverte.
2. Aucune anomalie **Majeure** ouverte sur les parcours J1 à J3.
3. Réussite ≥ 95 % sur les cas P1 et ≥ 90 % global.
4. Aucun cas P1 « Blocked ».
5. Risques résiduels connus, acceptés et tracés.

Sinon : **No-Go**, avec conditions de levée.

## 10. Livrables et traçabilité

| Livrable | Fichier |
|---|---|
| Stratégie | `docs/test-strategy.md` |
| Risques | `docs/risk-matrix.md` |
| 24 cas et résultats | `docs/test-cases.xlsx` |
| Campagne et Go / No-Go | `docs/execution-report.md` |
| 8 bug reports | `docs/bug-reports/` |
| Tests utilisateurs | `docs/user-feedback.md` |
| Plan d'amélioration | `docs/improvement-plan.md` |
| Preuves | `docs/evidence/` |
| Scripts rejouables | `docs/automation/` |

Traçabilité : risque (R-xx) → cas de test (TC-…) → anomalie (BUG-…) → amélioration (AM-…).
