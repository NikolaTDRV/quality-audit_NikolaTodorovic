# -*- coding: utf-8 -*-
"""Campagne QuickOrder : 24 cas de test (6 nominaux, 6 limites, 6 erreurs, 6 règles métier).

Chaque cas exécute ses étapes dans le navigateur (Playwright) ou sur l'API (requests), réinitialise la base
avant de commencer, enregistre ses preuves dans docs/evidence/ et son verdict dans results.json.
"""
import re, shutil
from decimal import Decimal as D
from datetime import datetime
from core import *


def coupon(t, sub, code="WELCOME10"):
    return t.api("POST", "/api/coupons/validate", {"code": code, "subtotal": sub}, label=f"subtotal={sub}")


@case("TC-ERR-01")
def e01(t):
    p = t.page(); login(p, pw="MauvaisMdp1!"); t.shot(p, "echec_connexion")
    t.check("incorrect" in " ".join(flashes(p)) and "/login" in p.url, "Message « Email ou mot de passe incorrect », pas de connexion.", f"Flashs {flashes(p)} URL {p.url}")


@case("TC-ERR-02")
def e03(t):
    r = t.api("GET", "/api/restaurants", key=None, label="Sans clé")
    t.check(r.status_code == 401, "401 Unauthorized.", f"HTTP {r.status_code}")


@case("TC-ERR-03")
def e11(t):
    p = t.page(); login(p); p.goto(BASE + "/admin/"); t.shot(p, "admin_client")
    t.check("réservé" in " ".join(flashes(p)) and "Administration" not in p.inner_text("main"), "Redirection avec « Accès réservé aux administrateurs ».", f"URL {p.url}, flashs {flashes(p)}")


@case("TC-ERR-04")
def e12(t):
    p = t.page(); login(p, "bob@example.com"); p.goto(BASE + "/orders/1"); t.shot(p, "commande_autrui")
    t.check("inaccessible" in " ".join(flashes(p)) and "Classic Burger" not in p.inner_text("main"), "« Commande inaccessible », contenu non affiché.", f"URL {p.url}, flashs {flashes(p)}")


@case("TC-ERR-05")
def e08(t):
    codes = [t.api("POST", "/api/coupons/validate", {"code": "WELCOME10", "subtotal": v}, label=f"subtotal={v}").status_code for v in ("NaN", "Infinity", "1e999")]
    t.check(codes == [400, 400, 400], "400 pour les trois valeurs.", f"Codes obtenus {codes} (valeurs non finies : 500 ou acceptées)", "BUG-007")


@case("TC-ERR-06")
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
    t.check("example.org" not in p.url, "Redirection restreinte au site (accueil).", f"Après connexion, le navigateur est envoyé vers {p.url} (redirection ouverte via ?next=).", "BUG-008")


@case("TC-LIM-01")
def lim01(t):
    r = coupon(t, 20.00); j = r.json()
    t.check(r.status_code == 200 and j.get("valid") is True and float(j.get("discount", 0)) == 2.0, "Coupon valide, réduction 2,00 € (10 % de 20 €).", f"HTTP {r.status_code} {j}")


@case("TC-LIM-02")
def lim02(t):
    r = coupon(t, 19.99); j = r.json()
    t.check(j.get("valid") is False, "Coupon refusé : minimum 20 € non atteint.", f"{j}")


@case("TC-LIM-03")
def lim03(t):
    r = coupon(t, 100); j = r.json()
    t.check(float(j.get("discount", 0)) == 8.0, "Réduction plafonnée à 8,00 € (max_discount de WELCOME10).", f"{j}")


@case("TC-LIM-04")
def lim05(t):
    a = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 20}], "payment_method": "card"}, label="quantité 20")
    b = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 21}], "payment_method": "card"}, label="quantité 21")
    t.check(a.status_code == 201 and b.status_code == 400, "20 → 201 ; 21 → 400.", f"20 → {a.status_code} ; 21 → {b.status_code}")


