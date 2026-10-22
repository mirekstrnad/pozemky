---
title: Státní pozemky — aktualizace dat
source: BookStack Projekty, page 76
exported: 2026-10-22
language: cs
---

# Aktualizace dat

## Tlačítko „Aktualizovat data“

Deploy hook ve stránce **není** — tlačítko volá Pages Function na stejné doméně
(`POST /api/refresh`), která ověří heslo (`REFRESH_PASSWORD`) a teprve pak
spustí build přes `DEPLOY_HOOK`. Stejná doména → žádné CORS a tlačítko čte
skutečnou odpověď.

V prohlížeči:

- heslo se zeptá jen poprvé a po úspěchu si ho zapamatuje; po špatném hesle ho
  zapomene a zeptá se znovu,
- po kliknutí se tlačítko zablokuje a odpočítá 100 s, pak napíše „obnov stránku“,
- hlásí stav: Spouštím / Hotovo / Špatné heslo / Build běžel právě teď, zkus za
  N s / chyba N.

Doporučení: mít v Cloudflare nastavený KV binding `RL`, který omezuje frekvenci
buildů. Tlačítko nespouští nic jiného než nový build — data jsou jen veřejná
nabídka ÚZSVM.

## Jak aktualizovat data

- Na webu tlačítko **Aktualizovat data**, počkat 1–2 minuty a obnovit stránku.
- Nebo jakýkoli `git push` do `main` (Cloudflare build se spustí sám).
- Žádná automatická aktualizace není — denní cron v GitHub Actions je od
  17. 8. 2026 zakomentovaný. Proto stránka může hlásit stará data.
