# -*- coding: utf-8 -*-
"""Cas d'erreur (TC-ERR-xx)."""
from decimal import Decimal as D
from core import *


@case("TC-ERR-01")
def e01(t):
    p = t.page(); login(p, pw="MauvaisMdp1!"); t.shot(p, "echec_connexion")
    t.check("incorrect" in " ".join(flashes(p)) and "/login" in p.url, "Message « Email ou mot de passe incorrect », pas de connexion.", f"Flashs {flashes(p)} URL {p.url}")


@case("TC-ERR-02")
def e02(t):
    p = t.page(); p.goto(BASE + "/register")
    p.fill("input[name=name]", "Alice Bis"); p.fill("input[name=email]", "alice@example.com"); p.fill("input[name=password]", "Password123!")
    p.click("form button.button"); p.wait_for_load_state(); t.shot(p, "email_existant")
    t.check("existe déjà" in " ".join(flashes(p)), "Refus : « Un compte existe déjà avec cet email ».", f"Flashs {flashes(p)}")


@case("TC-ERR-03")
def e03(t):
    r = t.api("GET", "/api/restaurants", key=None, label="Sans clé")
    t.check(r.status_code == 401, "401 Unauthorized.", f"HTTP {r.status_code}")


@case("TC-ERR-04")
def e04(t):
    r = t.api("GET", "/api/orders", key="mauvaise-cle", label="Clé invalide")
    t.check(r.status_code == 401, "401 Unauthorized.", f"HTTP {r.status_code}")


@case("TC-ERR-05")
def e05(t):
    r = t.api("GET", "/api/restaurants/999", label="Restaurant inexistant")
    ct = r.headers.get("Content-Type", "")
    t.check(r.status_code == 404 and "json" in ct, "404 avec un corps JSON d'erreur.", f"HTTP {r.status_code} mais Content-Type « {ct} » : corps HTML au lieu de JSON (contrat d'erreur non respecté, voir openapi.yaml).", "BUG-011")


@case("TC-ERR-06")
def e06(t):
    r = t.api("POST", "/api/orders", {"items": []}, label="items vide")
    t.check(r.status_code == 400, "400 « items is required… ».", f"HTTP {r.status_code}")


@case("TC-ERR-07")
def e07(t):
    r = t.api("POST", "/api/coupons/validate", {"code": "WELCOME10", "subtotal": "abc"}, label="subtotal=abc")
    t.check(r.status_code == 400, "400 « subtotal must be numeric ».", f"HTTP {r.status_code}")


@case("TC-ERR-08")
def e08(t):
    codes = [t.api("POST", "/api/coupons/validate", {"code": "WELCOME10", "subtotal": v}, label=f"subtotal={v}").status_code for v in ("NaN", "Infinity", "1e999")]
    t.check(codes == [400, 400, 400], "400 pour les trois valeurs.", f"Codes obtenus {codes} (valeurs non finies : 500 ou acceptées)", "BUG-010")


@case("TC-ERR-09")
def e09(t):
    r = t.api("POST", "/api/orders", raw="[1]", label="corps tableau")
    t.check(r.status_code == 400, "400 corps invalide.", f"HTTP {r.status_code} : erreur serveur non gérée.", "BUG-010")


@case("TC-ERR-10")
def e10(t):
    a = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}, "x"], "payment_method": "card"}, label="élément 'x'")
    b = t.api("POST", "/api/orders", {"items": [{"product_id": "1", "quantity": 1}], "payment_method": "card"}, label="product_id chaîne")
    t.check(a.status_code == 400 and b.status_code == 400, "400 dans les deux cas.", f"Codes {a.status_code} / {b.status_code}", "BUG-010")


@case("TC-ERR-11")
def e11(t):
    p = t.page(); login(p); p.goto(BASE + "/admin/"); t.shot(p, "admin_client")
    t.check("réservé" in " ".join(flashes(p)) and "Administration" not in p.inner_text("main"), "Redirection avec « Accès réservé aux administrateurs ».", f"URL {p.url}, flashs {flashes(p)}")


@case("TC-ERR-12")
def e12(t):
    p = t.page(); login(p, "bob@example.com"); p.goto(BASE + "/orders/1"); t.shot(p, "commande_autrui")
    t.check("inaccessible" in " ".join(flashes(p)) and "Classic Burger" not in p.inner_text("main"), "« Commande inaccessible », contenu non affiché.", f"URL {p.url}, flashs {flashes(p)}")


@case("TC-ERR-13")
def e13(t):
    p = t.page(); login(p); add(p, 1, 2); checkout(p, "card", coupon="EXPIRED10", confirm=False); t.shot(p, "coupon_expire")
    s = checkout_summary(p)
    t.check("expiré" in " ".join(flashes(p)) and s["reduction"] in (None, D("0")), "Message « Coupon invalide ou expiré », aucune réduction.", f"Flashs {flashes(p)}, réduction {s['reduction']}")


@case("TC-ERR-14")
def e14(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}], "coupon": "EXPIRED10", "payment_method": "card"}, label="coupon expiré")
    t.check(r.status_code == 400, "400 : coupon expiré refusé.", f"HTTP {r.status_code} : commande créée, coupon ignoré silencieusement (aucune erreur).", "BUG-009")


