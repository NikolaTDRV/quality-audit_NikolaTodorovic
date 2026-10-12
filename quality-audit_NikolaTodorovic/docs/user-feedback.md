# Tests utilisateurs — QuickOrder V3.1

Objectif : compléter les tests techniques par le point de vue d'utilisateurs qui ne connaissent pas l'application, pour repérer les difficultés d'usage que les cas de test n'expriment pas.

> **Transparence sur la méthode.** Cette section a été produite dans un cadre d'exercice, sans recrutement de vraies personnes. Les trois participants sont des **personas** (profils réalistes) ; les scénarios ont été **réellement rejoués sur l'application** (captures dans `docs/evidence/`) pour établir ce que chaque persona voit et rencontre. Les **verbatims sont rédigés** pour illustrer la réaction plausible d'un profil, ce ne sont pas des citations de personnes réelles. Les fréquences (« 3 / 3 ») indiquent combien de personas rencontrent le problème en suivant le scénario, pas une mesure statistique. Avant de s'appuyer sur ces retours pour décider, il faut les confirmer avec de vrais utilisateurs.

## 1. Protocole

| Élément | Choix |
|---|---|
| Méthode | Parcours de scénarios par personas, rejoués sur l'application réelle ; réactions formulées « à voix haute » par le rédacteur à partir de ce que le profil verrait |
| Participants | 3 personas (le brief en demande 2 au minimum) |
| Durée | Environ 20 minutes de rejeu par scénario |
| Matériel | Chromium (Playwright), application sur base seedée, compte `alice@example.com` pour les parcours connectés |
| Consigne | Aucune connaissance préalable des anomalies : chaque scénario est suivi comme le ferait le persona |
| Recueil | Constats réels sur l'application, réactions illustratives (verbatims fictifs), réussite par scénario |

### Participants (personas)

| ID | Profil | Habitudes |
|---|---|---|
| **T1 — Léa**, 21 ans | Étudiante en gestion, utilisatrice quotidienne d'applications de livraison sur mobile | Va vite, compare les prix, attend un retour immédiat |
| **T2 — Marc**, 54 ans | Cadre commercial, utilise surtout l'ordinateur, commande rarement en ligne | Lit les messages, craint les erreurs de paiement |
| **T3 — Samira**, 38 ans | Parent de deux enfants, commande des repas en famille 2 à 3 fois par mois | Cherche des restaurants fiables, regarde les avis et les favoris |

### Scénarios

| ID | Scénario | Critère de réussite |
|---|---|---|
| **S1** | « Vous voulez un repas avec une livraison à 2 € maximum. Choisissez un restaurant, ajoutez un plat au panier et utilisez le code WELCOME10. » | Restaurant à ≤ 2 € choisi, plat au panier, remise visible au checkout |
| **S2** | « Payez avec PayPal, vérifiez votre commande dans « Mes commandes » puis annulez-la. » | Commande confirmée, retrouvée, annulée |
| **S3** | « Ajoutez une adresse de travail et mettez-la par défaut, supprimez l'ancienne adresse, ajoutez Pizza Roma en favori et lisez les avis de ce restaurant. » | Les quatre actions réalisées |

### Résultats par scénario (constats réels, réactions des personas)

| Scénario | T1 Léa | T2 Marc | T3 Samira | Constat |
|---|---|---|---|---|
| **S1** | Réussi, après un doute sur le filtre | Réussi avec aide (a quitté le filtre, trié à la main) | Réussi avec une erreur (restaurant à 2,99 € choisi par confusion) | Le filtre « Livraison max » trompe les trois personas |
| **S2** | Réussi ; s'inquiète d'un double paiement | Réussi ; contacte « le support » dans sa tête avant de poursuivre | Réussi ; hésite à annuler les deux commandes | Deux commandes identiques apparaissent pour les trois personas |
| **S3** | **Échec partiel** : adresse ajoutée, reste impossible | **Échec partiel** : adresse ajoutée, reste impossible | **Échec partiel** : adresse ajoutée, reste impossible | Suppression d'adresse, favori et avis sont introuvables pour tous |