@case("TC-LIM-05")
def lim06(t):
    codes = [t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": q}], "payment_method": "card"}, label=f"quantité {q!r}").status_code for q in (0, -1, "abc")]
    t.check(codes == [400, 400, 400], "0, -1 et « abc » → 400.", f"Codes {codes}")


@case("TC-LIM-06")
def lim08(t):
    p = t.page(); login(p); st0 = stock_ui(p, 7); fl = add(p, 7, 3, bypass=True)
    c = cart_totals(p); t.shot(p, "panier_3_pour_stock_2")
    t.log(f"Stock {st0}, flashs {fl}, panier {c['texte'][:200]!r}")
    t.check("Salmon" not in c["texte"] or "×" not in c["texte"] and False, "", "") if False else None
    accepted = "Salmon" in c["texte"]
    if accepted:
        checkout(p, "card"); o = order_info(p); t.shot(p, "commande_3_pour_stock_2")
        st1 = stock_ui(p, 7); t.shot(p, "stock_apres_commande")
        t.log(f"Commande #{o['id']} confirmée ({o['status']}) ; stock du Salmon Bowl : {st0} → {st1}")
    t.check(not accepted, "Ajout refusé (stock 2).", f"Quantité 3 acceptée au panier pour un stock de {st0} (sous-total {c['sous_total']} €), commande #{o['id']} confirmée, stock final {st1}." if accepted else "", "BUG-004")


@case("TC-NOM-01")
def nom03(t):
    p = t.page(); login(p); t.shot(p, "connecte")
    t.check("Déconnexion" in p.content() and p.url.rstrip("/") == BASE, "Connexion réussie, redirection vers l'accueil, lien Déconnexion visible.", f"URL {p.url}")


@case("TC-NOM-02")
def nom05(t):
    p = t.page(); login(p); fl = add(p, 1, 1); t.shot(p, "apres_ajout")
    c = cart_totals(p); t.shot(p, "panier")
    t.log(f"Flashs : {fl} ; totaux panier : { {k: str(v) for k, v in c.items() if k != 'texte'} }")
    t.check("ajouté" in " ".join(fl) and c["sous_total"] == D("11.90") and c["livraison"] == D("2.99") and c["total"] == D("14.89"),
            "Message de confirmation ; panier : sous-total 11,90 €, livraison 2,99 €, total 14,89 €.", f"Panier obtenu : {c['sous_total']}/{c['livraison']}/{c['total']}")


@case("TC-NOM-03")
def nom07(t):
    p = t.page(); login(p); add(p, 1, 2)
    p.goto(BASE + "/checkout"); t.shot(p, "checkout")
    checkout(p, "card", coupon="WELCOME10", confirm=False)
    s = checkout_summary(p); t.shot(p, "recap_coupon")
    t.log(f"Récap : {s['texte']}")
    checkout(p, "card", coupon="WELCOME10")
    o = order_info(p); t.shot(p, "commande_confirmee")
    exp = D("23.80") - D("2.38") + D("2.99")  # 24,41 €
    t.log(f"Statut affiché tel quel dans le badge : {o['status']!r}")
    t.check(o["status"] and "confirm" in o["status"].lower() and o["total"] == exp and s["reduction"] == D("2.38"),
            f"Commande #{o['id']} confirmée ; réduction 2,38 € ; total {o['total']} €.", f"Statut {o['status']}, total {o['total']}, réduction {s['reduction']} (attendu {exp})")


@case("TC-NOM-04")
def nom08(t):
    p = t.page(); login(p); add(p, 1, 2); checkout(p, "card"); oid = order_info(p)["id"]
    p.click("button[name=action][value=cancel]"); p.wait_for_load_state(); t.shot(p, "annulee")
    o = order_info(p)
    t.log(f"Badge affiché : {o['status']!r}")
    t.check(o["status"] and ("annul" in o["status"].lower() or "cancel" in o["status"].lower()), f"Commande #{oid} passée à l'état annulé (badge « {o['status']} »).", f"Statut {o['status']}")


@case("TC-NOM-05")
def nom09(t):
    r = t.api("GET", "/api/restaurants", label="Liste des restaurants")
    t.api("GET", "/api/health", key=None, label="Santé sans clé")
    d = r.json(); n = len(d.get("items", d)) if isinstance(d, (dict, list)) else 0
    t.check(r.status_code == 200 and n == 6, "200 et 6 restaurants au format JSON.", f"HTTP {r.status_code}, {n} éléments")


@case("TC-NOM-06")
def nom10(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}], "payment_method": "card"}, label="Création commande carte")
    j = r.json() if r.status_code < 500 else {}
    t.check(r.status_code == 201 and j.get("status") == "confirmed" and str(j.get("total")) in ("14.89", "14.9"), "201, commande confirmée, total 14,89 €.", f"HTTP {r.status_code} {j}")


