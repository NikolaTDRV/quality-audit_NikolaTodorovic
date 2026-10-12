# -*- coding: utf-8 -*-
"""Swagger UI : chargement, Authorize avec la clé de démonstration, exécution de GET /health."""
import os, sys
from playwright.sync_api import sync_playwright
BASE = os.getenv("QO_BASE", "http://127.0.0.1:5000")
pr = os.environ.get("HTTPS_PROXY")  # le CDN unpkg (swagger-ui-dist) est servi via le proxy de l'environnement
with sync_playwright() as pw:
    b = pw.chromium.launch(proxy={"server": pr, "bypass": "127.0.0.1,localhost"} if pr else None)
    pg = b.new_context(viewport={"width": 1280, "height": 900}).new_page(); pg.set_default_timeout(15000)
    pg.goto(BASE + "/docs/", wait_until="networkidle", timeout=60000); pg.wait_for_timeout(1500)
    n = pg.locator(".opblock").count(); pg.screenshot(path=sys.argv[1], full_page=True)
    pg.click("button.authorize"); pg.fill(".auth-container input[type=text]", "quickorder-demo-key")
    pg.click(".auth-btn-wrapper button.authorize"); pg.click("button.btn-done")
    pg.locator(".opblock-summary-get").first.click(); pg.click("button.try-out__btn"); pg.click("button.execute")
    pg.wait_for_selector(".live-responses-table"); pg.wait_for_timeout(800)
    code = pg.locator(".live-responses-table tbody .response-col_status").first.inner_text().split()[0]
    pg.screenshot(path=sys.argv[2], full_page=True)
    print(f"OPS={n} CODE={code}"); b.close()