## 2. Observations

Chaque observation précise le profil concerné, le contexte, le problème, sa fréquence (sur 3 personas), l'impact, un verbatim, une hypothèse d'amélioration et une priorité (Haute / Moyenne / Basse). La colonne « Lien » rapproche chaque retour d'une anomalie technique ou d'une amélioration.

### O1 — Le filtre « Livraison max » renvoie l'inverse de ce qui est demandé

- **Profil** : T1, T2, T3 · **Contexte** : S1, accueil, sélection de « ≤ 2,00 € »
- **Problème** : après avoir demandé 2 € maximum, la liste affiche des restaurants à 2,49 €, 2,99 € et 3,49 € et fait disparaître Green Kitchen à 1,99 €.
- **Fréquence** : 3 / 3 · **Impact** : bloquant pour l'objectif du scénario ; perte de confiance dans les filtres.
- **Verbatim** : *« J'ai demandé deux euros maximum et je vois du trois euros quarante-neuf. Le site se trompe ou je n'ai pas compris ? »* (T1)
- **Hypothèse d'amélioration** : corriger le filtre, afficher le nombre de résultats et un bandeau « Filtres actifs » modifiable.
- **Priorité** : **Haute** · **Lien** : BUG-006, AM-09

### O2 — Deux commandes identiques après un paiement PayPal

- **Profil** : T1, T2, T3 · **Contexte** : S2, « Mes commandes »
- **Problème** : une seule validation, deux commandes de même montant dans la liste ; l'utilisateur ne sait pas s'il a été débité deux fois.
- **Fréquence** : 3 / 3 · **Impact** : critique ; peur d'un double paiement, appel au support.
- **Verbatim** : *« Là j'en ai deux ! Je n'ai cliqué qu'une fois. J'ai payé deux fois ? »* (T3)
- **Hypothèse d'amélioration** : une seule commande par paiement, message de confirmation explicite avec numéro de commande.
- **Priorité** : **Haute** · **Lien** : BUG-001, AM-01

### O3 — Les statuts sont affichés sous forme de codes techniques

- **Profil** : T2, T3 (T1 les a ignorés) · **Contexte** : S2, détail et liste des commandes
- **Problème** : « confirmed », « out_for_delivery », « paid · paypal » s'affichent tels quels, alors que le reste de l'interface est en français.
- **Fréquence** : 2 / 3 · **Impact** : gênant ; la compréhension de l'état de la commande est dégradée.
- **Verbatim** : *« « Confirmed », ça veut dire que c'est accepté ou que c'est parti ? »* (T2)
- **Hypothèse d'amélioration** : libellés français (« Confirmée », « En préparation », « En livraison », « Livrée », « Annulée ») avec une frise de progression.
- **Priorité** : **Moyenne** · **Lien** : AM-07, AM-08

### O4 — Les libellés de paiement sont déroutants

- **Profil** : T2, T3 · **Contexte** : S2, liste « Mode de paiement »
- **Problème** : « Carte bancaire — succès » et « PayPal — succès » semblent annoncer un résultat plutôt qu'un choix.
- **Fréquence** : 2 / 3 · **Impact** : gênant ; hésitation avant de payer.
- **Verbatim** : *« « Succès » ? Je n'ai encore rien payé. »* (T2)
- **Hypothèse d'amélioration** : libellés « Carte bancaire », « PayPal », « Espèces à la livraison », avec la mention « paiement simulé » en bandeau.
- **Priorité** : **Moyenne** · **Lien** : AM-08

### O5 — Le bouton « Appliquer » réinitialise les choix du formulaire

- **Profil** : T1, T3 · **Contexte** : S1, checkout, application du coupon
- **Problème** : après avoir saisi le coupon, l'adresse revient à la valeur par défaut, la note disparaît et le paiement redevient « Carte bancaire ».
- **Fréquence** : 2 / 3 · **Impact** : gênant ; risque de livraison à la mauvaise adresse ou de mauvais mode de paiement.
- **Verbatim** : *« J'avais choisi mon adresse du travail et elle est repartie sur l'autre. Heureusement que je regarde. »* (T3)
- **Hypothèse d'amélioration** : conserver les valeurs saisies, ou appliquer le coupon sans recharger la page.
- **Priorité** : **Moyenne** · **Lien** : BUG-020, AM-08

