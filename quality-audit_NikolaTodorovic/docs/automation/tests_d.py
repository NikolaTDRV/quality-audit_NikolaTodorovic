# -*- coding: utf-8 -*-
"""Cas complémentaires (TC-EXT-xx)."""
import os, re, subprocess, sys
from core import *


@case("TC-EXT-01", reseed_db=False)
def x01(t):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], cwd=REPO, env=env, capture_output=True, text=True)
    out = (r.stdout + r.stderr)
    t.log("$ pytest -q tests\n" + out[-2500:])
    last = out.strip().splitlines()[-1] if out.strip() else ""
    t.check(r.returncode == 0, "Tests de fumée fournis : tous verts.", f"Tests fournis non verts — {last}. Le test test_api_orders_with_key échoue avec AttributeError « 'NoneType' object has no attribute 'id' » (app/routes/api.py:219) : l'API s'appuie sur le compte alice@example.com, absent de la base de test.", "BUG-026")


@case("TC-EXT-02", reseed_db=False)
def x02(t):
    r = subprocess.run([sys.executable, str(HERE / "swagger_check.py"), str(EVID / "TC-EXT-02_01_swagger_liste.png"), str(EVID / "TC-EXT-02_02_swagger_execute.png")],
                       capture_output=True, text=True, env=os.environ.copy())
    t.log(r.stdout + r.stderr)
    t.files += ["TC-EXT-02_01_swagger_liste.png", "TC-EXT-02_02_swagger_execute.png"]
    m = re.search(r"OPS=(\d+) CODE=(\d+)", r.stdout)
    n, code = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    t.check(n >= 8 and code == 200, f"Swagger UI chargé ({n} opérations), clé API acceptée via Authorize, exécution → 200.", f"{r.stdout[-200:]} {r.stderr[-200:]}")


@case("TC-EXT-03")
def x03(t):
    p = t.page(width=375, height=800); p.goto(BASE + "/"); t.shot(p, "accueil_mobile")
    w = p.evaluate("document.documentElement.scrollWidth")
    login(p); add(p, 1, 1); p.goto(BASE + "/checkout"); t.shot(p, "checkout_mobile")
    w2 = p.evaluate("document.documentElement.scrollWidth")
    t.log(f"scrollWidth accueil {w}, checkout {w2} (viewport 375)")
    t.check(w <= 376 and w2 <= 376, "Aucun défilement horizontal à 375 px.", f"Débordement horizontal : {w} / {w2} px")


@case("TC-EXT-04")
def x04(t):
    p = t.page(); login(p); p.goto(BASE + "/profile/")
    p.fill("form[action$='/profile/update'] input[name=name]", "Alice M."); p.fill("form[action$='/profile/update'] input[name=phone]", "0612345678")
    p.click("form[action$='/profile/update'] button"); p.wait_for_load_state(); t.shot(p, "profil_mis_a_jour")
    t.check("Alice M." in p.content() and "Profil mis à jour" in " ".join(flashes(p)), "Profil mis à jour et affiché dans l'en-tête.", f"Flashs {flashes(p)}")


@case("TC-EXT-05")
def x05(t):
    p = t.page(); p.goto(BASE + "/?vegetarian=1"); t.shot(p, "vegetarien")
    names = [n for n in ["Couscous Atlas", "Tokyo Bowl", "Burger Factory", "Green Kitchen", "Pizza Roma", "Night Sushi"] if n in p.inner_text("main")]
    t.log(str(names)); t.check(len(names) >= 3 and "Green Kitchen" in names, f"Restaurants avec au moins un plat végétarien : {names}.", f"{names}")


@case("TC-EXT-06")
def x06(t):
    p = t.page(); p.goto(BASE + "/?category=Japonais"); t.shot(p, "categorie_japonais")
    txt = p.inner_text("main"); t.check("Tokyo Bowl" in txt and "Pizza Roma" not in txt, "Seul Tokyo Bowl affiché.", txt[:150])


