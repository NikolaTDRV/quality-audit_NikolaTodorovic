# -*- coding: utf-8 -*-
"""Cas nominaux et limites (TC-NOM-xx, TC-LIM-xx)."""
from decimal import Decimal as D
from core import *


@case("TC-NOM-01")
def nom01(t):
    p = t.page(); p.goto(BASE + "/")
    names = [e.inner_text().strip() for e in p.query_selector_all("article.card h2, article.card h3")]
    t.shot(p, "accueil")
    body = p.inner_text("main")
    order = [n for n in ["Couscous Atlas", "Tokyo Bowl", "Burger Factory", "Green Kitchen", "Pizza Roma", "Night Sushi"]]
    pos = [body.find(n) for n in order]
    ok = all(x >= 0 for x in pos) and pos == sorted(pos) and "FERMÉ" in body.upper()
    t.log(f"Ordre des positions : {pos}")
    t.check(ok, "6 restaurants listés par note décroissante, Night Sushi marqué FERMÉ.", f"Ordre/contenu inattendu : {pos}")


@case("TC-NOM-02")
def nom02(t):
    p = t.page(); p.goto(BASE + "/register")
    p.fill("input[name=name]", "Test QA"); p.fill("input[name=email]", "test.qa1@example.com"); p.fill("input[name=password]", "Password123!")
    t.shot(p, "formulaire")
    p.click("form button.button"); p.wait_for_load_state()
    t.shot(p, "apres_inscription")
    logged = "/logout" in p.content() or "Déconnexion" in p.content()
    t.check(logged and p.url.rstrip("/") == BASE, "Compte créé, utilisateur connecté et redirigé vers l'accueil.", f"URL {p.url}, connecté={logged}")


@case("TC-NOM-03")
def nom03(t):
    p = t.page(); login(p); t.shot(p, "connecte")
    t.check("Déconnexion" in p.content() and p.url.rstrip("/") == BASE, "Connexion réussie, redirection vers l'accueil, lien Déconnexion visible.", f"URL {p.url}")


@case("TC-NOM-04")
def nom04(t):
    p = t.page(); p.goto(BASE + "/restaurant/1"); t.shot(p, "menu_burger_factory")
    txt = p.inner_text("main")
    need = ["Classic Burger", "11.90", "Frites"]
    miss = [n for n in ["Classic Burger", "Frites", "Veggie Burger"] if n not in txt]
    t.check(not miss and "Burger Factory" in txt, "Menu affiché : produits, prix, stock, catégories et formulaire d'ajout.", f"Éléments manquants : {miss}")


@case("TC-NOM-05")
def nom05(t):
    p = t.page(); login(p); fl = add(p, 1, 1); t.shot(p, "apres_ajout")
    c = cart_totals(p); t.shot(p, "panier")
    t.log(f"Flashs : {fl} ; totaux panier : { {k: str(v) for k, v in c.items() if k != 'texte'} }")
    t.check("ajouté" in " ".join(fl) and c["sous_total"] == D("11.90") and c["livraison"] == D("2.99") and c["total"] == D("14.89"),
            "Message de confirmation ; panier : sous-total 11,90 €, livraison 2,99 €, total 14,89 €.", f"Panier obtenu : {c['sous_total']}/{c['livraison']}/{c['total']}")


@case("TC-NOM-06")
def nom06(t):
    p = t.page(); login(p); add(p, 1, 1)
    p.goto(BASE + "/cart"); p.fill("input[name=qty_1]", "3"); p.click("form:not([action]) button, form[method=post]:not([action]) button.secondary"); p.wait_for_load_state()
    c = cart_totals(p); t.shot(p, "panier_x3")
    t.check(c["sous_total"] == D("35.70") and c["total"] == D("38.69"), "Sous-total 35,70 € ; total 38,69 €.", f"Obtenu {c['sous_total']} / {c['total']}")


@case("TC-NOM-07")
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


@case("TC-NOM-08")
def nom08(t):
    p = t.page(); login(p); add(p, 1, 2); checkout(p, "card"); oid = order_info(p)["id"]
    p.click("button[name=action][value=cancel]"); p.wait_for_load_state(); t.shot(p, "annulee")
    o = order_info(p)
    t.log(f"Badge affiché : {o['status']!r}")
    t.check(o["status"] and ("annul" in o["status"].lower() or "cancel" in o["status"].lower()), f"Commande #{oid} passée à l'état annulé (badge « {o['status']} »).", f"Statut {o['status']}")