@case("TC-RM-01")
def r02(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/6"); t.shot(p, "menu_restaurant_ferme")
    fl = add(p, 24, 1); checkout(p, "card"); t.shot(p, "resultat_checkout")
    ordered = "/orders/" in p.url
    t.log(f"Flashs ajout : {fl} ; URL finale : {p.url}")
    t.check(not ordered, "Commande refusée : restaurant fermé.", f"Commande {p.url.split('/')[-1]} confirmée chez Night Sushi (FERMÉ) pour 14,00 €.", "BUG-002")


@case("TC-RM-02")
def r04(t):
    p = t.page(); login(p); add(p, 3, 1); c = cart_totals(p); checkout(p, "card"); t.shot(p, "resultat")
    ordered = "/orders/" in p.url
    t.check(not ordered, "Commande refusée : minimum 20 € non atteint.", f"Commande confirmée pour {c['sous_total']} € de produits (minimum du restaurant : 20 €).", "BUG-005")


@case("TC-RM-03")
def r06(t):
    p = t.page(); login(p); add(p, 1, 1); checkout(p, "cash", cash=1.00, confirm=False); t.shot(p, "cash_1_euro")
    p.click("button[name=confirm][value='1']"); p.wait_for_load_state(); t.shot(p, "resultat")
    txt = p.inner_text("main"); t.log(txt)
    ok1 = "/orders/" not in p.url
    add(p, 1, 1); checkout(p, "cash", cash=None, confirm=False); p.click("button[name=confirm][value='1']"); p.wait_for_load_state(); t.shot(p, "cash_vide")
    t.log("Cas « montant remis vide » :\n" + p.inner_text("main"))
    ok2 = "/orders/" not in p.url
    t.check(ok1 and ok2, "Commande refusée : 1,00 € < 14,89 € (et montant vide).", f"Commande acceptée avec 1,00 € remis pour 14,89 € (monnaie négative affichée) ; un montant vide est accepté aussi : {not ok2}.", "BUG-003")


@case("TC-RM-04")
def r09(t):
    p = t.page(video=True); login(p); add(p, 1, 1)
    before = order_ids(p); checkout(p, "paypal"); t.shot(p, "commande_paypal")
    after = order_ids(p); t.shot(p, "liste_commandes")
    t.log(f"Commandes avant : {before} ; après : {after}")
    vp = p.video.path(); p.context.close()
    dst = EVID / "TC-RM-04_paypal_double_commande.webm"
    shutil.move(vp, dst); t.files.append(dst.name)
    n = len(after) - len(before)
    t.check(n == 1, "Une seule commande créée.", f"{n} commandes créées pour un seul paiement PayPal ({sorted(set(after)-set(before))}).", "BUG-001")


@case("TC-RM-05")
def r11(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/5"); t.shot(p, "offre_annoncee", full=False)
    add(p, 20, 2); checkout(p, "card", coupon="ATLAS15", confirm=False); s = checkout_summary(p); t.shot(p, "recap"); t.log("Récapitulatif du checkout :\n"+s["texte"])
    exp = (s["sous_total"] * D("0.15")).quantize(D("0.01"))
    t.log(f"Sous-total {s['sous_total']} ; réduction obtenue {s['reduction']} ; attendue à 15 % : {exp}")
    t.check(s["reduction"] == exp, "Réduction de 15 %.", f"Offre annoncée « -15 % » mais réduction de {s['reduction']} € sur {s['sous_total']} € (= 10 %), au lieu de {exp} €.", "BUG-006")


@case("TC-RM-06")
def r12(t):
    p = t.page(); login(p); add(p, 6, 3); checkout(p, "card", coupon="TOKYO30", confirm=False); s = checkout_summary(p); t.shot(p, "recap_tokyo30"); t.log("Récapitulatif du checkout :\n"+s["texte"])
    t.check(s["reduction"] == D("3.49") and s["total"] == s["sous_total"], "Livraison offerte : réduction 3,49 €, total = sous-total.", f"{s}")
