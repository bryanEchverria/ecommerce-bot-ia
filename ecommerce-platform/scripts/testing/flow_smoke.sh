#!/usr/bin/env bash
set -euo pipefail
API="${API:-https://app.sintestesia.cl}"
# Puedes ajustar esta lista si tienes más tenants
TENANTS=(${TENANTS:-acme bravo})

CURL_OPTS=(-sS --http1.1)
ok(){ printf "\033[32m%s\033[0m\n" "$*"; }
warn(){ printf "\033[33m%s\033[0m\n" "$*"; }
err(){ printf "\033[31m%s\033[0m\n" "$*"; }
line(){ printf "\n\033[36m%s\033[0m\n" "—— $* ———————————————"; }

need(){ command -v "$1" >/dev/null || { err "Falta $1"; exit 1; }; }
j(){ jq -r "$1" 2>/dev/null || true; }
json(){ jq . 2>/dev/null || cat; }
req(){ local host="$1" method="$2" path="$3"; shift 3; curl "${CURL_OPTS[@]}" -H "Host: ${host}" -H "Accept: application/json" -X "$method" "$@" "${API%/}${path}"; }

need curl; need jq

line "Health"
h="$(curl -sS "${API%/}/health" || true)"; echo "$h" | json
echo "$h" | grep -q "healthy" && ok "Health OK" || warn "Health no OK"

declare -A ORD; declare -A TIDS_UNIQ

for t in "${TENANTS[@]}"; do
  host="${t}.sintestesia.cl"
  line "Tenant ${t} (${host}) – /flow/orders"
  o="$(req "$host" GET "/flow/orders" || true)"; echo "$o" | json
  cnt="$(echo "$o" | j '(.pedidos // .orders // []) | length')"; echo "Total pedidos: ${cnt:-0}"
  uniq="$(echo "$o" | j '(.pedidos // .orders // []) | map(.tenant_id) | unique | length')"
  TIDS_UNIQ["$t"]="${uniq:-0}"
  [[ "${uniq:-0}" -le 1 ]] && ok "Aislamiento OK (tenant_id único)" || err "¡Mezcla de tenant_id en la misma respuesta!"

  oid="$(echo "$o" | j '(.pedidos // .orders // [] | .[0].id)')"
  [[ -n "${oid}" && "${oid}" != "null" ]] && ORD["$t"]="$oid" && echo "order_id ejemplo: $oid" || warn "No hay order_id para probar /flow/return"

  line "Tenant ${t} – /flow/stats"
  s="$(req "$host" GET "/flow/stats" || true)"; echo "$s" | json
done

line "Simular /flow/return si existe order_id"
for t in "${TENANTS[@]}"; do
  oid="${ORD[$t]:-}"; host="${t}.sintestesia.cl"
  if [[ -n "${oid:-}" ]]; then
    r="$(req "$host" GET "/flow/return?status=SUCCESS&commerceOrder=${oid}" || true)"
    echo "[${t}] /flow/return →"; echo "$r" | json
  else
    warn "[${t}] sin order_id para /flow/return"
  fi
done

line "Resumen"
for t in "${TENANTS[@]}"; do
  echo "- ${t}: tenant_id únicos en /flow/orders = ${TIDS_UNIQ[$t]:-0}"
done
echo "API=$API  Tenants=${TENANTS[*]}"