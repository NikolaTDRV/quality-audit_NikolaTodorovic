# Matrice de risques

La matrice sert à **prioriser les 24 cas de test** : plus le score (probabilité × impact) est élevé, plus le risque est testé tôt. Les probabilités ont été estimées avant la campagne puis relues avec les résultats (colonne « Constat »).

## Échelles

| Valeur | Probabilité | Impact |
|---|---|---|
| 1 | Très improbable | Négligeable |
| 2 | Improbable | Gêne mineure, contournement simple |
| 3 | Possible | Parcours dégradé ou donnée fausse sans perte directe |
| 4 | Probable | Perte financière limitée, commande non honorée, atteinte à la confiance |
| 5 | Quasi certain | Perte financière importante, fuite de données, blocage de la mise en production |

Niveau : **Critique** ≥ 16 · **Élevé** 10 à 15 · **Moyen** 6 à 9 · **Faible** ≤ 5.

## Grille probabilité × impact

| Probabilité \ Impact | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | · | · | · | R02 | · |
| **4** | · | · | R07, R08 | R03, R04, R05 | R01 |
| **3** | · | · | · | R06 | · |
| **2** | · | · | · | · | R09, R10 |
| **1** | · | · | · | · | · |

## Registre des risques (classé par score)

| ID | Risque | P | I | Score | Niveau | Parcours | Constat | Cas de test | Parade recommandée |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Double commande (et double encaissement) lors du paiement PayPal | 4 | 5 | **20** | Critique | J2 | [BUG-001](bug-reports/BUG-001.md) | TC-RM-04, TC-NOM-03, TC-NOM-06 | Idempotence de la création de commande ; test de non-régression |
| R02 | Survente : quantité supérieure au stock, produit en rupture, stock négatif | 5 | 4 | **20** | Critique | J1 | [BUG-004](bug-reports/BUG-004.md) | TC-LIM-06 | Contrôle serveur du stock et décrément atomique |
| R03 | Commande acceptée chez un restaurant fermé | 4 | 4 | **16** | Critique | J1 | [BUG-002](bug-reports/BUG-002.md) | TC-RM-01 | Contrôle `is_open` à l'ajout, au checkout et dans l'API |
| R04 | Paiement en espèces incohérent (montant remis inférieur au total) | 4 | 4 | **16** | Critique | J2 | [BUG-003](bug-reports/BUG-003.md) | TC-RM-03 | Validation serveur du montant remis |
| R05 | Coupons et promotions erronés ou incohérents avec l'annonce | 4 | 4 | **16** | Critique | J3 | [BUG-006](bug-reports/BUG-006.md) | TC-RM-05, TC-RM-06, TC-LIM-01, TC-LIM-02, TC-LIM-03, TC-NOM-03 | Source unique pour l'offre affichée et le coupon appliqué |
| R06 | Redirection ouverte après connexion (hameçonnage) | 3 | 4 | **12** | Élevé | J4 | [BUG-008](bug-reports/BUG-008.md) | TC-ERR-06 | N'accepter que des chemins internes pour `next` |
| R07 | API fragile : erreur 500 et débogueur exposé sur entrées mal formées | 4 | 3 | **12** | Élevé | J5 | [BUG-007](bug-reports/BUG-007.md) | TC-ERR-05, TC-ERR-02, TC-LIM-04, TC-LIM-05 | Validation de schéma ; gestionnaires d'erreurs JSON ; debug désactivé |
| R08 | Commande sous le minimum du restaurant | 4 | 3 | **12** | Élevé | J1 | [BUG-005](bug-reports/BUG-005.md) | TC-RM-02 | Contrôle du sous-total au checkout et dans l'API |
| R09 | Accès non autorisé aux comptes, commandes et à l'administration | 2 | 5 | **10** | Élevé | J4 | Aucun bug : contrôles conformes | TC-ERR-01, TC-ERR-03, TC-ERR-04 | Contrôles existants à conserver ; non-régression |
| R10 | Parcours nominal inutilisable (connexion, panier, commande, annulation, API) | 2 | 5 | **10** | Élevé | J1, J5 | Aucun bug : contrôles conformes | TC-NOM-01, TC-NOM-02, TC-NOM-04, TC-NOM-05, TC-NOM-06 | Cas nominaux automatisés et rejoués à chaque livraison |

## Lecture

- **5 risques critiques** (R01, R02, R03, R04, R05) : tous touchent l'argent ou la possibilité réelle de livrer ; chacun s'est confirmé par un bug reproductible.
- Les risques R09 (accès non autorisé) et R10 (parcours nominal) ont un impact maximal mais une probabilité faible : les 8 cas associés passent, les contrôles existants sont à protéger par des tests de non-régression.
- Cette campagne est **ciblée** (24 cas) : les risques non listés ici (RGPD, performance, compatibilité navigateurs, installation Docker, favoris, avis, administration des statuts) ne sont pas évalués dans ce dépôt.

## Règle d'ordonnancement

1. Score ≥ 16 : exécuté en premier, sur le web **et** l'API, avec cas limites.
2. Score 10 à 15 : exécuté ensuite (nominal, limite, erreur).
3. Score < 10 : un cas nominal et un cas d'erreur.