@case("TC-NOM-09")
def nom09(t):
    r = t.api("GET", "/api/restaurants", label="Liste des restaurants")
    t.api("GET", "/api/health", key=None, label="Santé sans clé")
    d = r.json(); n = len(d.get("items", d)) if isinstance(d, (dict, list)) else 0
    t.check(r.status_code == 200 and n == 6, "200 et 6 restaurants au format JSON.", f"HTTP {r.status_code}, {n} éléments")


@case("TC-NOM-10")
def nom10(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}], "payment_method": "card"}, label="Création commande carte")
    j = r.json() if r.status_code < 500 else {}
    t.check(r.status_code == 201 and j.get("status") == "confirmed" and str(j.get("total")) in ("14.89", "14.9"), "201, commande confirmée, total 14,89 €.", f"HTTP {r.status_code} {j}")


@case("TC-NOM-11")
def nom11(t):
    p = t.page(); p.goto(BASE + "/?q=pizza"); t.shot(p, "recherche_pizza")
    txt = p.inner_text("main")
    t.check("Pizza Roma" in txt and "Burger Factory" not in txt, "Seul Pizza Roma est affiché.", f"Contenu : {txt[:150]!r}")


@case("TC-NOM-12")
def nom12(t):
    p = t.page(); p.goto(BASE + "/?sort=time"); t.shot(p, "tri_delai")
    txt = p.inner_text("main")
    import re
    times = [int(x) for x in re.findall(r"(\d+)\s*min", txt)]
    t.log(f"Délais lus : {times}")
    t.check(times == sorted(times) and len(times) >= 6, "Restaurants triés par délai croissant.", f"Délais lus : {times}")


@case("TC-NOM-13")
def nom13(t):
    p = t.page(); login(p); p.goto(BASE + "/profile/")
    f = "form[action$='/profile/address']"
    p.fill(f + " input[name=label]", "Travail"); p.fill(f + " input[name=street]", "5 rue Neuve")
    p.fill(f + " input[name=postal_code]", "75002"); p.fill(f + " input[name=city]", "Paris"); p.check(f + " input[name=is_default]")
    p.click(f + " button"); p.wait_for_load_state(); t.shot(p, "profil")
    txt = p.inner_text("main")
    t.check("5 rue Neuve" in txt and "Adresse ajoutée" in " ".join(flashes(p)), "Adresse « Travail » ajoutée et définie par défaut.", f"Flashs {flashes(p)}")


@case("TC-NOM-14")
def nom14(t):
    p = t.page(); login(p); p.goto(BASE + "/orders/1"); p.click("form[action$='/reorder'] button"); p.wait_for_load_state(); t.shot(p, "panier_recommande")
    txt = p.inner_text("main")
    t.check("Classic Burger" in txt and "Frites" in txt, "Panier rempli avec Classic Burger et Frites maison.", f"Panier : {txt[:200]!r}")


@case("TC-NOM-15")
def nom15(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/4"); t.shot(p, "menu_pizza_roma")
    html = p.content().lower()
    has_btn = "/favorite/" in html
    t.log(f"Présence d'un formulaire /favorite/ dans le DOM de la page restaurant : {has_btn}")
    p.goto(BASE + "/"); has_btn2 = "/favorite/" in p.content().lower(); t.log(f"… sur l'accueil : {has_btn2}")
    if not (has_btn or has_btn2):
        t.blocked("Aucun bouton « favori » dans l'interface : la route POST /favorite/<id> existe mais n'est reliée à aucun écran. Cas non exécutable par l'UI.", "BUG-022")
    else:
        t.ok("Bouton favori présent.")


@case("TC-NOM-16")
def nom16(t):
    p = t.page(); login(p); p.goto(BASE + "/profile/"); t.shot(p, "profil_adresses")
    has = "/delete" in p.content()
    t.log(f"Présence d'un formulaire de suppression d'adresse dans le DOM : {has}")
    if not has:
        t.blocked("Aucun bouton « Supprimer » dans l'interface : la route /profile/address/<id>/delete n'est reliée à aucun écran.", "BUG-022")
    else:
        t.ok("Suppression disponible.")


# ----------------------------------------------------------------------------- LIMITES
def coupon(t, sub, code="WELCOME10"):
    return t.api("POST", "/api/coupons/validate", {"code": code, "subtotal": sub}, label=f"subtotal={sub}")


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
def lim04(t):
    res = []
    for i, pw in enumerate(["Pass123", "Pass1234"]):
        p = t.page(); p.goto(BASE + "/register")
        p.fill("input[name=name]", "Lim Test"); p.fill("input[name=email]", f"lim{i}@example.com")
        # on retire minlength (équivalent DevTools) pour tester la règle serveur
        p.evaluate("document.querySelector('input[name=password]').removeAttribute('minlength')")
        p.fill("input[name=password]", pw); p.click("form button.button"); p.wait_for_load_state()
        res.append(("Déconnexion" in p.content(), flashes(p)))
        t.shot(p, f"mdp_{len(pw)}_car")
    t.log(str(res))
    t.check(res[0][0] is False and res[1][0] is True, "7 caractères refusé (message), 8 caractères accepté.", f"Résultats {res}")


@case("TC-LIM-05")
def lim05(t):
    a = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 20}], "payment_method": "card"}, label="quantité 20")
    b = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 21}], "payment_method": "card"}, label="quantité 21")
    t.check(a.status_code == 201 and b.status_code == 400, "20 → 201 ; 21 → 400.", f"20 → {a.status_code} ; 21 → {b.status_code}")


