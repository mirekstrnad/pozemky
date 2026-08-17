# Státní nabídky prodeje pozemků a nemovitostí 🏛️

Automaticky aktualizovaný web, který sbírá aktuální **státní nabídky prodeje
pozemků a nemovitostí** z portálu ÚZSVM (`nabidkamajetku.gov.cz`) a zobrazuje je
jako přehledný dashboard s filtry (typ, kraj, cena, stav) a vyhledáváním.

**Bez instalace čehokoli.** Scraper běží zdarma na serverech GitHubu (GitHub
Actions) každé ráno a výsledek publikuje na GitHub Pages — otevřeš prostě URL na
mobilu i počítači.

## 🌐 Adresa webu

Po prvním úspěšném běhu bude web zde:

```
https://mirekstrnad.github.io/pozemky/
```

## ⚙️ Jednorázové nastavení (2 kroky, ~1 minuta)

GitHub kvůli bezpečnosti vyžaduje dvě povolení, která nejde zapnout kódem:

1. **Settings → Actions → General → Workflow permissions** →
   zvol **„Read and write permissions"** → Save.
2. **Settings → Pages → Build and deployment → Source** →
   zvol **„GitHub Actions"** (workflow se to většinou nastaví sám).

Pak jdi do záložky **Actions**, otevři workflow *„Aktualizace nabídek…"* a klikni
**Run workflow** (nebo počkej na ranní automatický běh). Po doběhnutí (zelená
fajfka) je web živý na adrese výše.

## 🔁 Jak často se aktualizuje

Každý den v **05:00 UTC** (07:00 letního / 06:00 zimního času v ČR). Frekvenci
změníš v `.github/workflows/update.yml` v řádku `cron`. Kdykoli můžeš spustit
ručně tlačítkem **Run workflow**.

## 🏘️ Obce a kraje (volitelné)

Pro doplnění záměrů prodeje z úředních desek obcí a krajů přes **edesky.cz**:

1. Vyžádej si API klíč na edesky.cz.
2. **Settings → Secrets and variables → Actions → New repository secret**,
   název `EDESKY_KEY`, hodnota = tvůj klíč.

Modul je „nejlepší snaha" — endpoint/pole případně dolaď ve funkci
`fetch_edesky` v `scraper.py`.

## 🗂️ Co je v repozitáři

| Soubor | Účel |
|---|---|
| `scraper.py` | Stáhne data z ÚZSVM a vygeneruje `public/index.html` |
| `template.html` | Šablona dashboardu (vzhled + filtry) |
| `.github/workflows/update.yml` | Denní běh a publikace na Pages |
| `public/index.html` | Vygenerovaný web (přepisuje se při každém běhu) |

## ℹ️ Zdroje a poznámky

- Primární zdroj: **ÚZSVM** – nabidkamajetku.gov.cz (veřejné JSON API).
- Další zdroje (Lesy ČR, Správa železnic, edesky, Registr smluv) jsou na webu
  jako odkazy k ruční kontrole — jejich portály nemají použitelné API.
- Data vždy ověř v oficiálním detailu nabídky. Tento web je pouze přehled.
