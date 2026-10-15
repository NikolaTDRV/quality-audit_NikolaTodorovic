#!/usr/bin/env bash
# Rejoue en ligne de commande (curl) les 8 bugs documentés dans docs/bug-reports/.
#
# Prérequis : curl, python3, application lancée sur BASE_URL, base FRAÎCHEMENT initialisée (python seed.py).
# Usage     : python seed.py && python run.py      (terminal 1)
#             bash docs/automation/reproduce_bugs.sh [BASE_URL]   (terminal 2)
# Le script crée des commandes et modifie des stocks : relancer `python seed.py` avant de le rejouer.
# Pour chaque bug : « REPRODUIT » si le comportement fautif est observé, « NON REPRODUIT » sinon.

BASE="${1:-http://127.0.0.1:5000}"
KEY="quickorder-demo-key"
BODY="$(mktemp)"; trap 'rm -f "$BODY"' EXIT
FAIL=0

req() { # METHOD PATH [JSON] -> code HTTP ; corps dans $BODY
  local m="$1" p="$2" d="${3:-}"
  if [ -n "$d" ]; then curl -s -o "$BODY" -w "%{http_code}" -X "$m" -H "X-API-Key: $KEY" -H "Content-Type: application/json" -d "$d" "$BASE$p"
  else curl -s -o "$BODY" -w "%{http_code}" -X "$m" -H "X-API-Key: $KEY" "$BASE$p"; fi
}
jget() { python3 - "$1" "$BODY" <<'PY'
import json, sys
try:
    v = json.load(open(sys.argv[2]))
    for k in sys.argv[1].split("."): v = v[k]
    print(v)
except Exception:
    print("")
PY
}
verdict() { # BUG "constat" CONDITION(0|1)
  if [ "$3" = "1" ]; then echo "  REPRODUIT      $1  $2"; else echo "  NON REPRODUIT  $1  $2"; FAIL=$((FAIL+1)); fi
}

curl -s -f -o /dev/null "$BASE/api/health" || { echo "Application injoignable sur $BASE" >&2; exit 2; }
echo "== Reproduction des bugs sur $BASE"

# BUG-001 : un paiement PayPal crée deux commandes
req GET /api/orders >/dev/null; n0=$(jget count)
req GET /api/products/1 >/dev/null; s0=$(jget stock)
c=$(req POST /api/orders '{"items":[{"product_id":1,"quantity":1}],"payment_method":"paypal"}')
req GET /api/orders >/dev/null; n1=$(jget count)
req GET /api/products/1 >/dev/null; s1=$(jget stock)
verdict BUG-001 "POST PayPal -> HTTP $c ; commandes $n0 -> $n1 (attendu +1) ; stock $s0 -> $s1 (attendu -1)" $([ $((n1-n0)) -eq 2 ] && echo 1 || echo 0)

# BUG-002 : restaurant fermé (Night Sushi, produit 24)
c=$(req POST /api/orders '{"items":[{"product_id":24,"quantity":1}],"payment_method":"card"}')
verdict BUG-002 "commande chez Night Sushi (FERMÉ) -> HTTP $c (attendu 409)" $([ "$c" = "201" ] && echo 1 || echo 0)

# BUG-003 : espèces insuffisantes
c=$(req POST /api/orders '{"items":[{"product_id":1,"quantity":1}],"payment_method":"cash","cash_received":1}')
ch=$(jget change_due)
verdict BUG-003 "espèces 1 EUR pour 14,89 EUR -> HTTP $c, monnaie à rendre $ch (attendu 400)" $([ "$c" = "201" ] && echo 1 || echo 0)

# BUG-004 : stock ignoré (Salmon Bowl : stock 2, on en commande 3 ; Veggie Burger : stock 0)
c=$(req POST /api/orders '{"items":[{"product_id":7,"quantity":3}],"payment_method":"card"}')
req GET /api/products/7 >/dev/null; st=$(jget stock)
c2=$(req POST /api/orders '{"items":[{"product_id":4,"quantity":1}],"payment_method":"card"}')
verdict BUG-004 "3 x Salmon Bowl (stock 2) -> HTTP $c, stock final $st ; Veggie Burger (stock 0) -> HTTP $c2 (attendu 409)" $([ "$c" = "201" ] && [ "$c2" = "201" ] && echo 1 || echo 0)

# BUG-005 : minimum de commande (Burger Factory : 20 EUR)
c=$(req POST /api/orders '{"items":[{"product_id":3,"quantity":1}],"payment_method":"card"}')
verdict BUG-005 "1 x Frites maison (3,50 EUR, minimum 20 EUR) -> HTTP $c (attendu 400)" $([ "$c" = "201" ] && echo 1 || echo 0)

# BUG-006 : ATLAS15 annoncé à 15 %
req POST /api/coupons/validate '{"code":"ATLAS15","subtotal":35.80}' >/dev/null
d=$(jget discount); p=$(jget discount_percent)
verdict BUG-006 "ATLAS15 sur 35,80 EUR -> remise $d (taux $p %) ; attendu 5.37 (15 %)" $([ "$d" = "3.58" ] && echo 1 || echo 0)

# BUG-007 : entrées mal formées -> erreur 500
c=$(req POST /api/coupons/validate '{"code":"WELCOME10","subtotal":"NaN"}')
c2=$(req POST /api/orders '[1]')
verdict BUG-007 "subtotal=\"NaN\" -> HTTP $c ; corps JSON tableau -> HTTP $c2 (attendu 400 / 400)" $([ "$c" = "500" ] && [ "$c2" = "500" ] && echo 1 || echo 0)

# BUG-008 : redirection ouverte après connexion
h=$(curl -s -i -o /dev/null -D - -X POST -d "email=alice@example.com&password=Password123!" "$BASE/login?next=https://example.org")
code=$(echo "$h" | head -1 | tr -d '\r' | awk '{print $2}')
loc=$(echo "$h" | grep -i '^location:' | tr -d '\r' | awk '{print $2}')
verdict BUG-008 "connexion avec ?next=https://example.org -> HTTP $code, Location: $loc (attendu : page interne)" $([ "$code" = "302" ] && [ "$loc" = "https://example.org" ] && echo 1 || echo 0)

echo
[ "$FAIL" -eq 0 ] && echo "8 bugs sur 8 reproduits." || echo "$FAIL bug(s) non reproduit(s)."
exit "$FAIL"
