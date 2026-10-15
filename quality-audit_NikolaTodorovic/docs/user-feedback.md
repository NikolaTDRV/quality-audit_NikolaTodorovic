# Tests utilisateurs — QuickOrder V3.1

Objectif : compléter les tests techniques par le point de vue d'utilisateurs qui ne connaissent pas l'application, pour repérer les difficultés d'usage que les cas de test n'expriment pas.

> **Transparence sur la méthode.** Cette section a été produite dans un cadre d'exercice, sans recrutement de vraies personnes. Les trois participants sont des **personas** (profils réalistes). Les scénarios ont été **réellement rejoués sur l'application** (captures et traces dans `docs/evidence/`, mêmes parcours que les cas TC-RM-04, TC-RM-05, TC-RM-01 et TC-RM-03) pour établir ce que chaque profil voit. Les **verbatims sont rédigés** pour illustrer une réaction plausible : ce ne sont pas des citations de personnes réelles. Les fréquences (« 3 / 3 ») indiquent combien de personas rencontrent le problème en suivant le scénario, pas une mesure statistique. Ces retours doivent être confirmés avec de vrais utilisateurs avant de décider.

## 1. Protocole

| Élément | Choix |
|---|---|
| Méthode | Parcours de scénarios par personas, rejoués sur l'application réelle |
| Participants | 3 personas (le brief en demande au moins 2) |
| Matériel | Chromium (Playwright), base seedée, compte `alice@example.com` |
| Consigne | Chaque scénario est suivi comme le ferait le persona, sans connaître les anomalies |
| Recueil | Constats réels sur l'application, réactions illustratives |

### Participants (personas)

| ID | Profil | Habitudes |
|---|---|---|
| **T1 — Léa**, 21 ans | Étudiante, commande souvent sur mobile | Va vite, compare les prix, attend un retour immédiat |
| **T2 — Marc**, 54 ans | Cadre commercial, commande rarement en ligne | Lit les messages, craint les erreurs de paiement |
| **T3 — Samira**, 38 ans | Parent de deux enfants, commande en famille | Cherche des restaurants fiables, compare les offres |

### Scénarios

| ID | Scénario | Critère de réussite |
|---|---|---|
| **S1** | « Commandez un plat et payez avec PayPal, puis vérifiez votre commande dans “Mes commandes”. » | Une commande confirmée, retrouvée dans la liste |
| **S2** | « Le restaurant Couscous Atlas annonce une offre : commandez-y 2 Couscous Royal en utilisant le code de l'offre. » | Remise annoncée (15 %) appliquée |
| **S3** | « Il est tard : essayez de commander chez Night Sushi, puis payez en espèces en indiquant que vous avez un billet de 1 € (erreur de frappe). » | Commande refusée (restaurant fermé) ; montant insuffisant refusé |

## 2. Résultats par scénario

| Scénario | T1 Léa | T2 Marc | T3 Samira | Constat réel |
|---|---|---|---|---|
| **S1** | Réussi, mais s'inquiète d'un double paiement | Réussi, hésite à contacter le support | Réussi, hésite à annuler l'une des deux | Deux commandes identiques apparaissent (TC-RM-04) |
| **S2** | Réussi, ne remarque pas l'écart | Remarque 10 % au lieu de 15 % | Remarque l'écart et se sent trompée | Remise de 3,58 € au lieu de 5,37 € (TC-RM-05) |
| **S3** | Commande acceptée alors que « Fermé » est affiché | Idem ; reste surpris du message de succès | Idem | Commande acceptée chez un restaurant fermé (TC-RM-01) ; monnaie négative en espèces (TC-RM-03) |

Les trois personas suivent des parcours identiques sur un défaut déterministe : la fréquence 3 / 3 reflète cela.

## 3. Observations

### O1 — Deux commandes identiques après un paiement PayPal

- **Profil** : T1, T2, T3 · **Contexte** : S1, page « Mes commandes »
- **Problème** : une seule validation, deux commandes de même montant ; l'utilisateur ne sait pas s'il est débité deux fois.
- **Fréquence** : 3 / 3 · **Impact** : critique ; peur d'un double paiement, appel au support.
- **Verbatim (illustratif)** : *« J'en ai deux ! Je n'ai cliqué qu'une fois. J'ai payé deux fois ? »* (T3)
- **Hypothèse d'amélioration** : une seule commande par paiement, numéro de commande affiché sur la confirmation.
- **Priorité** : **Haute** · **Lien** : BUG-001, AM-01

