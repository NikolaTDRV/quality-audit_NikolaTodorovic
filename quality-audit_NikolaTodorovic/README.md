# Audit qualité de QuickOrder V3.1 (campagne ciblée : 24 cas, 8 bugs)

Audit qualité réalisé avant la mise en production de **QuickOrder**, plateforme de livraison de repas (Flask, SQLite, API REST). Mission : évaluer la qualité, prouver les anomalies et recommander **Go / No-Go**. Le code source de QuickOrder n'a **pas été modifié**.

Les **24 cas** ont tous été **exécutés** sur l'application réelle (interface pilotée dans Chromium, requêtes HTTP sur l'API). Les **8 anomalies** sont **reproductibles** : le script `docs/automation/reproduce_bugs.sh` les rejoue en ligne de commande et affiche `REPRODUIT` (8 / 8).

## Verdict : **NO-GO**

| Indicateur | Valeur |
|---|---|
| Cas de test | **24** : 6 nominaux, 6 limites, 6 erreurs, 6 règles métier |
| Résultats | **16 Pass · 8 Fail** |
| Taux de réussite | 66,7 % global · 61,1 % sur les cas P1 |
| Anomalies | **8** : 1 Critique, 7 Majeures (4 en P1, 4 en P2) |
| Retours utilisateurs | 3 personas, 3 scénarios, 5 observations (voir l'encadré de transparence de `docs/user-feedback.md`) |
| Plan d'amélioration | 7 améliorations priorisées, feuille de route en 3 sprints |

Anomalies : paiement PayPal qui crée **deux commandes** (BUG-001, Critique) · commande chez un **restaurant fermé** (BUG-002) · paiement en **espèces** insuffisant accepté (BUG-003) · **stock** dépassé ou produit en rupture commandable (BUG-004) · **minimum de commande** ignoré (BUG-005) · **ATLAS15** annoncé à 15 % mais appliqué à 10 % (BUG-006) · **erreurs 500** et débogueur exposé sur l'API (BUG-007) · **redirection ouverte** après connexion (BUG-008).

## Organisation du dépôt

```text
quality-audit2/
├── README.md
└── docs/
    ├── test-strategy.md      Stratégie : périmètre, parcours critiques, approche, critères Go / No-Go
    ├── risk-matrix.md        Matrice probabilité × impact (10 risques)
    ├── test-cases.xlsx       24 cas, résultats réels, bugs, synthèse calculée par formules
    ├── execution-report.md   Chiffres, analyse, décision Go / No-Go, plan de revalidation
    ├── bug-reports/          8 fiches BUG-001 à BUG-008 (preuves intégrées) et leur index
    ├── user-feedback.md      Tests utilisateurs (personas) : scénarios, observations, priorisation
    ├── improvement-plan.md   7 améliorations (MoSCoW, effort, critères d'acceptation), feuille de route
    ├── evidence/             Captures PNG, traces requête/réponse, vidéo du double paiement PayPal,
    │                         reproduction-curl.txt (sortie du rejeu des 8 bugs)
    └── automation/           run_campaign.py (24 cas), reproduce_bugs.sh (8 bugs), results.json
```

## Par où commencer

1. [`docs/execution-report.md`](docs/execution-report.md) : la décision et les chiffres.
2. [`docs/bug-reports/README.md`](docs/bug-reports/README.md) : les 8 fiches (titre, contexte, préconditions, étapes, résultat attendu, résultat obtenu, preuve, sévérité, priorité).
3. [`docs/test-cases.xlsx`](docs/test-cases.xlsx) : les 24 cas (filtrables par statut, priorité, catégorie ou bug).
4. [`docs/improvement-plan.md`](docs/improvement-plan.md) : la suite à donner.

Traçabilité : **risque (R-xx) → cas de test (TC-…) → anomalie (BUG-…) → amélioration (AM-…)**.

## Rejouer

```bash
# 1. Installer et lancer QuickOrder (voir docs/INSTALLATION.md du projet)
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python seed.py        # ⚠ réinitialise la base
python run.py         # http://127.0.0.1:5000

# 2a. Rejouer les 8 bugs en ligne de commande (base fraîchement seedée, curl requis)
bash docs/automation/reproduce_bugs.sh http://127.0.0.1:5000   # affiche REPRODUIT / NON REPRODUIT

# 2b. Rejouer les 24 cas (autre terminal)
python -m pip install playwright requests && python -m playwright install chromium
export QO_REPO=/chemin/vers/quickorder-qa-project       # seed.py est relancé avant chaque cas
export DATABASE_URL=sqlite:////chemin/vers/la/base.db   # la MÊME base que celle du serveur
cd docs/automation && python run_campaign.py            # ou : python run_campaign.py TC-RM-04 TC-LIM-06
```

`reproduce_bugs.sh` modifie la base (commandes, stock) : relancer `python seed.py` entre deux exécutions.

Comptes : `alice@example.com` / `Password123!` · `bob@example.com` / `Password123!` · `admin@quickorder.local` / `Admin123!` · clé API : `quickorder-demo-key`.

## Limites à connaître

- **Campagne ciblée** : 24 cas ; favoris, avis, profil, administration des statuts et installation Docker ne sont pas évalués ici.
- **Retours utilisateurs** : personas et verbatims illustratifs, à confirmer avec de vrais utilisateurs.
- Un seul navigateur (Chromium) ; pas de test de charge.

## Conventions

- **Sévérité** : Critique (perte financière ou blocage) · Majeure (règle métier, sécurité, parcours dégradé) · Mineure (confort).
- **Priorité** : P1 (avant toute mise en production) · P2 (avant, ou juste après si le risque est accepté) · P3 (backlog).
- **Statuts** : Pass · Fail (écart constaté, bug lié).