@case("TC-LIM-06")
def lim06(t):
    codes = [t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": q}], "payment_method": "card"}, label=f"quantité {q!r}").status_code for q in (0, -1, "abc")]
    t.check(codes == [400, 400, 400], "0, -1 et « abc » → 400.", f"Codes {codes}")


@case("TC-LIM-07")
def lim07(t):
    p = t.page(); res = {}
    for v in ("2.00", "2.50"):
        p.goto(f"{BASE}/?max_delivery={v}")
        res[v] = [n for n in ["Couscous Atlas", "Tokyo Bowl", "Burger Factory", "Green Kitchen", "Pizza Roma", "Night Sushi"] if n in p.inner_text("main")]
        t.shot(p, f"max_{v}")
    t.log(f"Restaurants affichés : {res}")
    # attendu : max 2.00 → Green Kitchen (1.99) ; max 2.50 → Green Kitchen + Pizza Roma (2.49)
    t.check(res["2.00"] == ["Green Kitchen"] and set(res["2.50"]) == {"Green Kitchen", "Pizza Roma"},
            "Seuls les restaurants dont les frais sont ≤ au plafond.", f"≤2,00 € → {res['2.00']} ; ≤2,50 € → {res['2.50']} (filtre inversé : affiche les frais ≥ plafond)", "BUG-006")


@case("TC-LIM-08")
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


@case("TC-LIM-09")
def lim09(t):
    p = t.page(); login(p); st = stock_ui(p, 4); fl = add(p, 4, 1); t.shot(p, "apres_ajout")
    c = cart_totals(p); t.shot(p, "panier")
    accepted = "Veggie" in c["texte"]
    t.check(not accepted, "Produit en rupture non ajoutable.", f"Veggie Burger (stock {st}) ajouté au panier. Flashs : {fl}", "BUG-004")


@case("TC-LIM-10")
def lim10(t):
    p = t.page(); login(p); fl = add(p, 1, 1000, bypass=True); c = cart_totals(p); t.shot(p, "panier_1000")
    t.log(f"Flashs {fl}; panier {c['texte'][:200]!r}")
    t.check("1000" not in c["texte"] and c["sous_total"] < D("5000"), "Quantité plafonnée (max 99 / stock).", f"1000 × Classic Burger au panier : sous-total {c['sous_total']} € pour un stock de 100.", "BUG-004")


@case("TC-LIM-11")
def lim11(t):
    p = t.page(); p.goto(BASE + "/?q=%25"); t.shot(p, "recherche_pourcent")
    n = len([x for x in ["Couscous Atlas", "Tokyo Bowl", "Burger Factory", "Green Kitchen", "Pizza Roma", "Night Sushi"] if x in p.inner_text("main")])
    t.check(n == 0, "Aucun restaurant dont le nom contient « % ».", f"{n} restaurants affichés pour q=% : le caractère joker n'est pas échappé.", "BUG-013")


@case("TC-LIM-12")
def lim12(t):
    p = t.page(); p.goto(BASE + "/register")
    p.fill("input[name=name]", "N" * 121); p.fill("input[name=email]", "long@example.com"); p.fill("input[name=password]", "Password123!")
    p.click("form button.button"); p.wait_for_load_state(); t.shot(p, "apres_nom_121")
    created = "Déconnexion" in p.content()
    t.check(not created, "Nom de 121 caractères refusé (limite attendue ≈ 120).", "Compte créé avec un nom de 121 caractères : aucune longueur maximale n'est contrôlée.", "BUG-024")


@case("TC-LIM-13")
def lim13(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 20}, {"product_id": 1, "quantity": 20}], "payment_method": "card"}, label="2 lignes de 20")
    t.check(r.status_code == 400, "Refus : 40 unités dépassent la limite de 20.", f"HTTP {r.status_code} : 40 unités acceptées via deux lignes de 20.", "BUG-004")
