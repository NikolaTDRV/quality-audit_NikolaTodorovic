# -*- coding: utf-8 -*-
"""Socle de la campagne QuickOrder : navigateur (Playwright), API (requests), preuves et résultats.

Variables d'environnement :
  QO_BASE   URL de l'application          (défaut http://127.0.0.1:5000)
  QO_REPO   dossier du projet QuickOrder   (pour relancer seed.py)
  DATABASE_URL doit pointer la même base que le serveur (utilisé par seed.py)
"""
import json
import os
import re
import subprocess
import sys
import traceback
from decimal import Decimal
from pathlib import Path

import requests

BASE = os.getenv("QO_BASE", "http://127.0.0.1:5000")
KEY = "quickorder-demo-key"
HERE = Path(__file__).resolve().parent
EVID = HERE.parent / "evidence"
RESULTS = HERE / "results.json"
REPO = Path(os.environ.get("QO_REPO", "."))
EVID.mkdir(parents=True, exist_ok=True)

# produit -> restaurant (jeu de données seed.py)
RESTO = {**{p: 1 for p in range(1, 6)}, **{p: 2 for p in range(6, 11)}, **{p: 3 for p in range(11, 16)},
         **{p: 4 for p in range(16, 20)}, **{p: 5 for p in range(20, 24)}, 24: 6, 25: 6}


def reseed():
    subprocess.run([sys.executable, "seed.py"], cwd=REPO, env=os.environ.copy(), capture_output=True, check=True)


def money(text):
    m = re.search(r"(-?\d+(?:[.,]\d{1,2})?)", text.replace("−", "-"))
    return Decimal(m.group(1).replace(",", ".")) if m else None


class Ctx:
    """Contexte d'un cas de test : pages, preuves, verdict."""

    def __init__(self, tid, browser):
        self.id, self.browser = tid, browser
        self.n = 0
        self.files, self.lines, self._ctxs = [], [], []
        self.verdict = None

    # ---------------------------------------------------------------- navigateur
    def page(self, width=1280, height=900, video=False, tz="Europe/Paris"):
        kw = dict(viewport={"width": width, "height": height}, locale="fr-FR", timezone_id=tz)
        if video:
            kw.update(record_video_dir=str(EVID / "_video_tmp"), record_video_size={"width": 1000, "height": 700})
        ctx = self.browser.new_context(**kw)
        self._ctxs.append(ctx)
        pg = ctx.new_page()
        pg.set_default_timeout(8000)
        return pg

    def shot(self, page, label, full=True):
        self.n += 1
        name = f"{self.id}_{self.n:02d}_{label}.png"
        page.screenshot(path=str(EVID / name), full_page=full)
        self.files.append(name)
        return name

    def log(self, text):
        self.lines.append(text)

    # ---------------------------------------------------------------- API
    def api(self, method, path, json_body=None, raw=None, key=KEY, headers=None, label=None, show_body=True):
        h = dict(headers or {})
        if key:
            h["X-API-Key"] = key
        if json_body is not None or raw is not None:
            h["Content-Type"] = "application/json"
        data = raw if raw is not None else (json.dumps(json_body) if json_body is not None else None)
        r = requests.request(method, BASE + path, headers=h, data=data, allow_redirects=False, timeout=20)
        cmd = f"curl -i -X {method} " + " ".join(f"-H '{k}: {v}'" for k, v in h.items())
        if data is not None:
            cmd += f" -d '{data}'"
        cmd += f" {BASE}{path}"
        body = r.text
        if "json" in r.headers.get("Content-Type", ""):
            try:
                body = json.dumps(r.json(), indent=2, ensure_ascii=False)
            except Exception:
                pass
        elif len(body) > 400:
            body = body[:400] + "\n[… corps HTML tronqué …]"
        self.lines.append((f"# {label}\n" if label else "") + f"$ {cmd}\nHTTP {r.status_code} {r.reason} | Content-Type: {r.headers.get('Content-Type')}\n"
                          + (body if show_body else "[corps omis]") + "\n")
        return r

    # ---------------------------------------------------------------- verdicts
    def ok(self, obtenu):
        self.verdict = ("Pass", obtenu, "")

    def ko(self, obtenu, bug):
        self.verdict = ("Fail", obtenu, bug)

    def blocked(self, obtenu, bug=""):
        self.verdict = ("Blocked", obtenu, bug)

    def skip(self, obtenu, bug=""):
        self.verdict = ("Skipped", obtenu, bug)

    def check(self, cond, ok_msg, ko_msg, bug=""):
        (self.ok(ok_msg) if cond else self.ko(ko_msg, bug))

    def close(self):
        for c in self._ctxs:
            try:
                c.close()
            except Exception:
                pass


