# Státní nabídky prodeje pozemků a nemovitostí 🏛️

Web, který sbírá aktuální **státní nabídky prodeje pozemků a nemovitostí**
z portálu ÚZSVM (`nabidkamajetku.gov.cz`) a zobrazuje je jako přehledný
dashboard s filtry (typ, kraj, cena, stav) a vyhledáváním.

**Bez instalace čehokoli.** Scraper běží na buildových serverech Cloudflare
a výsledek je statická stránka — otevřeš prostě URL na mobilu i počítači.

## 🌐 Adresa webu

```
https://pozemky.pages.dev
```

## 🔄 Aktualizace dat

Nahoře na webu je tlačítko **„Aktualizovat data"**. Kliknutím spustí nový
build (scraper znovu stáhne data z ÚZSVM a přegeneruje stránku). Trvá to
1–2 minuty, pak stačí stránku obnovit.

Poprvé si tlačítko vyžádá heslo, dál si ho pamatuje v `localStorage`
prohlížeče, takže je to na jedno kliknutí. Po kliknutí se zablokuje
a odpočítává, aby nešlo omylem spustit dva buildy za sebou.

Každý `git push` do větve `main` spustí nasazení také.

## 🔐 Jak je to udělané

Deploy hook je bearer token — kdo ho najde ve zdroji stránky, může spouštět
buildy. Proto ve stránce **žádný není**.

Místo toho běží `functions/api/refresh.js` jako Pages Function ve stejném
originu. Ta drží hook jako secret projektu a přijme požadavek jen s správným
heslem v hlavičce `X-Refresh-Key`. Protože jde o stejný origin, není potřeba
CORS a tlačítko čte skutečnou odpověď (hotovo / špatné heslo / limit).

### Potřebné proměnné

Cloudflare dashboard → projekt `pozemky` → **Settings → Variables and secrets**,
obojí typu **Secret**:

| Název | Hodnota |
|---|---|
| `DEPLOY_HOOK` | URL deploy hooku `manual` (Settings → Builds & deployments) |
| `REFRESH_PASSWORD` | heslo, které se zadává na webu |

Bez nich vrací endpoint `500 {"error":"not_configured"}`. Změna proměnných
se projeví až **při dalším nasazení**.

### Volitelně: limit na frekvenci buildů

Function počítá s KV bindingem pojmenovaným `RL`. Když se v **Settings →
Bindings** přidá KV namespace pod tímto jménem, automaticky se zapne limit
1 build / 5 minut (odpověď `429` s `retry_after`). Bez bindingu se limit
přeskočí — v kódu není co měnit.

## ⚙️ Konfigurace buildu

| Položka | Hodnota |
|---|---|
| Framework preset | None |
| Build command | `pip install -r requirements.txt && python scraper.py --out public/index.html` |
| Build output directory | `public` |
| Production branch | `main` |
| `PYTHON_VERSION` | `3.11` — **nutné**, jinak build image nenajde správný `python`/`pip` |

## 🏘️ Obce a kraje (volitelné)

Pro doplnění záměrů prodeje z úředních desek obcí a krajů přes **edesky.cz**
přidej proměnnou `EDESKY_KEY` s API klíčem (stejná sekce Variables and secrets).

Modul je „nejlepší snaha" — endpoint/pole případně dolaď ve funkci
`fetch_edesky` v `scraper.py`.

## 🗂️ Co je v repozitáři

| Soubor | Účel |
|---|---|
| `scraper.py` | Stáhne data z ÚZSVM a vygeneruje `public/index.html` |
| `template.html` | Šablona dashboardu (vzhled, filtry, tlačítko aktualizace) |
| `functions/api/refresh.js` | Pages Function — chráněné spuštění buildu |
| `requirements.txt` | Python závislosti pro build |
| `public/index.html` | Vygenerovaný web (přepisuje se při každém běhu) |

## ℹ️ Zdroje a poznámky

- Primární zdroj: **ÚZSVM** – nabidkamajetku.gov.cz (veřejné JSON API).
- Další zdroje (Lesy ČR, Správa železnic, edesky, Registr smluv) jsou na webu
  jako odkazy k ruční kontrole — jejich portály nemají použitelné API.
- Data vždy ověř v oficiálním detailu nabídky. Tento web je pouze přehled.
