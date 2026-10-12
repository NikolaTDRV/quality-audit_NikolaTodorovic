# Matrice de risques

Cette matrice sert à **prioriser les tests** : plus le score (probabilité × impact) est élevé, plus les cas associés sont exécutés tôt et profondément. Les scores ont été relus après la campagne (colonne « Constat »).

## Échelles

| Valeur | Probabilité (le problème existe ou survient) | Impact (conséquence pour le métier) |
|---|---|---|
| 1 | Très improbable | Négligeable (cosmétique) |
| 2 | Improbable | Gêne mineure, contournement simple |
| 3 | Possible | Parcours dégradé ou donnée fausse sans perte directe |
| 4 | Probable | Perte financière limitée, commande non honorée, atteinte à la confiance |
| 5 | Quasi certain | Perte financière importante, fuite de données, blocage de la mise en production |

Niveau : **Critique** ≥ 16 · **Élevé** 10 à 15 · **Moyen** 6 à 9 · **Faible** ≤ 5. La probabilité est estimée avant la campagne d'après l'analyse du produit, puis confirmée ou corrigée par les résultats.

## Grille probabilité × impact

| Probabilité \ Impact | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | · | · | · | R02 | · |
| **4** | · | R14, R15 | R09, R11, R12 | R03, R04, R05 | R01 |
| **3** | · | R17, R18, R19 | R13, R16 | R08, R10 | R06 |
| **2** | · | · | · | R20 | R07 |
| **1** | · | · | · | · | · |

## Registre des risques (classé par score)

