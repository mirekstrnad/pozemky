#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skener státních nabídek prodeje pozemků a nemovitostí -> statická webová stránka.

Běží v GitHub Actions: stáhne aktuální nabídky z ÚZSVM (nabidkamajetku.gov.cz)
přes veřejné JSON API a vygeneruje samostatný `public/index.html`, který se
publikuje na GitHub Pages. Data jsou vložena přímo do stránky (funguje bez API
i bez serveru).

Volitelně přidá obce/kraje z edesky.cz, pokud je nastavena proměnná EDESKY_KEY.
"""

import argparse
import datetime as _dt
import html
import json
import os
import time

try:
    import requests
except ImportError:
    requests = None

UZSVM_BASE = "https://www.nabidkamajetku.gov.cz"
UZSVM_LIST = UZSVM_BASE + "/api/Property/AuctionList"
UZSVM_ATTACH = UZSVM_BASE + "/api/Property/Attachment"
UZSVM_DETAIL = UZSVM_BASE + "/Home/AuctionDetail"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "cs,en;q=0.6",
    "Content-Type": "application/json",
}

OKRES_KRAJ = {
    "Praha": "Praha", "Benešov": "Středočeský", "Beroun": "Středočeský",
    "Kladno": "Středočeský", "Kolín": "Středočeský", "Kutná Hora": "Středočeský",
    "Mělník": "Středočeský", "Mladá Boleslav": "Středočeský", "Nymburk": "Středočeský",
    "Praha-východ": "Středočeský", "Praha-západ": "Středočeský", "Příbram": "Středočeský",
    "Rakovník": "Středočeský", "České Budějovice": "Jihočeský", "Český Krumlov": "Jihočeský",
    "Jindřichův Hradec": "Jihočeský", "Písek": "Jihočeský", "Prachatice": "Jihočeský",
    "Strakonice": "Jihočeský", "Tábor": "Jihočeský", "Domažlice": "Plzeňský",
    "Klatovy": "Plzeňský", "Plzeň-jih": "Plzeňský", "Plzeň-město": "Plzeňský",
    "Plzeň-sever": "Plzeňský", "Rokycany": "Plzeňský", "Tachov": "Plzeňský",
    "Cheb": "Karlovarský", "Karlovy Vary": "Karlovarský", "Sokolov": "Karlovarský",
    "Děčín": "Ústecký", "Chomutov": "Ústecký", "Litoměřice": "Ústecký", "Louny": "Ústecký",
    "Most": "Ústecký", "Teplice": "Ústecký", "Ústí nad Labem": "Ústecký",
    "Česká Lípa": "Liberecký", "Jablonec nad Nisou": "Liberecký", "Liberec": "Liberecký",
    "Semily": "Liberecký", "Hradec Králové": "Královéhradecký", "Jičín": "Královéhradecký",
    "Náchod": "Královéhradecký", "Rychnov nad Kněžnou": "Královéhradecký",
    "Trutnov": "Královéhradecký", "Chrudim": "Pardubický", "Pardubice": "Pardubický",
    "Svitavy": "Pardubický", "Ústí nad Orlicí": "Pardubický", "Havlíčkův Brod": "Vysočina",
    "Jihlava": "Vysočina", "Pelhřimov": "Vysočina", "Třebíč": "Vysočina",
    "Žďár nad Sázavou": "Vysočina", "Blansko": "Jihomoravský", "Brno-město": "Jihomoravský",
    "Brno-venkov": "Jihomoravský", "Břeclav": "Jihomoravský", "Hodonín": "Jihomoravský",
    "Vyškov": "Jihomoravský", "Znojmo": "Jihomoravský", "Jeseník": "Olomoucký",
    "Olomouc": "Olomoucký", "Prostějov": "Olomoucký", "Přerov": "Olomoucký",
    "Šumperk": "Olomoucký", "Kroměříž": "Zlínský", "Uherské Hradiště": "Zlínský",
    "Vsetín": "Zlínský", "Zlín": "Zlínský", "Bruntál": "Moravskoslezský",
    "Frýdek-Místek": "Moravskoslezský", "Karviná": "Moravskoslezský",
    "Nový Jičín": "Moravskoslezský", "Opava": "Moravskoslezský", "Ostrava-město": "Moravskoslezský",
}


def kraj_for(okres):
    return OKRES_KRAJ.get((okres or "").strip(), "Neuvedeno")


def parse_price(s):
    if not s:
        return None
    cleaned = "".join(ch for ch in str(s).replace(",", ".") if ch.isdigit() or ch == ".")
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def coarse_type(category):
    c = (category or "").lower()
    if "pozem" in c: return "Pozemek"
    if "byt" in c: return "Byt"
    if "stav" in c or "budov" in c or "dům" in c or "objekt" in c: return "Budova / stavba"
    if "garáž" in c or "garaz" in c: return "Garáž"
    return "Ostatní"


def normalize_uzsvm(a):
    aid = str(a.get("Id", "") or "")
    category = a.get("CategoryName", "") or ""
    district = a.get("DistrictName", "") or ""
    org = (a.get("Organization") or {}).get("u04Name", "") or ""
    image_id = a.get("ImageId", "") or ""
    st = {0: "Vyhlášeno", 1: "Probíhá", 2: "Ukončeno"}.get(a.get("AuctionStatus", 0), a.get("StatusName", ""))
    return {
        "zdroj": "ÚZSVM", "id": aid, "nazev": a.get("Name", "") or "",
        "popis": a.get("Description", "") or "", "kategorie": category,
        "typ": coarse_type(category), "okres": district, "kraj": kraj_for(district),
        "cena": parse_price(a.get("Price")),
        "cena_text": (f"{a.get('Price')} Kč" if a.get("Price") else "Neuvedena"),
        "stav": st, "organizace": org, "datum_od": a.get("StartDate", "") or "",
        "datum_do": a.get("EndDate", "") or "", "aktualizovano": a.get("UpdatedDate", "") or "",
        "obrazek": (f"{UZSVM_ATTACH}/{image_id}" if image_id else ""),
        "odkaz": (f"{UZSVM_DETAIL}/{aid}" if aid else UZSVM_BASE),
        "top": bool(a.get("TopProperty", False)),
    }


def fetch_uzsvm(status="active", max_listings=0, pause=0.3):
    if requests is None:
        raise RuntimeError("Chybí knihovna requests (pip install requests)")
    out, page, total = [], 1, None
    s = requests.Session(); s.headers.update(HEADERS)
    while True:
        body = {"Page": page, "PageSize": 100, "ListType": status, "Order": "Default",
                "OrderDesc": True, "CategoryId": 0, "LocalityId": 0, "MunicipialityId": 0,
                "CadastreId": 0, "AuctionModeId": 0, "Fulltext": "", "OrgId": "",
                "OrganizationType": 0, "OrganizationId": 0, "ContactZipCode": ""}
        r = s.post(UZSVM_LIST, json=body, timeout=60)
        if r.status_code != 200:
            print(f"  ! HTTP {r.status_code} na straně {page}"); break
        data = r.json()
        auctions = data.get("Auctions", []) or []
        if total is None:
            total = data.get("PropertyTotalCount", 0)
            print(f"  ÚZSVM ({status}): hlášeno {total} položek")
        if not auctions: break
        out.extend(auctions)
        print(f"  strana {page}: +{len(auctions)} ({len(out)}/{total})")
        if max_listings and len(out) >= max_listings: out = out[:max_listings]; break
        if total and len(out) >= total: break
        page += 1; time.sleep(pause)
    return [normalize_uzsvm(a) for a in out]


def fetch_edesky(api_key, query="záměr prodeje pozemku", pages=3):
    if requests is None or not api_key:
        return []
    out = []
    ENDPOINT = "https://edesky.cz/api/v1/documents"  # uprav dle své verze API
    for page in range(1, pages + 1):
        try:
            r = requests.get(ENDPOINT, params={"api_key": api_key, "query": query,
                             "page": page, "format": "json"},
                             headers={"User-Agent": HEADERS["User-Agent"]}, timeout=45)
            if r.status_code != 200:
                print(f"  ! edesky HTTP {r.status_code}"); break
            docs = r.json().get("documents") or r.json().get("data") or []
            if not docs: break
            for d in docs:
                nm = d.get("name") or d.get("title") or "Dokument úřední desky"
                out.append({"zdroj": "Obce/kraje (edesky)", "id": str(d.get("id", "")),
                    "nazev": nm, "popis": d.get("snippet", "") or "",
                    "kategorie": "Záměr prodeje (úřední deska)",
                    "typ": "Pozemek" if "pozem" in nm.lower() else "Ostatní",
                    "okres": d.get("dek_name") or d.get("board_name") or "", "kraj": "Neuvedeno",
                    "cena": None, "cena_text": "Viz dokument", "stav": "Zveřejněno",
                    "organizace": d.get("dek_name") or d.get("board_name") or "",
                    "datum_od": d.get("published_at", "") or d.get("date", ""), "datum_do": "",
                    "aktualizovano": d.get("published_at", "") or "", "obrazek": "",
                    "odkaz": d.get("url") or "https://edesky.cz", "top": False})
            print(f"  edesky strana {page}: +{len(docs)}"); time.sleep(0.4)
        except Exception as e:
            print(f"  ! edesky chyba: {e}"); break
    return out


WATCH_LINKS = [
    {"nazev": "ÚZSVM – všechny nabídky", "url": UZSVM_BASE + "/Home/Properties",
     "popis": "Kompletní portál nabídek státního majetku (zdroj tohoto webu)."},
    {"nazev": "Lesy ČR – prodej nemovitostí", "url": "https://pnm.lesycr.cz/",
     "popis": "Výběrová řízení Lesů ČR (pozemky, stavby). Ruční procházení."},
    {"nazev": "edesky.cz – štítek „Prodej“", "url": "https://edesky.cz/dokumenty?tag=Prodej",
     "popis": "Záměry prodeje na úředních deskách obcí a krajů."},
    {"nazev": "Správa železnic – prodej nemovitostí",
     "url": "https://www.spravazeleznic.cz/o-nas/prodej-nemovitosti",
     "popis": "Nabídky prodeje nepotřebného majetku Správy železnic."},
    {"nazev": "Registr smluv – kontrola výsledků",
     "url": "https://smlouvy.gov.cz/", "popis": "Ověření uzavřených kupních smluv."},
]

TEMPLATE = open(os.path.join(os.path.dirname(__file__), "template.html"),
                encoding="utf-8").read()


def build_html(records, meta):
    payload = json.dumps({"records": records, "meta": meta, "watch": WATCH_LINKS},
                         ensure_ascii=False)
    return TEMPLATE.replace("<!--__DATA__-->", html.escape(payload, quote=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="public/index.html")
    ap.add_argument("--status", default="active")
    ap.add_argument("--max", type=int, default=0)
    args = ap.parse_args()

    records, sources = [], []
    print("Stahuji nabídky z ÚZSVM…")
    statuses = ["active", "prepared"] if args.status == "active" else \
        (["active", "prepared", "closed"] if args.status == "all" else [args.status])
    for st in statuses:
        try:
            records.extend(fetch_uzsvm(status=st, max_listings=args.max))
        except Exception as e:
            print(f"  ! ÚZSVM ({st}) selhalo: {e}")
    sources.append("ÚZSVM")

    seen, dedup = set(), []
    for r in records:
        k = (r["zdroj"], r["id"])
        if k not in seen:
            seen.add(k); dedup.append(r)
    records = dedup

    edesky_key = os.environ.get("EDESKY_KEY", "").strip()
    if edesky_key:
        print("Stahuji edesky.cz…")
        ede = fetch_edesky(edesky_key)
        records.extend(ede)
        if ede: sources.append("Obce/kraje (edesky)")

    meta = {"generated": _dt.datetime.now().strftime("%d.%m.%Y %H:%M"),
            "sources": ", ".join(sources), "count": len(records), "mode": "live"}

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_html(records, meta))
    # JSON/CSV do stejné složky
    with open(os.path.join(out_dir or ".", "nabidky.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "records": records}, f, ensure_ascii=False, indent=2)

    print(f"\nHotovo: {len(records)} nabídek -> {args.out}")
    if not records:
        print("Pozor: nula nabídek může znamenat změnu API.")


if __name__ == "__main__":
    main()