@case("TC-ERR-15")
def e15(t):
    p = t.page(); login(p); add(p, 1, 2); p.goto(BASE + "/checkout")
    p.evaluate("""() => { const s=document.querySelector('select[name=address_id]'); const o=document.createElement('option'); o.value='2'; o.text='adresse de Bob'; s.add(o); s.value='2'; }""")
    p.select_option("#payment_method", "card"); p.click("button[name=confirm][value='1']"); p.wait_for_load_state(); t.shot(p, "adresse_autrui")
    t.check("invalide" in " ".join(flashes(p)) and "/orders/" not in p.url, "« Adresse de livraison invalide », pas de commande.", f"URL {p.url}, flashs {flashes(p)}")


@case("TC-ERR-16")
def e16(t):
    p = t.page(); p.goto(BASE + "/login?next=https://example.org")
    p.fill("input[name=email]", "alice@example.com"); p.fill("input[name=password]", "Password123!")
    reqs = []
    p.on("request", lambda r: reqs.append(r.url) if r.is_navigation_request() else None)
    p.click("form button.button")
    try:
        p.wait_for_url("**example.org**", timeout=6000)
    except Exception:
        pass
    t.log(f"Navigations : {reqs}\nURL finale : {p.url}")
    raw = requests.post(BASE + "/login?next=https://example.org", data={"email": "alice@example.com", "password": "Password123!"}, allow_redirects=False)
    t.log(f"$ curl -i -X POST -d 'email=alice@example.com&password=…' '{BASE}/login?next=https://example.org'\nHTTP {raw.status_code} | Location: {raw.headers.get('Location')}")
    t.shot(p, "apres_connexion", full=False)
    t.check("example.org" not in p.url, "Redirection restreinte au site (accueil).", f"Après connexion, le navigateur est envoyé vers {p.url} (redirection ouverte via ?next=).", "BUG-015")


@case("TC-ERR-17")
def e17(t):
    p = t.page(); login(p); p.goto(BASE + "/checkout"); t.shot(p, "panier_vide")
    t.check("vide" in " ".join(flashes(p)) and "/cart" in p.url, "Redirection vers le panier, message « panier vide ».", f"URL {p.url}, flashs {flashes(p)}")


@case("TC-ERR-18")
def e18(t):
    p = t.page(); login(p); add(p, 1, 1); p.goto(BASE + "/cart")
    p.evaluate("const i=document.querySelector('input[name=qty_1]'); i.type='text';")
    p.fill("input[name=qty_1]", "abc"); p.click("form:not([action]) button, form[method=post]:not([action]) button.secondary"); p.wait_for_load_state(); t.shot(p, "quantite_abc")
    t.check("invalide" in " ".join(flashes(p)), "Message « Quantité invalide », pas d'erreur 500.", f"Flashs {flashes(p)}")


@case("TC-ERR-19")
def e19(t):
    r = t.api("POST", "/api/orders/1/cancel", label="annuler #1 livrée")
    t.check(r.status_code == 409, "409 « order cannot be cancelled ».", f"HTTP {r.status_code}")


@case("TC-ERR-20")
def e20(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}], "coupon": "FOO", "payment_method": "card"}, label="coupon inconnu")
    t.check(r.status_code == 400, "400 : coupon inconnu refusé.", f"HTTP {r.status_code} : commande créée sans réduction ni message.", "BUG-009")


@case("TC-ERR-21")
def e21(t):
    # aucun produit seed n'est indisponible ; rendre un produit indisponible exigerait de modifier la base ou le code.
    r = t.api("GET", "/api/products/1", label="aucun produit available=false dans le jeu de données")
    avail = [t.api("GET", f"/api/products/{i}", show_body=False).json().get("available") for i in range(1, 26)]
    t.log(f"available par produit 1..25 : {avail}")
    if all(avail):
        t.blocked("Les 25 produits du jeu de données sont disponibles et aucune interface ne permet d'en rendre un indisponible : cas non exécutable sans modifier la base.", "BUG-022")
    else:
        t.ok("Produit indisponible refusé.")


@case("TC-ERR-22")
def e22(t):
    r = t.api("POST", "/api/coupons/validate", {"code": "WELCOME10", "subtotal": 100000}, label="subtotal fantaisiste")
    j = r.json()
    t.check(r.status_code != 200 or not j.get("valid"), "Le sous-total devrait être recalculé côté serveur / refusé.", f"HTTP {r.status_code} {j} : le serveur fait confiance au sous-total envoyé par le client.", "BUG-012")


@case("TC-ERR-23")
def e23(t):
    p = t.page(); login(p); add(p, 1, 1); p.goto(BASE + "/cart")
    html = p.content().lower()
    token = "csrf" in html
    p.goto(BASE + "/logout"); t.shot(p, "apres_get_logout")
    out = "Connexion" in p.content() or "/login" in p.content()
    t.log(f"Jeton CSRF présent dans les formulaires : {token} ; GET /logout déconnecte : {out}")
    t.check(token and False, "", f"Aucun jeton CSRF dans les formulaires POST ; GET /logout déconnecte (déconnexion forcée par simple lien/image).", "BUG-023") if (not token or out) else t.ok("CSRF présent.")