### O6 — Pas de retour visible sur le contenu du panier

- **Profil** : T1, T2, T3 · **Contexte** : S1, ajout d'un produit depuis le menu
- **Problème** : l'ajout recharge la page ; le message de confirmation est en haut, hors de vue si l'on est descendu dans le menu ; aucun compteur sur « Panier » dans la navigation.
- **Fréquence** : 3 / 3 · **Impact** : gênant ; doute (« est-ce ajouté ? ») et ajouts en double.
- **Verbatim** : *« J'ai cliqué et il ne s'est rien passé, alors j'ai recliqué. »* (T2)
- **Hypothèse d'amélioration** : compteur de panier dans l'en-tête, message près du bouton ou « toast » visible.
- **Priorité** : **Moyenne** · **Lien** : AM-08

### O7 — Impossible de retirer un produit du panier autrement qu'en saisissant 0

- **Profil** : T1, T2 · **Contexte** : S1, page « Votre panier »
- **Problème** : aucun bouton « Retirer » ; les personas cherchent une icône corbeille, finissent par taper 0 ou vider tout le panier.
- **Fréquence** : 2 / 3 · **Impact** : gênant.
- **Verbatim** : *« Où est le bouton supprimer ? Ah, il faut mettre zéro… »* (T1)
- **Hypothèse d'amélioration** : bouton « Retirer » par ligne, bouton « − / + » sur les quantités.
- **Priorité** : **Moyenne** · **Lien** : BUG-022, AM-08

### O8 — Favoris, suppression d'adresse et avis sont introuvables

- **Profil** : T1, T2, T3 · **Contexte** : S3
- **Problème** : aucun bouton Favori, aucune action de suppression ou de modification d'une adresse, aucune liste d'avis sur la fiche du restaurant (alors qu'un formulaire permet d'en publier).
- **Fréquence** : 3 / 3 · **Impact** : bloquant pour S3 ; perception d'une application inachevée. T3 attend les avis avant de choisir un restaurant.
- **Verbatim** : *« Je veux voir ce que les gens en pensent avant de commander, mais je ne vois que « laisser un avis ». »* (T3)
- **Hypothèse d'amélioration** : afficher les avis et la note moyenne, ajouter le cœur Favori sur la carte et la fiche, compléter la gestion d'adresses.
- **Priorité** : **Haute** pour les avis et les adresses, **Basse** pour les favoris · **Lien** : BUG-018, BUG-022, AM-10

### O9 — La possibilité de commander chez un restaurant fermé surprend

- **Profil** : T1, T2 · **Contexte** : exploration libre après S1
- **Problème** : le badge FERMÉ est présent, mais le bouton « Ajouter » et le paiement fonctionnent quand même.
- **Fréquence** : 2 / 3 · **Impact** : critique pour le métier ; message contradictoire pour le client.
- **Verbatim** : *« C'est écrit fermé et ça me laisse commander ? Je serai livrée quand, alors ? »* (T1)
- **Hypothèse d'amélioration** : griser la fiche, désactiver « Ajouter » et expliquer l'horaire d'ouverture.
- **Priorité** : **Haute** · **Lien** : BUG-002, AM-02

### O10 — Les mentions « HORS STOCK » et « Stock N » créent des doutes

- **Profil** : T1, T2, T3 · **Contexte** : S1, menu d'un restaurant
- **Problème** : un plat marqué HORS STOCK peut tout de même être ajouté ; le nombre exact de stock restant (« Stock 2 ») est montré aux clients ; un stock négatif a été observé après une commande.
- **Fréquence** : 3 / 3 · **Impact** : gênant à critique selon le cas ; manque de crédibilité.
- **Verbatim** : *« Pourquoi je vois le stock ? Et si c'est indisponible, pourquoi je peux le mettre dans mon panier ? »* (T2)
- **Hypothèse d'amélioration** : bouton désactivé en rupture, message « Plus que 2 » seulement sous un seuil, retrait du chiffre exact sinon.
- **Priorité** : **Haute** · **Lien** : BUG-004, AM-02

