# AGENTS.md — Státní pozemky

Vstup pro AI modely a agenty. Podrobná dokumentace: [docs/wiki/README.md](docs/wiki/README.md).

## Co projekt je

Statický dashboard státních nabídek prodeje pozemků a nemovitostí z veřejného API
ÚZSVM (nabidkamajetku.gov.cz) — filtry, hledání, řazení, vše v prohlížeči.
Web: https://pozemky.pages.dev (Cloudflare Pages, projekt `pozemky`).

## Struktura

- `scraper.py` — stáhne a normalizuje data, vloží je do `template.html`
  a zapíše `public/index.html` + `public/nabidky.json`.
- `template.html` — celý dashboard (HTML + JS, bez knihoven). **Vzhled a chování
  se mění tady.**
- `functions/api/refresh.js` — Cloudflare Pages Function pro tlačítko
  „Aktualizovat data“ (ověří heslo, spustí deploy hook).
- `public/index.html` — **generuje se buildem a při každém buildu se přepíše.**
  Neupravovat ručně; v repu je jen placeholder.
- `.github/workflows/update.yml` — starý build na GitHub Pages (viz níž).
- `.github/workflows/monthly-refresh.yml` — 1. den v měsíci prázdný commit do
  `main`, čímž spustí build na Cloudflare (jediná automatická aktualizace).

## Build a nasazení

- Cloudflare Pages staví větev `main` při každém pushi:
  `pip install -r requirements.txt && python scraper.py --out public/index.html`,
  výstup `public`, `PYTHON_VERSION=3.11`.
- Každý push do `main` navíc spustí workflow `update.yml`, který nasadí druhou
  (starou) kopii na GitHub Pages.
- Lokálně: `python scraper.py --out public/index.html --max 50`
  a `python3 -m http.server -d public 8000`.

## Co nedělat

- Neupravovat `public/index.html` ručně — změny patří do `template.html`
  nebo `scraper.py`.
- Nikdy nedávat do repa ani do stránky hodnoty tajemství. Proměnné jsou jen
  v Cloudflare a znají se jménem: `DEPLOY_HOOK`, `REFRESH_PASSWORD`,
  `EDESKY_KEY`, KV binding `RL`.
- Stránka je statická a bez knihoven; zachovat to, pokud o změnu nikdo
  výslovně nepožádá.
- Data jsou jen přehled; závazné jsou detaily nabídek na nabidkamajetku.gov.cz.
