---
title: Státní pozemky — vývoj, omezení a historie
source: BookStack Projekty, page 76
exported: 2026-10-22
language: cs
---

# Vývoj lokálně

```bash
git clone https://github.com/mirekstrnad/pozemky && cd pozemky
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scraper.py --out public/index.html --max 50   # rychlá zkouška
python3 -m http.server -d public 8000                          # http://localhost:8000
```

Tlačítko lokálně nefunguje (`/api/refresh` je Pages Function); šlo by přes
`npx wrangler pages dev public` s nastavenými proměnnými, ale není to potřeba.
Šablona se mění v `template.html`, nikdy v `public/index.html`.

# Omezení a známé problémy

- **Data mohou být stará**: build 23. 8. 2026 (627 nabídek, zdroj jen ÚZSVM,
  ověřeno na webu 22. 10. 2026) — stránka pak ukazuje červený pruh. Stačí
  kliknout na Aktualizovat data.
- **Souběžně žije stará kopie na GitHub Pages**
  (`https://mirekstrnad.github.io/pozemky/`). Workflow
  `.github/workflows/update.yml` se pořád spouští **při každém pushi do `main`**
  (a ručně) a nasazuje na GitHub Pages s Pythonem 3.12 — kromě Cloudflare buildu
  tedy každý push postaví i druhou kopii. README i docstring říkají, že GitHub
  Pages se už nepoužívá. Kandidát na úklid: workflow smazat nebo vypnout
  a v nastavení repa vypnout Pages.
- Placeholder `public/index.html` v repu pořád píše „Web se připraví po prvním
  běhu GitHub Actions“ — zastaralý text (na produkci ho přepíše build).
- Pokud ÚZSVM změní API, scraper nespadne, ale vygeneruje prázdný web (v logu
  buildu „nula nabídek může znamenat změnu API“). Při selhání jednoho stavu
  (`active`/`prepared`) pokračuje s ostatními.
- Kraj se dopočítává z názvu okresu; okres mimo tabulku dá „Neuvedeno“.
- Cena se parsuje z textu; „Neuvedena“ nabídky propadnou filtrem ceny.
- Data jsou vložená přímo do HTML → stránka má zhruba **1 MB** (627 nabídek)
  a s počtem nabídek roste; na mobilních datech se to pozná.
- edesky modul je neověřený odhad API.

# Historie

| Datum | Co se stalo |
|---|---|
| 16. 8. 2026 | Založení: placeholder, šablona dashboardu, scraper ÚZSVM a generátor stránky, README |
| 17. 8. 2026 | GitHub Actions workflow — build a nasazení na GitHub Pages; denní cron 5:00 UTC hned vypnutý, aktualizace ručně (workflow_dispatch) |
| 23. 8. 2026 | Přechod na **Cloudflare Pages**: `requirements.txt`, Pages Function `/api/refresh` (heslo, deploy hook jako secret, omezení frekvence přes KV), skutečné tlačítko Aktualizovat data místo odkazu na Actions, nové README |
| 23. 8. 2026 | `generated_iso` v metadatech (čas byl o 2 h posunutý, build běží v UTC), čas v místním čase, varovný pruh po 7 / 30 dnech |
| 22. 10. 2026 | Přidána dokumentace pro AI modely (`AGENTS.md`, `docs/wiki/`) |