REGISTRY = []


def case(tid, reseed_db=True):
    def deco(fn):
        REGISTRY.append((tid, reseed_db, fn))
        return fn
    return deco


def run_all(only=None, results_path=RESULTS):
    from playwright.sync_api import sync_playwright
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for tid, do_reseed, fn in REGISTRY:
            if only and tid not in only:
                continue
            if do_reseed:
                reseed()
            t = Ctx(tid, browser)
            try:
                fn(t)
                if t.verdict is None:
                    raise RuntimeError("aucun verdict")
            except Exception as e:  # erreur du script de test, pas du produit
                t.verdict = ("ERROR", f"{type(e).__name__}: {e}", "")
                t.lines.append("[ERREUR DU SCRIPT]\n" + traceback.format_exc())
            finally:
                t.close()
            if t.lines:
                (EVID / f"{tid}.txt").write_text("\n".join(t.lines), encoding="utf-8")
                t.files.append(f"{tid}.txt")
            st, ob, bug = t.verdict
            results[tid] = dict(statut=st, obtenu=ob, bug=bug, preuves=t.files)
            print(f"{st:8} {tid:11} {ob[:110]}")
        browser.close()
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    return results


# ------------------------------------------------------------------ aides navigateur
def login(page, email="alice@example.com", pw="Password123!"):
    page.goto(BASE + "/login")
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", pw)
    page.click("form button.button")
    page.wait_for_load_state()


def flashes(page):
    return [e.inner_text().strip() for e in page.query_selector_all(".flash")]


def add(page, pid, qty=1, bypass=False):
    """Ajoute un produit depuis le menu de son restaurant (formulaire réel)."""
    page.goto(f"{BASE}/restaurant/{RESTO[pid]}")
    sel = f"form[action='/cart/add/{pid}']"
    if bypass:  # équivalent DevTools : retirer les contraintes HTML5
        page.evaluate("""(s) => { const i=document.querySelector(s+' input[name=quantity]'); i.removeAttribute('max'); i.removeAttribute('min'); }""", sel)
    page.fill(f"{sel} input[name=quantity]", str(qty))
    page.click(f"{sel} button")
    page.wait_for_load_state()
    return flashes(page)


def card_text(page, pid):
    return page.locator(f"article.card:has(form[action='/cart/add/{pid}'])").inner_text()


def stock_ui(page, pid):
    page.goto(f"{BASE}/restaurant/{RESTO[pid]}")
    m = re.search(r"Stock (-?\d+)", card_text(page, pid))
    return int(m.group(1))


def cart_totals(page):
    page.goto(BASE + "/cart")
    txt = page.inner_text("main")
    g = lambda lab: money(re.search(lab + r"\s*([-\d.,]+)\s*€", txt).group(1))
    return dict(sous_total=g("Sous-total"), livraison=g("Livraison"), total=g(r"Total"), texte=txt)


def checkout_summary(page):
    txt = page.inner_text("aside.summary")
    g = lambda lab: money(re.search(lab + r"\s*([-\d.,]+)\s*€", txt).group(1))
    return dict(sous_total=g("Sous-total"), livraison=g("Livraison"), reduction=g(r"Réduction\s*-"),
                total=g(r"\nTotal"), texte=txt)


def checkout(page, pay="card", coupon=None, cash=None, address=None, note=None, confirm=True):
    page.goto(BASE + "/checkout")
    if coupon:
        page.fill("input[name=coupon]", coupon)
        page.click("button[name=confirm][value='0']")
        page.wait_for_load_state()
    if address:
        val = page.evaluate("""(t) => { const o=[...document.querySelectorAll('select[name=address_id] option')].find(o=>o.textContent.includes(t)); return o? o.value : null }""", address)
        page.select_option("select[name=address_id]", val)
    if note:
        page.fill("textarea[name=customer_note]", note)
    page.select_option("#payment_method", pay)
    if cash is not None:
        page.fill("input[name=cash_received]", str(cash))
    if confirm:
        page.click("button[name=confirm][value='1']")
        page.wait_for_load_state()
    return page.url


def order_info(page):
    txt = page.inner_text("main")
    m = re.search(r"/orders/(\d+)", page.url)
    st = page.query_selector(".status")
    total = re.search(r"Total\s*([-\d.,]+)\s*€", txt)
    return dict(id=int(m.group(1)) if m else None, status=st.inner_text().strip() if st else None,
                total=money(total.group(1)) if total else None, texte=txt, flashes=flashes(page))


def order_ids(page):
    page.goto(BASE + "/orders")
    return [int(re.search(r"#(\d+)", e.inner_text()).group(1)) for e in page.query_selector_all("a.card.order > div:first-child > strong")]
