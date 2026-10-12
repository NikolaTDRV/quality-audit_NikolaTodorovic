# -*- coding: utf-8 -*-
"""Règles métier, environnement, concurrence et complémentaires."""
import re, shutil, subprocess, threading, os
from datetime import datetime
from decimal import Decimal as D
from zoneinfo import ZoneInfo
from core import *


def api_count(t, label=None):
    return t.api("GET", "/api/orders", show_body=False, label=label).json().get("count")


@case("TC-RM-01")
def r01(t):
    p = t.page(); login(p); add(p, 6, 1); fl = add(p, 1, 1); t.shot(p, "message_mono_restaurant")
    c = cart_totals(p)
    t.check("même restaurant" in " ".join(fl) and "Classic Burger" not in c["texte"], "Message « même restaurant », seul le produit de Tokyo Bowl reste au panier.", f"Flashs {fl}")


@case("TC-RM-02")
def r02(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/6"); t.shot(p, "menu_restaurant_ferme")
    fl = add(p, 24, 1); checkout(p, "card"); t.shot(p, "resultat_checkout")
    ordered = "/orders/" in p.url
    t.log(f"Flashs ajout : {fl} ; URL finale : {p.url}")
    t.check(not ordered, "Commande refusée : restaurant fermé.", f"Commande {p.url.split('/')[-1]} confirmée chez Night Sushi (FERMÉ) pour 14,00 €.", "BUG-002")


@case("TC-RM-03")
def r03(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 24, "quantity": 1}], "payment_method": "card"}, label="produit d'un restaurant fermé")
    t.check(r.status_code == 409, "409 restaurant fermé.", f"HTTP {r.status_code} : commande créée chez un restaurant fermé.", "BUG-002")


@case("TC-RM-04")
def r04(t):
    p = t.page(); login(p); add(p, 3, 1); c = cart_totals(p); checkout(p, "card"); t.shot(p, "resultat")
    ordered = "/orders/" in p.url
    t.check(not ordered, "Commande refusée : minimum 20 € non atteint.", f"Commande confirmée pour {c['sous_total']} € de produits (minimum du restaurant : 20 €).", "BUG-005")


@case("TC-RM-05")
def r05(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 3, "quantity": 1}], "payment_method": "card"}, label="3,50 € < 20 €")
    t.check(r.status_code == 400, "400 minimum non atteint.", f"HTTP {r.status_code} : commande créée sous le minimum.", "BUG-005")


@case("TC-RM-06")
def r06(t):
    p = t.page(); login(p); add(p, 1, 1); checkout(p, "cash", cash=1.00, confirm=False); t.shot(p, "cash_1_euro")
    p.click("button[name=confirm][value='1']"); p.wait_for_load_state(); t.shot(p, "resultat")
    txt = p.inner_text("main"); t.log(txt)
    ok1 = "/orders/" not in p.url
    add(p, 1, 1); checkout(p, "cash", cash=None, confirm=False); p.click("button[name=confirm][value='1']"); p.wait_for_load_state(); t.shot(p, "cash_vide")
    t.log("Cas « montant remis vide » :\n" + p.inner_text("main"))
    ok2 = "/orders/" not in p.url
    t.check(ok1 and ok2, "Commande refusée : 1,00 € < 14,89 € (et montant vide).", f"Commande acceptée avec 1,00 € remis pour 14,89 € (monnaie négative affichée) ; un montant vide est accepté aussi : {not ok2}.", "BUG-003")


@case("TC-RM-07")
def r07(t):
    r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}], "payment_method": "cash", "cash_received": 1}, label="espèces 1 €")
    t.check(r.status_code == 400, "400 montant insuffisant.", f"HTTP {r.status_code} : {r.text[:120]!r}", "BUG-003")


@case("TC-RM-08")
def r08(t):
    p = t.page(); login(p); add(p, 1, 1); checkout(p, "cash", cash=20); t.shot(p, "commande_cash")
    txt = p.inner_text("main"); t.log(txt)
    t.check("5.11" in txt or "5,11" in txt, "Monnaie à rendre 5,11 €.", f"Texte : {txt[:200]!r}")


