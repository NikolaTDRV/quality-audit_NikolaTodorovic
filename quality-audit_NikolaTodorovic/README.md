# Audit qualité de QuickOrder V3.1

Audit qualité réalisé avant la mise en production de **QuickOrder**, plateforme de livraison de repas (Flask, SQLite, API REST). Mission : évaluer la qualité de l'application existante, prouver les anomalies et recommander **Go / No-Go**. Le code source de QuickOrder n'a **pas été modifié** pendant la campagne.

Tous les cas ont été **exécutés** sur l'application réelle (interface pilotée dans Chromium, requêtes HTTP sur l'API) ; les résultats, captures, traces de requêtes et la vidéo du double paiement PayPal sont dans `docs/evidence/`.

## Verdict : **NO-GO**

| Indicateur | Valeur |
|---|---|
| Cas de test | **99** (16 nominaux, 13 limites, 23 erreurs, 25 règles métier, 22 complémentaires) |
| Résultats | **48 Pass · 46 Fail · 4 Blocked · 1 Skipped** |
| Taux de réussite (Pass / exécutés) | 51,1 % global · 48,5 % sur les cas P1 |
| Anomalies | **29** : 1 Critique, 15 Majeures, 13 Mineures (5 en P1, 11 en P2, 13 en P3) |
| Retours utilisateurs | 3 personas × 3 scénarios, 12 observations (voir l'encadré de transparence de `docs/user-feedback.md`) |
| Plan d'amélioration | 13 améliorations priorisées, feuille de route en 4 sprints |

Problèmes les plus graves : paiement PayPal qui crée **deux commandes** (BUG-001) ; commandes possibles chez un **restaurant fermé**, en **rupture de stock** ou **sous le minimum** (BUG-002, 004, 005) ; paiement en **espèces** accepté pour 1 € sur 14,89 € (BUG-003) ; **ATLAS15** annoncé à 15 % et appliqué à 10 % (BUG-007) ; **redirection ouverte** et configuration par défaut non sécurisée (BUG-015, 023) ; **erreurs 500** de l'API sur entrées mal formées (BUG-010) ; installation **Docker** inutilisable sous Linux/macOS (BUG-025). Détail et conditions de levée dans [`docs/execution-report.md`](docs/execution-report.md).

## Organisation du dépôt

```text
quality-audit/
├── README.md
└── docs/
    ├── test-strategy.md        Stratégie : périmètre, parcours critiques, types de tests, critères Go / No-Go
    ├── risk-matrix.md          Matrice probabilité × impact (20 risques) et règle de priorisation
    ├── test-cases.xlsx         99 cas de test, résultats réels, bugs et synthèse calculée par formules
    ├── execution-report.md     Chiffres de la campagne, analyse, décision Go / No-Go, plan de revalidation
    ├── bug-reports/            29 fiches BUG-001 à BUG-029 (preuves intégrées) et leur index (README.md)
    ├── user-feedback.md        Tests utilisateurs (personas) : scénarios, observations, priorisation
    ├── improvement-plan.md     13 améliorations (MoSCoW, effort, critères d'acceptation) et feuille de route
    ├── evidence/               Captures PNG, traces requête/réponse (.txt), vidéo du doublon PayPal
    └── automation/             Scripts Playwright + requests qui ont produit les résultats (results.json)
```

## Par où commencer

1. [`docs/execution-report.md`](docs/execution-report.md) : la décision et les chiffres.
2. [`docs/bug-reports/README.md`](docs/bug-reports/README.md) : l'index des anomalies, de la plus urgente à la moins urgente.
3. [`docs/test-cases.xlsx`](docs/test-cases.xlsx) : le détail des cas (onglet « Cas de test », filtrable par statut, priorité, catégorie ou bug ; colonne « Preuves » vers `docs/evidence/`).
4. [`docs/improvement-plan.md`](docs/improvement-plan.md) : la suite à donner.

Traçabilité : **risque (R-xx) → cas de test (TC-…) → anomalie (BUG-…) → amélioration (AM-…)**.

## Rejouer la campagne

```bash
# 1. Installer et lancer QuickOrder (voir docs/INSTALLATION.md du projet)
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python seed.py        # ⚠ réinitialise la base
python run.py         # http://127.0.0.1:5000

# 2. Dans un autre terminal : installer les outils de test et lancer la campagne
python -m pip install playwright requests && python -m playwright install chromium
export QO_REPO=/chemin/vers/quickorder-qa-project     # dossier du projet (seed.py est relancé avant chaque cas)
export DATABASE_URL=sqlite:////chemin/vers/la/base.db # la MÊME base que celle du serveur
cd docs/automation && python run_campaign.py          # tous les cas ; ou : python run_campaign.py TC-RM-09 TC-ERR-16
```

Chaque cas réinitialise la base (`seed.py`), exécute ses étapes, enregistre les preuves dans `docs/evidence/` et écrit `docs/automation/results.json`. `swagger_check.py` charge Swagger UI (qui récupère `swagger-ui-dist` sur un CDN : accès Internet nécessaire pour TC-EXT-02).

Comptes : `alice@example.com` / `Password123!` · `bob@example.com` / `Password123!` · `admin@quickorder.local` / `Admin123!` · clé API Swagger : `quickorder-demo-key`.

## Limites à connaître

- **Docker Compose n'a pas été lancé** (pas de démon Docker dans l'environnement de test) : TC-ENV-01 / BUG-025 reposent sur l'exécution directe de `docker-entrypoint.sh` (« Permission denied ») et sur le mode Git du fichier (100644).
- **Retours utilisateurs** : personas et verbatims illustratifs, à confirmer avec de vrais utilisateurs.
- Un seul moteur de navigateur (Chromium) ; mobile émulé à 375 px.

## Conventions

- **Sévérité** : Critique (perte financière ou blocage) · Majeure (règle métier, sécurité, parcours dégradé) · Mineure (confort, cohérence).
- **Priorité** : P1 (avant toute mise en production) · P2 (avant, ou juste après si le risque est accepté) · P3 (backlog).
- **Statuts de test** : Pass · Fail · Blocked (impossible à exécuter, cause tracée) · Skipped (règle non tranchée, motif tracé).
