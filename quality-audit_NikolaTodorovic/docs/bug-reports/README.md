# Index des bug reports

8 anomalies documentées. Sévérité : Critique (perte financière ou blocage), Majeure (règle métier, sécurité ou parcours dégradé), Mineure (confort, cohérence).
Priorité : P1 = à corriger avant toute mise en production · P2 = avant ou juste après la mise en production · P3 = backlog.

| ID | Titre | Sévérité | Priorité | Canal | Cas liés |
|---|---|---|---|---|---|
| [BUG-001](BUG-001.md) | Le paiement PayPal crée deux commandes identiques (web et API) | Critique | P1 | UI + API | TC-RM-04 |
| [BUG-002](BUG-002.md) | Un restaurant fermé peut recevoir des commandes (web et API) | Majeure | P1 | UI + API | TC-RM-01 |
| [BUG-003](BUG-003.md) | Le paiement en espèces accepte un montant inférieur au total (monnaie négative) | Majeure | P1 | UI + API | TC-RM-03 |
| [BUG-004](BUG-004.md) | Contrôles de stock défaillants : quantité supérieure au stock et produit en rupture commandables | Majeure | P1 | UI + API | TC-LIM-06 |
| [BUG-005](BUG-005.md) | Le minimum de commande du restaurant n'est pas appliqué (web et API) | Majeure | P2 | UI + API | TC-RM-02 |
| [BUG-006](BUG-006.md) | ATLAS15 est annoncé à 15 % mais appliqué à 10 % | Majeure | P2 | UI + API | TC-RM-05 |
| [BUG-007](BUG-007.md) | API : des entrées mal formées provoquent des erreurs 500 (traceback exposé) | Majeure | P2 | API | TC-ERR-05 |
| [BUG-008](BUG-008.md) | Redirection ouverte après connexion (paramètre `next`) | Majeure | P2 | UI | TC-ERR-06 |