@case("TC-RM-09")
def r09(t):
    p = t.page(video=True); login(p); add(p, 1, 1)
    before = order_ids(p); checkout(p, "paypal"); t.shot(p, "commande_paypal")
    after = order_ids(p); t.shot(p, "liste_commandes")
    t.log(f"Commandes avant : {before} ; après : {after}")
    vp = p.video.path(); p.context.close()
    dst = EVID / "TC-RM-09_paypal_double_commande.webm"
    shutil.move(vp, dst); t.files.append(dst.name)
    n = len(after) - len(before)
    t.check(n == 1, "Une seule commande créée.", f"{n} commandes créées pour un seul paiement PayPal ({sorted(set(after)-set(before))}).", "BUG-001")


@case("TC-RM-10")
def r10(t):
    s0 = t.api("GET", "/api/products/1", show_body=False).json()["stock"]
    b = api_count(t, "avant"); r = t.api("POST", "/api/orders", {"items": [{"product_id": 1, "quantity": 1}], "payment_method": "paypal"}, label="paypal"); a = api_count(t, "après")
    s1 = t.api("GET", "/api/products/1", label="stock après", show_body=False).json()["stock"]
    t.log(f"Commandes : {b} → {a} ; stock du produit 1 : {s0} → {s1}")
    t.check(a - b == 1, "Une seule commande créée.", f"{a - b} commandes créées par une seule requête PayPal ; stock du Classic Burger {s0} → {s1} (−{s0 - s1} pour 1 unité commandée).", "BUG-001")