### O2 — L'offre annoncée n'est pas celle appliquée

- **Profil** : T2, T3 (T1 ne l'a pas remarqué) · **Contexte** : S2, fiche Couscous Atlas puis checkout
- **Problème** : l'annonce dit « 15 % », le récapitulatif applique 10 %.
- **Fréquence** : 2 / 3 · **Impact** : perte de confiance, risque de réclamation.
- **Verbatim (illustratif)** : *« C'était écrit quinze pour cent. Là c'est dix. On me ment ? »* (T3)
- **Hypothèse d'amélioration** : générer le texte de l'offre à partir de la valeur du coupon.
- **Priorité** : **Moyenne** · **Lien** : BUG-006, AM-05

### O3 — Commande acceptée chez un restaurant « Fermé »

- **Profil** : T1, T2, T3 · **Contexte** : S3, fiche Night Sushi
- **Problème** : la page indique « Fermé » mais le parcours de commande se termine par une confirmation.
- **Fréquence** : 3 / 3 · **Impact** : élevé ; le client attend une livraison qui n'aura pas lieu.
- **Verbatim (illustratif)** : *« C'est marqué fermé et ça me confirme quand même ? Qui va me livrer ? »* (T2)
- **Hypothèse d'amélioration** : désactiver l'ajout au panier et refuser la commande avec un message clair.
- **Priorité** : **Haute** · **Lien** : BUG-002, AM-02

### O4 — Aucun garde-fou sur le montant en espèces

- **Profil** : T1, T2, T3 · **Contexte** : S3, paiement en espèces
- **Problème** : saisir 1 au lieu de 15 est accepté ; la monnaie à rendre devient négative.
- **Fréquence** : 3 / 3 · **Impact** : élevé ; une faute de frappe passe sans alerte.
- **Verbatim (illustratif)** : *« Je me suis trompée de chiffre et personne ne me le dit. »* (T1)
- **Hypothèse d'amélioration** : refuser un montant inférieur au total, avec le message « Montant insuffisant ».
- **Priorité** : **Haute** · **Lien** : BUG-003, AM-01

### O5 — Petite commande acceptée malgré le minimum affiché

- **Profil** : T1 · **Contexte** : exploration libre à partir de S2 (une portion de frites seule)
- **Problème** : la fiche annonce « Commande minimum : 20 € » mais une commande à 3,50 € est confirmée.
- **Fréquence** : 1 / 3 (observation de T1 hors scénario) · **Impact** : moyen ; règle affichée mais non appliquée.
- **Verbatim (illustratif)** : *« Ils disent vingt euros minimum, j'ai pris pour trois cinquante et ça passe. »* (T1)
- **Hypothèse d'amélioration** : bloquer le checkout et indiquer le montant manquant.
- **Priorité** : **Moyenne** · **Lien** : BUG-005, AM-02

## 4. Priorisation

| Observation | Fréquence | Impact | Priorité | Lien |
|---|---|---|---|---|
| O1 Double commande PayPal | 3 / 3 | Critique | Haute | BUG-001, AM-01 |
| O3 Restaurant fermé commandable | 3 / 3 | Élevé | Haute | BUG-002, AM-02 |
| O4 Espèces insuffisantes | 3 / 3 | Élevé | Haute | BUG-003, AM-01 |
| O2 Offre ATLAS15 | 2 / 3 | Moyen | Moyenne | BUG-006, AM-05 |
| O5 Minimum non appliqué | 1 / 3 | Moyen | Moyenne | BUG-005, AM-02 |

## 5. Enseignements

- Les retours utilisateurs **confirment les anomalies techniques** de la campagne : les défauts critiques sont visibles par un utilisateur sans expertise.
- L'application **promet** (restaurant fermé, minimum, 15 %) **sans faire respecter** : c'est ce décalage qui pèse le plus sur la confiance.
- Aucune observation de confort (libellés, navigation) n'a été produite : ces scénarios étaient volontairement centrés sur les parcours à risque. Des tests avec de vrais utilisateurs devraient élargir ce point.