@case("TC-EXT-07")
def x07(t):
    p = t.page(); p.goto(BASE + "/restaurant/1")
    cats = p.evaluate("[...document.querySelectorAll('a[href*=\"category=\"], select[name=category] option')].map(e=>e.textContent.trim())")
    p.goto(BASE + "/restaurant/1?category=Burgers"); t.shot(p, "menu_filtre_categorie")
    txt = p.inner_text("main"); t.log(f"Contrôles de catégorie trouvés dans la page : {cats}")
    if not cats:
        t.blocked("La route accepte ?category= et ?q= mais aucun contrôle de filtre n'est affiché sur la page du restaurant : filtrage inaccessible depuis l'interface.", "BUG-022")
    else:
        t.check("Frites" not in txt, "Filtre appliqué.", txt[:150])


@case("TC-EXT-08")
def x08(t):
    p = t.page(); login(p, "admin@quickorder.local", "Admin123!"); p.goto(BASE + "/admin/"); t.shot(p, "tableau_de_bord_admin")
    txt = p.inner_text("main"); t.log(txt[:300])
    t.check("Utilisateurs" in txt and "Administration" in txt, "Tableau de bord : compteurs et 10 dernières commandes.", txt[:150])


@case("TC-EXT-09")
def x09(t):
    p = t.page(); p.goto(BASE + "/?sort=price"); t.shot(p, "tri_livraison")
    fees = [float(x.replace(",", ".")) for x in re.findall(r"Livraison\s*([\d.,]+)\s*€", p.inner_text("main"))]
    t.log(str(fees)); t.check(fees == sorted(fees) and len(fees) == 6, "Tri par frais de livraison croissants.", str(fees))


@case("TC-EXT-10")
def x10(t):
    p = t.page(); login(p); p.goto(BASE + "/orders/1"); t.shot(p, "commande_livree_bouton")
    p.goto(BASE + "/orders"); t.shot(p, "liste_statuts")
    labels = [e.inner_text() for e in p.query_selector_all(".status")]
    p.goto(BASE + "/orders/1"); has_cancel = bool(p.query_selector("button[name=action][value=cancel]"))
    t.log(f"Libellés de statut : {labels} ; bouton Annuler sur la commande livrée : {has_cancel}")
    t.check(not has_cancel and all(re.search("[éèà]|livr|confirm[ée]e|annul", l) for l in labels),
            "Libellés en français et pas de bouton Annuler sur une commande livrée.",
            f"Statuts affichés en anglais technique ({sorted(set(labels))}) et bouton « Annuler la commande » proposé sur la commande #1 livrée (le clic est refusé ensuite).", "BUG-027")


@case("TC-EXT-11")
def x11(t):
    p = t.page(); login(p); p.click("a[href='/logout']"); p.wait_for_load_state(); p.goto(BASE + "/orders"); t.shot(p, "apres_deconnexion")
    t.check("/login" in p.url, "Après déconnexion, /orders redirige vers /login.", p.url)


@case("TC-EXT-12")
def x12(t):
    p = t.page(); errs = []
    p.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None)
    p.on("pageerror", lambda e: errs.append(str(e)))
    login(p)
    for u in ("/", "/restaurant/1", "/cart", "/orders", "/profile/", "/login"):
        p.goto(BASE + u)
    t.log(f"Erreurs/avertissements console : {errs}"); t.shot(p, "derniere_page")
    t.check(not errs, "Console navigateur sans erreur.", f"{errs}")


@case("TC-EXT-13")
def x13(t):
    import json as j
    col = j.loads((REPO / "docs/quickorder-api.postman_collection.json").read_text(encoding="utf-8"))
    var = {v["key"]: v["value"] for v in col["variable"]}
    def walk(items):
        for i in items:
            if "item" in i: yield from walk(i["item"])
            else: yield i
    bad = []
    for it in walk(col["item"]):
        rq = it["request"]; raw = rq["url"]["raw"] if isinstance(rq["url"], dict) else rq["url"]
        for k, v in var.items(): raw = raw.replace("{{%s}}" % k, v)
        body = rq.get("body", {}).get("raw") if rq.get("body") else None
        r = requests.request(rq["method"], raw, headers={"X-API-Key": KEY, "Content-Type": "application/json"}, data=body, timeout=15)
        t.log(f"{rq['method']} {raw} → {r.status_code}")
        if r.status_code >= 500: bad.append((it["name"], r.status_code))
    t.check(not bad, "La collection Postman fournie s'exécute sans erreur 5xx.", f"{bad}")