@case("TC-RM-11")
def r11(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/5"); t.shot(p, "offre_annoncee", full=False)
    add(p, 20, 2); checkout(p, "card", coupon="ATLAS15", confirm=False); s = checkout_summary(p); t.shot(p, "recap"); t.log("Récapitulatif du checkout :\n"+s["texte"])
    exp = (s["sous_total"] * D("0.15")).quantize(D("0.01"))
    t.log(f"Sous-total {s['sous_total']} ; réduction obtenue {s['reduction']} ; attendue à 15 % : {exp}")
    t.check(s["reduction"] == exp, "Réduction de 15 %.", f"Offre annoncée « -15 % » mais réduction de {s['reduction']} € sur {s['sous_total']} € (= 10 %), au lieu de {exp} €.", "BUG-007")


@case("TC-RM-12")
def r12(t):
    p = t.page(); login(p); add(p, 6, 3); checkout(p, "card", coupon="TOKYO30", confirm=False); s = checkout_summary(p); t.shot(p, "recap_tokyo30"); t.log("Récapitulatif du checkout :\n"+s["texte"])
    t.check(s["reduction"] == D("3.49") and s["total"] == s["sous_total"], "Livraison offerte : réduction 3,49 €, total = sous-total.", f"{s}")


@case("TC-RM-13")
def r13(t):
    p = t.page(); login(p); add(p, 1, 3); checkout(p, "card", coupon="TOKYO30", confirm=False); s = checkout_summary(p); t.shot(p, "tokyo30_chez_burger"); t.log("Récapitulatif du checkout :\n"+s["texte"])
    t.check(not s["reduction"], "Coupon TOKYO30 refusé hors Tokyo Bowl.", f"Réduction de {s['reduction']} € appliquée chez Burger Factory (code réservé à Tokyo Bowl : « Livraison gratuite dès 30 € avec TOKYO30 »).", "BUG-008")


@case("TC-RM-14")
def r14(t):
    p = t.page(); login(p); add(p, 1, 1); checkout(p, "card", coupon="WELCOME10", confirm=False); t.shot(p, "minimum_coupon")
    s = checkout_summary(p)
    t.check("Montant minimum" in " ".join(flashes(p)) and not s["reduction"], "Message « Montant minimum de 20.00 € requis », pas de réduction.", f"Flashs {flashes(p)}")


@case("TC-RM-15")
def r15(t):
    p = t.page(); login(p); p.goto(BASE + "/orders/1"); t.shot(p, "commande_livree")
    btn = p.query_selector("button[name=action][value=cancel]")
    t.log(f"Bouton Annuler présent : {bool(btn)}")
    # envoi direct de la requête POST (équivalent DevTools)
    p.evaluate("""() => { const f=document.createElement('form'); f.method='post'; const i=document.createElement('input'); i.name='action'; i.value='cancel'; f.appendChild(i); document.body.appendChild(f); f.submit(); }""")
    p.wait_for_load_state(); t.shot(p, "apres_post_annulation")
    o = order_info(p)
    t.check("plus être annulée" in " ".join(o["flashes"]) and "deliver" in o["status"].lower(), "Annulation refusée, statut inchangé.", f"Flashs {o['flashes']}, statut {o['status']}")


@case("TC-RM-16")
def r16(t):
    p = t.page(); login(p); s0 = stock_ui(p, 1); add(p, 1, 2); checkout(p, "card"); s1 = stock_ui(p, 1)
    p.goto(BASE + "/orders"); oid = order_ids(p)[0]; p.goto(f"{BASE}/orders/{oid}")
    p.click("button[name=action][value=cancel]"); p.wait_for_load_state(); t.shot(p, "apres_annulation")
    o = order_info(p); s2 = stock_ui(p, 1)
    pay = re.search(r"(?i)(paiement|payment)[^\n]*", o["texte"])
    t.log(f"Stock {s0} → {s1} (commande) → {s2} (annulation) ; statut {o['status']} ; paiement : {pay.group(0) if pay else '?'} ; texte : {o['texte'][:300]!r}")
    t.check(s2 == s0 and "refund" in o["texte"].lower(), "Stock restitué et paiement remboursé.", f"Stock {s0} → {s1} → {s2} après annulation ; la commande annulée reste « paid » (aucun remboursement ni restitution).", "BUG-016")


@case("TC-RM-17")
def r17(t):
    p = t.page(); login(p, "admin@quickorder.local", "Admin123!"); p.goto(BASE + "/admin/"); t.shot(p, "admin")
    f = "form[action$='/orders/1/status']"
    res = []
    for st in ("confirmed", "cancelled"):
        p.select_option(f"{f} select[name=status]", st); p.click(f"{f} button"); p.wait_for_load_state()
        res.append((st, flashes(p)))
        p.goto(BASE + "/orders/1"); res.append(order_info(p)["status"]); p.goto(BASE + "/admin/")
    t.shot(p, "apres_transitions"); t.log(str(res))
    accepted = [x for x in res if isinstance(x, tuple) and any("mis à jour" in f for f in x[1])]
    t.check(not accepted, "Transitions delivered → confirmed/cancelled refusées.", f"Transitions arrière acceptées : {res}", "BUG-017")


@case("TC-RM-18")
def r18(t):
    p = t.page(); login(p, "bob@example.com"); p.goto(BASE + "/restaurant/4")
    p.select_option("select[name=rating]", "1"); p.fill("textarea[name=comment]", "Nul"); p.click("form[action$='/review'] button"); p.wait_for_load_state(); t.shot(p, "avis_publie")
    t.check("Merci" not in " ".join(flashes(p)), "Avis refusé : Bob n'a jamais commandé chez Pizza Roma.", f"Avis publié sans commande préalable (flashs {flashes(p)}).", "BUG-018")


@case("TC-RM-19")
def r19(t):
    p = t.page(); login(p); p.goto(BASE + "/restaurant/4"); h0 = p.inner_text("main")
    m0 = re.search(r"(\d\.\d)\s*★|★\s*(\d\.\d)|Note[^\d]*(\d\.\d)", h0)
    for note, txt in ((1, "Nul"), (1, "Très mauvais")):
        p.select_option("select[name=rating]", str(note)); p.fill("textarea[name=comment]", txt); p.click("form[action$='/review'] button"); p.wait_for_load_state()
    p.goto(BASE + "/restaurant/4"); h1 = p.inner_text("main"); t.shot(p, "restaurant_apres_avis")
    t.log(f"Avant : {h0[:300]!r}\nAprès : {h1[:300]!r}")
    r = t.api("GET", "/api/restaurants/4", label="note via l'API")
    t.check(False, "", "Les avis publiés n'influencent pas la note affichée (4.3 inchangée après deux avis à 1/5) : la note est une valeur fixe, pas une moyenne.", "BUG-018") if "4.3" in h1 else t.ok("La note évolue avec les avis.")


@case("TC-RM-20")
def r20(t):
    p = t.page(); login(p); add(p, 1, 1); p.goto(BASE + "/cart")
    p.evaluate("document.querySelector('input[name=qty_1]').name='qty_6'")
    p.click("form:not([action]) button, form[method=post]:not([action]) button.secondary"); p.wait_for_load_state()
    c = cart_totals(p); t.shot(p, "panier_deux_restaurants"); t.log(c["texte"])
    both = "Classic Burger" in c["texte"] and "Teriyaki" in c["texte"]
    if both:
        checkout(p, "card"); o = order_info(p); t.shot(p, "commande_mixte"); t.log("Commande créée :\n" + o["texte"])
    t.check(not both, "Un seul restaurant par panier, y compris via le formulaire du panier.", f"Panier avec deux restaurants (Burger Factory + Tokyo Bowl) : {c['sous_total']} € ; la commande #{o['id']} est confirmée avec les deux (voir capture)." if both else "", "BUG-019")


@case("TC-RM-21")
def r21(t):
    p = t.page(); login(p); s0 = stock_ui(p, 1); add(p, 1, 2); checkout(p, "card"); s1 = stock_ui(p, 1)
    t.check(s1 == s0 - 2, f"Stock {s0} → {s0 - 2}.", f"Stock {s0} → {s1}")


@case("TC-RM-22")
def r22(t):
    p = t.page(); p.goto(BASE + "/register")
    p.fill("input[name=name]", "Nouvel Client"); p.fill("input[name=email]", "nouveau@example.com"); p.fill("input[name=password]", "Password123!")
    p.click("form button.button"); p.wait_for_load_state()
    add(p, 1, 2); p.goto(BASE + "/checkout"); t.shot(p, "checkout_adresse_vide")
    opt = p.inner_text("select[name=address_id]"); t.log(f"Option d'adresse proposée : {opt!r}")
    p.select_option("#payment_method", "card"); p.click("button[name=confirm][value='1']"); p.wait_for_load_state(); t.shot(p, "commande")
    t.check("/orders/" not in p.url, "Commande refusée tant qu'aucune adresse complète n'est saisie.", f"Commande confirmée avec une adresse de livraison vide (option « {opt.strip()[:40]} »).", "BUG-014")


@case("TC-RM-23")
def r23(t):
    p = t.page(); login(p); p.goto(BASE + "/profile/")
    f = "form[action$='/profile/address']"
    p.fill(f + " input[name=label]", "Travail"); p.fill(f + " input[name=street]", "5 rue Neuve"); p.fill(f + " input[name=postal_code]", "75002"); p.fill(f + " input[name=city]", "Paris"); p.click(f + " button"); p.wait_for_load_state()
    add(p, 1, 2); p.goto(BASE + "/checkout")
    val = p.evaluate("[...document.querySelectorAll('select[name=address_id] option')].find(o=>o.textContent.includes('Travail')).value")
    p.select_option("select[name=address_id]", val); p.fill("textarea[name=customer_note]", "Code 5678"); p.select_option("#payment_method", "cash"); p.fill("input[name=coupon]", "LUNCH5")
    t.shot(p, "avant_application")
    p.click("button[name=confirm][value='0']"); p.wait_for_load_state(); t.shot(p, "apres_application")
    state = p.evaluate("""() => ({addr: document.querySelector('select[name=address_id]').selectedOptions[0].textContent, note: document.querySelector('textarea[name=customer_note]').value, pay: document.querySelector('#payment_method').value})""")
    t.log(f"État du formulaire après « Appliquer » : {state}")
    kept = "Travail" in state["addr"] and state["note"] == "Code 5678" and state["pay"] == "cash"
    t.check(kept, "Adresse, note et mode de paiement conservés.", f"Après « Appliquer le coupon » : adresse « {state['addr'][:30].strip()} », note « {state['note']} », paiement « {state['pay']} » (saisies perdues).", "BUG-020")


@case("TC-RM-24")
def r24(t):
    p = t.page(tz="Europe/Paris"); login(p); add(p, 1, 2); checkout(p, "card")
    now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M"); t.shot(p, "commande_heure")
    txt = p.inner_text("main"); hm = re.findall(r"\b\d{2}:\d{2}\b", txt)
    t.log(f"Heure à Paris au moment du test : {now} ; heures affichées sur la commande : {hm}")
    t.check(now in hm or (hm and abs(int(hm[0][:2]) * 60 + int(hm[0][3:]) - (int(now[:2]) * 60 + int(now[3:]))) <= 2), "Heure affichée en heure de Paris.", f"Heure affichée {hm} alors qu'il est {now} à Paris : l'horaire est en UTC sans indication.", "BUG-021")


@case("TC-RM-25")
def r25(t):
    p = t.page(); login(p); res = []
    for i in range(2):
        add(p, 1, 2); checkout(p, "card", coupon="WELCOME10", confirm=False); s = checkout_summary(p); res.append(s["reduction"]); checkout(p, "card", coupon="WELCOME10")
    t.log(f"Réductions obtenues sur deux commandes successives : {res}")
    t.skip(f"Le code « WELCOME10 » est accepté à chaque commande (réductions {[str(x) for x in res]}). Aucune spécification ne dit s'il est limité à la première commande : règle à clarifier avec le métier avant de conclure.", "")


@case("TC-ENV-01", reseed_db=False)
def env01(t):
    try:
        r = subprocess.run(["./docker-entrypoint.sh"], cwd=REPO, capture_output=True, text=True)
    except PermissionError as e:
        r = subprocess.CompletedProcess([], 126, "", f"bash: ./docker-entrypoint.sh: Permission denied ({e})")
    mode = subprocess.run(["git", "ls-files", "-s", "docker-entrypoint.sh"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dock = subprocess.run("which docker; docker info 2>&1 | head -3", shell=True, capture_output=True, text=True).stdout
    t.log(f"$ ./docker-entrypoint.sh\nexit={r.returncode}\n{r.stderr.strip() or r.stdout.strip()}\n\n$ git ls-files -s docker-entrypoint.sh\n{mode}\n\n$ docker info\n{dock}")
    ko = r.returncode != 0 and "Permission" in (r.stderr + r.stdout)
    t.check(not ko, "Le script d'entrée est exécutable (mode 100755).", f"« {r.stderr.strip()} » (exit {r.returncode}) ; mode Git {mode.split()[0]} : le conteneur ne peut pas démarrer sous Linux/macOS. (Daemon Docker indisponible dans cet environnement : l'échec est reproduit par exécution directe du script.)", "BUG-025")


@case("TC-NFR-01")
def nfr01(t):
    out = []
    def go(i):
        r = requests.post(BASE + "/api/orders", headers={"X-API-Key": KEY, "Content-Type": "application/json"}, data=json.dumps({"items": [{"product_id": 7, "quantity": 1}], "payment_method": "card"}))
        out.append((i, r.status_code))
    th = [threading.Thread(target=go, args=(i,)) for i in range(4)]
    [x.start() for x in th]; [x.join() for x in th]
    st = t.api("GET", "/api/products/7", label="stock final").json().get("stock")
    t.log(f"Réponses : {sorted(out)} ; stock final : {st}")
    ok_n = len([1 for _, c in out if c == 201])
    t.check(ok_n <= 2 and st >= 0, "Au plus 2 commandes acceptées, stock jamais négatif.", f"{ok_n} commandes acceptées sur 4 pour un stock initial de 2 ; stock final {st}.", "BUG-004")
