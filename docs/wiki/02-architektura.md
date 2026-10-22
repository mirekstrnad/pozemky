---
title: Státní pozemky — architektura a build
source: BookStack Projekty, page 76
exported: 2026-10-22
language: cs
---

# Architektura

```
git push do main ─┐
tlačítko na webu ─┴→ Cloudflare Pages build
                     pip install requests
                     python scraper.py --out public/index.html
                        ├─ ÚZSVM API → záznamy
                        ├─ (edesky.cz, jen s EDESKY_KEY)
                        └─ template.html + data → public/index.html, public/nabidky.json
                   → statická stránka pozemky.pages.dev
                   + Pages Function functions/api/refresh.js (/api/refresh)
```

- **`scraper.py`** — stáhne a normalizuje data a vloží je jako JSON do značky
  `<!--__DATA__-->` v šabloně. Stránka tedy nepotřebuje žádné API ani server;
  filtrování dělá prohlížeč. Vedle vznikne `nabidky.json` (meta + všechny
  záznamy), dostupné na `https://pozemky.pages.dev/nabidky.json`. Přepínače:
  `--out`, `--status` (`active` = aktivní + připravované, `all` = i ukončené,
  nebo jeden konkrétní stav), `--max` (strop počtu, pro zkoušení).
- **`template.html`** — celý dashboard (vzhled, filtry, tlačítko), bez knihoven.
- **`functions/api/refresh.js`** — Pages Function na stejné doméně, chráněné
  spuštění buildu.
- **`public/index.html`** v repozitáři je jen placeholder; skutečný se generuje
  při každém buildu.
- **`requirements.txt`** — jen `requests`.

## Konfigurace buildu (Cloudflare Pages)

| Položka | Hodnota |
|---|---|
| Framework preset | None |
| Build command | `pip install -r requirements.txt && python scraper.py --out public/index.html` |
| Build output directory | `public` |
| Production branch | `main` |
| `PYTHON_VERSION` | `3.11` — nutné, jinak build nenajde správný python/pip |

## Proměnné a tajemství (jen jména, hodnoty jsou v Cloudflare)

Cloudflare → projekt `pozemky` → Settings → Variables and secrets (typ Secret),
resp. Bindings:

| Jméno | Druh | Význam |
|---|---|---|
| `DEPLOY_HOOK` | Secret | URL deploy hooku (Settings → Builds & deployments). Je to sám o sobě spouštěcí token — nikdy do stránky ani do repa. |
| `REFRESH_PASSWORD` | Secret | heslo, které se zadává u tlačítka na webu |
| `EDESKY_KEY` | proměnná (volitelná) | API klíč edesky.cz; bez něj se modul přeskočí |
| `RL` | KV binding | KV namespace pro omezení frekvence buildů; doporučeno mít nastavený |
| `PYTHON_VERSION` | proměnná buildu | `3.11` |

Změna proměnných se projeví až **při dalším nasazení**.