| ID | Risque | P | I | Score | Niveau | Parcours | Constat (bugs) | Tests associés | Parade recommandée |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Double encaissement ou double commande lors du paiement | 4 | 5 | **20** | Critique | J1, J2 | BUG-001 | TC-RM-09, TC-RM-10 | Idempotence de la commande, test de non-régression, revue du flux de paiement |
| R02 | Survente : produit hors stock ou quantité > stock acceptée, stock négatif | 5 | 4 | **20** | Critique | J1, J7 | BUG-004 | TC-LIM-08, TC-LIM-09, TC-LIM-10, TC-LIM-13 | Contrôle serveur du stock, décrément atomique, plafonds de quantité |
| R03 | Commande acceptée pour un restaurant fermé | 4 | 4 | **16** | Critique | J1, J7 | BUG-002 | TC-RM-02, TC-RM-03 | Contrôle `is_open` à l'ajout, au checkout et dans l'API |
| R04 | Paiement en espèces incohérent (montant insuffisant accepté) | 4 | 4 | **16** | Critique | J2 | BUG-003 | TC-RM-06, TC-RM-07, TC-RM-08 | Validation serveur du montant remis |
| R05 | Promotions et coupons erronés (ATLAS15, TOKYO30, coupon expiré par API) | 4 | 4 | **16** | Critique | J3 | BUG-007, BUG-008, BUG-009 | TC-RM-11, TC-RM-12, TC-RM-13, TC-ERR-13, TC-ERR-14, TC-ERR-20 | Source unique de calcul, cohérence promo/coupon, tests paramétrés |
| R06 | Sécurité de configuration et de session (debug, secret par défaut, CSRF, redirection ouverte) | 3 | 5 | **15** | Élevé | J4, J7 | BUG-015, BUG-023 | TC-ERR-16, TC-ERR-23, TC-EXT-19, TC-EXT-20 | Durcissement de la configuration, jetons CSRF, validation de `next` |
| R08 | Concurrence sur le dernier exemplaire en stock | 3 | 4 | **12** | Élevé | J1 | BUG-029 | TC-NFR-01 | Mise à jour atomique du stock, test de charge ciblé |
| R09 | Commande sous le minimum du restaurant | 4 | 3 | **12** | Élevé | J1 | BUG-005 | TC-RM-04, TC-RM-05 | Contrôle du sous-total au checkout et dans l'API |
| R10 | Adresse de livraison vide ou fictive | 3 | 4 | **12** | Élevé | J1, J4 | BUG-014 | TC-RM-22 | Pas d'adresse créée à l'inscription ; adresse complète obligatoire |
| R11 | API fragile : erreurs 500 sur entrées mal formées | 4 | 3 | **12** | Élevé | J7 | BUG-010, BUG-011 | TC-ERR-05, TC-ERR-08, TC-ERR-09, TC-ERR-10, TC-EXT-16 | Validation de schéma, gestionnaires d'erreurs JSON |
| R12 | Données incohérentes après annulation (stock, paiement) | 4 | 3 | **12** | Élevé | J5 | BUG-016 | TC-RM-16 | Annulation centralisée avec restitution du stock et du paiement |
| R07 | Accès non autorisé aux données (commandes, adresses, administration) | 2 | 5 | **10** | Élevé | J4, J5, J6 | — | TC-ERR-11, TC-ERR-12, TC-ERR-15 | Contrôles d'accès existants à conserver ; tests de non-régression |
| R13 | Installation impossible pour une partie des utilisateurs (Docker sous Linux/macOS) | 3 | 3 | **9** | Moyen | J8 | BUG-025, BUG-026 | TC-ENV-01, TC-EXT-01 | Corriger le mode du script, tester le démarrage conteneur |
| R16 | Statuts de commande incohérents (transitions administrateur) | 3 | 3 | **9** | Moyen | J6 | BUG-017 | TC-RM-17 | Machine à états |
| R14 | Parcours de découverte faux (filtre inversé, recherche limitée au nom) | 4 | 2 | **8** | Moyen | J1 | BUG-006, BUG-013 | TC-LIM-07, TC-LIM-11, TC-EXT-14, TC-NOM-11 | Corriger les filtres, tests paramétrés |
| R15 | Fonctionnalités annoncées inaccessibles ou ambiguës (favoris, adresses, avis, retrait panier) | 4 | 2 | **8** | Moyen | J4, J5 | BUG-018, BUG-020, BUG-022 | TC-NOM-15, TC-NOM-16, TC-RM-18, TC-RM-19, TC-RM-23, TC-EXT-07, TC-EXT-17, TC-EXT-18 | Compléter l'interface, conserver les saisies |
| R20 | Conformité RGPD et gestion des données personnelles | 2 | 4 | **8** | Moyen | J4 | — | Hors périmètre de la campagne | À auditer séparément (consentement, suppression de compte, rétention) |
| R17 | Horodatages erronés, libellés techniques et affichage mobile | 3 | 2 | **6** | Moyen | J5 | BUG-021, BUG-027, BUG-028 | TC-RM-24, TC-EXT-10, TC-EXT-03 | Fuseau explicite et conversion à l'affichage |
| R18 | Qualité des données saisies (nom, email, téléphone, code postal) | 3 | 2 | **6** | Moyen | J4 | BUG-024 | TC-LIM-12, TC-EXT-15 | Validation de schéma côté serveur |
| R19 | Avis falsifiables et jamais affichés | 3 | 2 | **6** | Moyen | J5 | BUG-018 | TC-RM-18, TC-RM-19, TC-EXT-17 | Avis liés à une commande ; affichage et moyenne |

## Lecture

- **5 risques critiques** (R01, R02, R03, R04, R05) : tous concernent l'argent ou la disponibilité réelle de la commande. Ils ont été testés en premier et se sont tous confirmés par au moins un bug (R02 et R01 par l'exécution réelle sur le web et l'API).
- **7 risques élevés** (R06, R07, R08, R09, R10, R11, R12) : sécurité, règles de commande et fiabilité de l'API.
- Le risque d'accès non autorisé (R07) a une probabilité estimée faible (2) mais un impact maximal (5), soit un score de 10 (niveau Élevé) : il a été testé en priorité et les contrôles d'accès se sont révélés corrects (aucun bug).
- R20 (RGPD) n'est pas couvert par cette campagne et doit faire l'objet d'un audit dédié avant la mise en production.

## Règle d'ordonnancement des tests

1. Score ≥ 16 : exécution en premier, UI **et** API, chaque règle testée aux limites.
2. Score 10 à 15 : exécution ensuite, cas nominaux, limites et erreurs.
3. Score ≤ 9 : cas nominal et un cas d'erreur ; exploration libre si le temps le permet.
