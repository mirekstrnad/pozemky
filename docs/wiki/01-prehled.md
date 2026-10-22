---
title: Státní pozemky — přehled a zdroje dat
source: BookStack Projekty, page 76
exported: 2026-10-22
language: cs
---

# Státní pozemky — přehled

Přehled **státních nabídek prodeje pozemků a nemovitostí** z portálu ÚZSVM na jedné
stránce s filtry a hledáním. Funguje na mobilu i počítači, nic se neinstaluje —
scraper běží při buildu na Cloudflare a výsledek je obyčejná statická stránka.

| | |
|---|---|
| Web | https://pozemky.pages.dev |
| Repozitář | https://github.com/mirekstrnad/pozemky (veřejný, větev `main`) |
| Hosting | Cloudflare Pages, projekt `pozemky` |
| Jazyk | Python 3.11 (scraper), čisté HTML + JS (dashboard), JS (Pages Function) |

> Web je jen přehled. Podmínky a termíny vždy ověřit v oficiálním detailu nabídky
> na nabidkamajetku.gov.cz.

## Co web umí

- **Karty nabídek** s fotkou (nebo ikonou podle typu), zdrojem, typem, stavem,
  štítkem TOP, cenou, okresem a krajem, nabízející organizací, termíny a odkazem
  **Zobrazit detail** na ÚZSVM.
- **Souhrn nahoře**: počet nabídek celkem, pozemky, budovy a byty, počet krajů.
- **Filtry**: zdroj, typ (Pozemek / Byt / Budova / stavba / Garáž / Ostatní), kraj,
  stav (Vyhlášeno / Probíhá / Ukončeno), cena od–do. **Hledání** v názvu, popisu,
  okresu, kraji, organizaci a kategorii. **Řazení**: nejnovější (TOP první), cena
  vzestupně / sestupně, konec nejdříve. Tlačítko **Zrušit filtry**.
- **Varování na stará data**: po 7 dnech oranžový pruh „Data jsou N dní stará“,
  po 30 dnech červený. Čas aktualizace se ukazuje v místním čase prohlížeče.
- **Tlačítko „Aktualizovat data“** — spustí nový build (viz
  [03-aktualizace-dat.md](03-aktualizace-dat.md)).
- **Další sledované zdroje** k ruční kontrole (nemají použitelné API): Lesy ČR
  (pnm.lesycr.cz), edesky.cz se štítkem „Prodej“, Správa železnic, Registr smluv,
  plus odkaz na celý portál ÚZSVM.
- Světlý i tmavý vzhled podle systému.

## Zdroje dat

**ÚZSVM — nabidkamajetku.gov.cz** (Úřad pro zastupování státu ve věcech
majetkových), veřejné JSON API bez klíče:

| Endpoint | K čemu |
|---|---|
| `POST https://www.nabidkamajetku.gov.cz/api/Property/AuctionList` | seznam nabídek, stránkuje se po 100 (`Page`, `PageSize`, `ListType`) |
| `/api/Property/Attachment/<ImageId>` | obrázek nabídky (prohlížeč ho tahá přímo z ÚZSVM) |
| `/Home/AuctionDetail/<Id>` | odkaz na detail nabídky |

Scraper stáhne seznamy `active` a `prepared` (připravované), odstraní duplicity,
okres převede na kraj podle vlastní tabulky okresů a kategorii zjednoduší na typ.
Mezi stránkami čeká 0,3 s. Volá se s prohlížečovým User-Agentem.

**Obce a kraje přes edesky.cz** (volitelné): když je nastavená proměnná
`EDESKY_KEY`, scraper hledá „záměr prodeje pozemku“ na úředních deskách
(3 stránky, `https://edesky.cz/api/v1/documents`). Modul je „nejlepší snaha“ —
endpoint ani pole nejsou ověřené (v kódu je poznámka „uprav dle své verze API“).
Podle veřejného webu teď není zapnutý: zdroje jsou jen „ÚZSVM“.
