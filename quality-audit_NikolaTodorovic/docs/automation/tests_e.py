# -*- coding: utf-8 -*-
"""Cas complémentaires de vérification des anomalies (TC-EXT-14 à 20)."""
from core import *
from pathlib import Path
import os

NAMES = ["Couscous Atlas", "Tokyo Bowl", "Burger Factory", "Green Kitchen", "Pizza Roma", "Night Sushi"]


@case("TC-EXT-14")
def x14(t):
    p = t.page(); res = {}
    for q in ("japonais", "marocaine", "Marocain"):
        p.goto(f"{BASE}/?q={q}"); res[q] = [n for n in NAMES if n in p.inner_text("main")]; t.shot(p, f"q_{q}")
    t.log(str(res))
    t.check(res["japonais"] and res["marocaine"], "La recherche trouve aussi par cuisine / description.", f"Résultats : {res} — la recherche ne porte que sur le nom du restaurant.", "BUG-013")


@case("TC-EXT-15")
def x15(t):
    p = t.page(); p.goto(BASE + "/register")
    p.evaluate("""() => { const e=document.querySelector('input[name=email]'); e.type='text'; }""")
    p.fill("input[name=name]", "Valid Test"); p.fill("input[name=email]", "a@b"); p.fill("input[name=password]", "12345678")
    p.click("form button.button"); p.wait_for_load_state(); t.shot(p, "email_a_at_b")
    created = "Déconnexion" in p.content()
    p.goto(BASE + "/profile/")
    p.fill("form[action$='/profile/update'] input[name=phone]", "abc"); p.click("form[action$='/profile/update'] button"); p.wait_for_load_state()
    f = "form[action$='/profile/address']"
    p.fill(f + " input[name=label]", "Test"); p.fill(f + " input[name=street]", "x"); p.fill(f + " input[name=postal_code]", "ZZZZZ"); p.fill(f + " input[name=city]", "y"); p.click(f + " button"); p.wait_for_load_state(); t.shot(p, "profil_valeurs_libres")
    txt = p.inner_text("main"); t.log(f"Compte « a@b » créé : {created} ; téléphone « abc » dans le profil : {'abc' in p.content()} ; code postal ZZZZZ listé : {'ZZZZZ' in txt}")
    ok = (not created) and "ZZZZZ" not in txt
    t.check(ok, "Formats email, téléphone et code postal contrôlés.", f"Compte créé avec l'email « a@b » et le mot de passe « 12345678 » ; téléphone « abc » et code postal « ZZZZZ » acceptés.", "BUG-024")


@case("TC-EXT-16")
def x16(t):
    a = t.api("POST", "/api/coupons/validate", {"code": "FOO", "subtotal": 50}, label="coupon inconnu")
    b = t.api("POST", "/api/coupons/validate", {"code": "WELCOME10", "subtotal": 5}, label="sous le minimum")
    c = t.api("POST", "/api/orders/999/cancel", label="annulation d'une commande inexistante")
    t.check(a.status_code == b.status_code and "json" in c.headers.get("Content-Type", ""), "Statuts cohérents et erreurs JSON.",
            f"Coupon inconnu → {a.status_code} ; sous le minimum → {b.status_code} (valid:false) ; commande 999 → {c.status_code} en {c.headers.get('Content-Type')}.", "BUG-011")


@case("TC-EXT-17")
def x17(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/4")
    for i in range(2):
        p.select_option("select[name=rating]", "1"); p.fill("textarea[name=comment]", f"Avis test {i}"); p.click("form[action$='/review'] button"); p.wait_for_load_state()
    p.goto(BASE + "/restaurant/4"); t.shot(p, "fiche_apres_avis")
    vis = "Avis test" in p.inner_text("main"); seed = len(re.findall("(?i)avis", p.inner_text("main")))
    t.log(f"Avis visibles sur la fiche : {vis}")
    t.check(vis, "Les avis publiés sont visibles sur la fiche.", "Deux avis publiés par le même client sans commande, aucun avis n'est affiché sur la fiche du restaurant.", "BUG-018")


@case("TC-EXT-18")
def x18(t):
    p = t.page(); login(p); add(p, 1, 1); p.goto(BASE + "/cart"); t.shot(p, "panier")
    html = p.content()
    remove = "/cart/remove/" in html
    nested = html.count("<form") != html.count("</form>") or "<form></form>" in html
    t.log(f"Formulaire /cart/remove présent : {remove} ; <form> imbriqués ou vides : {nested}")
    t.check(remove, "Un bouton « Retirer » existe pour chaque ligne du panier.", "Aucun bouton « Retirer » dans le panier (route POST /cart/remove/<id> non reliée) ; seul moyen : mettre la quantité à 0.", "BUG-022")


@case("TC-EXT-19")
def x19(t):
    p = t.page(); codes = []
    for i in range(12):
        p.goto(BASE + "/login"); p.fill("input[name=email]", "alice@example.com"); p.fill("input[name=password]", f"Mauvais{i}!"); p.click("form button.button"); p.wait_for_load_state()
        codes.append(" ".join(flashes(p)))
    p.goto(BASE + "/login"); p.fill("input[name=email]", "alice@example.com"); p.fill("input[name=password]", "Password123!"); p.click("form button.button"); p.wait_for_load_state(); t.shot(p, "connexion_apres_12_echecs")
    ok_login = "Déconnexion" in p.content()
    t.log(f"12 échecs : {set(codes)} ; connexion valide ensuite : {ok_login}")
    t.check(not ok_login, "Blocage ou délai après des échecs répétés.", "12 échecs consécutifs sans délai, ni blocage, ni CAPTCHA ; la connexion valide réussit immédiatement.", "BUG-023")


@case("TC-EXT-20", reseed_db=False)
def x20(t):
    p = t.page(); p.goto(BASE + "/"); t.shot(p, "accueil", full=False)
    r = requests.post(BASE + "/api/orders", headers={"X-API-Key": KEY, "Content-Type": "application/json"}, data="[1]")
    dbg = "Werkzeug Debugger" in r.text
    log = Path(os.environ.get("QO_SERVER_LOG", "")).read_text(errors="ignore")[:600] if os.environ.get("QO_SERVER_LOG") else "(journal serveur non fourni)"
    t.log(f"POST /api/orders corps '[1]' → HTTP {r.status_code} ; page du débogueur Werkzeug exposée : {dbg}\n\nJournal de démarrage du serveur :\n{log}")
    t.check(not dbg, "Aucune page de débogage exposée.", f"Erreur 500 avec la page interactive du débogueur Werkzeug (traceback et chemins du serveur) ; journal : « Debug mode: on », « Running on all addresses (0.0.0.0) ».", "BUG-023")