### O11 — L'heure de la commande est décalée

- **Profil** : T2, T3 · **Contexte** : S2, « Mes commandes »
- **Problème** : l'heure affichée a deux heures de retard par rapport à l'horloge de Paris (19:14 affiché pour 21:14, mesuré le 12/10/2026).
- **Fréquence** : 2 / 3 · **Impact** : mineur ; perte de confiance dans la fiabilité des informations.
- **Verbatim** : *« Il est 21 h et c'est écrit 19 h : ma commande date d'avant-hier ? »* (T2)
- **Hypothèse d'amélioration** : afficher l'heure locale ou le fuseau.
- **Priorité** : **Basse** · **Lien** : BUG-021, AM-12

### O12 — La recherche ne comprend pas le type de cuisine

- **Profil** : T1, T3 · **Contexte** : exploration libre
- **Problème** : « japonais » ou « marocain » ne renvoie rien alors que ces cuisines existent.
- **Fréquence** : 2 / 3 · **Impact** : gênant.
- **Verbatim** : *« Je tape ce que j'ai envie de manger, pas le nom du restaurant. »* (T1)
- **Hypothèse d'amélioration** : rechercher aussi dans la cuisine et la description, suggérer des catégories.
- **Priorité** : **Moyenne** · **Lien** : BUG-013, AM-09

## 3. Synthèse et priorisation

| Rang | Retour | Fréquence | Impact | Priorité | Lien |
|---|---|---|---|---|---|
| 1 | O2 Doublon PayPal | 3/3 | Critique | Haute | BUG-001, AM-01 |
| 2 | O1 Filtre livraison inversé | 3/3 | Bloquant | Haute | BUG-006, AM-09 |
| 3 | O9 Restaurant fermé commandable | 2/3 | Critique | Haute | BUG-002, AM-02 |
| 4 | O10 Stock incohérent | 3/3 | Gênant à critique | Haute | BUG-004, AM-02 |
| 5 | O8 Avis, adresses, favoris | 3/3 | Bloquant (S3) | Haute / Basse | BUG-018, BUG-022, AM-10 |
| 6 | O5 « Appliquer » réinitialise le formulaire | 2/3 | Gênant | Moyenne | BUG-020, AM-08 |
| 7 | O6 Pas de compteur panier | 3/3 | Gênant | Moyenne | AM-08 |
| 8 | O7 Pas de bouton « Retirer » | 2/3 | Gênant | Moyenne | BUG-022, AM-08 |
| 9 | O3 Statuts bruts | 2/3 | Gênant | Moyenne | AM-07 |
| 10 | O4 Libellés de paiement | 2/3 | Gênant | Moyenne | AM-08 |
| 11 | O12 Recherche | 2/3 | Gênant | Moyenne | BUG-013, AM-09 |
| 12 | O11 Heure décalée | 2/3 | Mineur | Basse | BUG-021, AM-12 |

**Enseignement principal** : les trois retours les plus graves (O1, O2, O10) sont **déjà des anomalies techniques** (BUG-006, BUG-001, BUG-004) : un utilisateur les rencontre sans effort, sans chercher à « casser » l'application. Ils confirment les priorités du rapport d'exécution.

## 4. Limites

- **Pas de vrais participants** : personas et verbatims sont fictifs (voir l'encadré du début). Les constats techniques sous-jacents (filtre inversé, deux commandes PayPal, statuts bruts, formulaire réinitialisé, absence de bouton « Retirer », heure décalée, recherche limitée au nom) sont, eux, **vérifiés sur l'application** : voir les cas TC-LIM-07, TC-RM-09, TC-EXT-10, TC-RM-23, TC-EXT-18, TC-RM-24 et TC-EXT-14.
- Les fréquences indiquent une tendance du scénario, pas un taux mesuré. Les hypothèses d'amélioration sont à valider par de vrais tests (observation de 5 personnes minimum) après correction.
