"""Read-only, anonymised HTTP API over the Licita spine, for n8n to orchestrate.

Licita stays the system of record; this exposes two views and never writes:
  GET /health                      spine id, data dates
  GET /radar?hospital=H-xxxx&flags=start_now,due_6m,verify&limit=50
  GET /deserted?hospital=H-xxxx&since=2025-01-01&outcome=not_republished&limit=50

Anonymity (same rule as Licita): no buyer, region or tribunal is named in anything this serves.
Hospitals are opaque keyed codes (H-xxxx), contract ids become keyed tokens (C-…), titles are scrubbed with
Licita's keyed denylist plus a pattern for file references, and links, suppliers and NIFs are dropped.
Budgets are rounded to the nearest €1,000. Someone with the public PLACSP archive could still match
dates and budgets; the goal is that nothing here names anyone.

Run with Licita's environment:
  uv run --project ~/Projects/licita python api/server.py
"""
from __future__ import annotations

import glob
import hashlib
import hmac
import json
import os
import re
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import duckdb
from licita import anon

LICITA = Path(os.environ.get("LICITA_HOME", Path.home() / "Projects/licita"))
SPINE = os.environ.get("LICITA_SPINE") or sorted(glob.glob(str(LICITA / "spines/spine_*.duckdb")))[-1]
PORT = int(os.environ.get("PORT", "8787"))
HOST = os.environ.get("HOST", "127.0.0.1")   # 0.0.0.0 only inside a container network
FLAGS = {"start_now", "due_6m", "verify", "covered", "ok", "lapsed", "one_off"}
OUTCOMES = {"not_republished", "deserted_again", "awarded"}

KEY = anon.load_key(LICITA / "private" / "anon.key")
if KEY is None:
    raise SystemExit("no Licita anonymity key (private/anon.key): refusing to serve un-anonymised data")
HASHES = anon.load_hashes(LICITA / "anon" / "denylist.sha256")
BUYERS = tomllib.loads((LICITA / "profiles/local.toml").read_text())["buyers"]


def mac(s: str) -> str:
    return hmac.new(KEY, s.encode(), hashlib.sha256).hexdigest()


# Keyed-hash codes: they say nothing about which profile entry they are, or how many there are.
CODES = {k: f"H-{mac('buyer:' + k)[:4]}" for k in BUYERS}
BY_CODE = {v: k for k, v in CODES.items()}

REF_RE = re.compile(r"[A-Za-z]{0,6}\d[\w.º]*(?:[-/][\w.º]+){2,}|\b\d{8,}\b")   # file numbers
# Generic Spanish health-administration phrases that point at a region once the place name is gone.
ORG_RES = [(re.compile(r"Gerencia Regional(?: de \w+)?(?: de \[…\])?", re.I), "[servicio regional de salud]"),
           (re.compile(r"Área de Salud[^.,;:)\"]*", re.I), "[área de salud]"),
           (re.compile(r"Sistema P[úu]blico de Salud de Salud", re.I), "[sistema público de salud]"),
           (re.compile(r"centros? de salud .*?(?=,? dependientes|[;()]|$)", re.I), "[centros de salud]"),
           (re.compile(r"\[…\]\s+(?:Oeste|Este|Norte|Sur|Centro)\b"), "[…]"),
           (re.compile(r"\b[A-Z]?\d{4}/\d{3,}\b|\b\d{1,4}/20\d{2}\b"), "[ref]")]
# Extra local names (health centres, area acronyms) kept in Licita's gitignored private folder.
EXTRA_FILE = LICITA / "private" / "scrub_extra.txt"
EXTRA_NORM = ({anon.normalise(x) for x in EXTRA_FILE.read_text().splitlines() if x.strip()}
              if EXTRA_FILE.is_file() else set())
WORD_RE = re.compile(r"\w+")

con = duckdb.connect(SPINE, read_only=True)


def token(kind: str, value) -> str | None:
    return None if value is None else f"{kind}-{mac(f'{kind}:{value}')[:8]}"


def scrub(text: str | None) -> str | None:
    """Replace denylisted 1–3 word phrases with […] and file references with [ref]."""
    if not text:
        return text
    text = REF_RE.sub("[ref]", text)
    words = list(WORD_RE.finditer(text))
    hit = [False] * len(words)
    for n in range(1, anon.MAX_WORDS + 1):
        for i in range(len(words) - n + 1):
            phrase = anon.normalise(" ".join(w.group() for w in words[i:i + n]))
            if phrase and (mac(phrase) in HASHES or phrase in EXTRA_NORM):
                hit[i:i + n] = [True] * n
    out, pos, i = [], 0, 0
    while i < len(words):
        if not hit[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(words) and hit[j + 1]:
            j += 1
        out += [text[pos:words[i].start()], "[…]"]
        pos, i = words[j].end(), j + 1
    out.append(text[pos:])
    text = "".join(out)
    for rx, repl in ORG_RES:
        text = rx.sub(repl, text)
    return re.sub(r"(?:\[…\][\s,.-]*){2,}", "[…] ", text).strip()


def k1000(x):
    return None if x is None else round(x / 1000) * 1000


def rows(sql: str, params: list) -> list[dict]:
    # Dates go out as ISO strings, cast in SQL (duckdb's Python datetimes need pytz).
    cur = con.cursor().execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def hospital_of(q: dict) -> str:
    code = q.get("hospital", "")
    if code not in BY_CODE:
        raise KeyError(code)
    return code


def health(_: dict) -> dict:
    meta = rows("select run_id, as_of::varchar as as_of, data_through::varchar as data_through, "
                "schema_version from meta", [])[0]
    return {"ok": True, **meta}


def radar(q: dict) -> dict:
    code = hospital_of(q)
    flags = [f for f in q.get("flags", "start_now,due_6m,verify").split(",") if f in FLAGS]
    limit = min(int(q.get("limit", 50)), 500)
    raw = rows(f"""
        select folder_id, title, cpv2, procedure,
               award_d::date::varchar as award_d, end_initial::date::varchar as end_initial,
               end_max::date::varchar as end_max, start_by::varchar as start_by, months_to_end,
               lead_days, prep_days, annual_budget, min_bids, max_bids,
               flag, successor_status, match_confidence, successor_folder, successor_title, truth_status
        from radar where hospital = ? and flag in ({",".join("?" * len(flags))})
        order by case flag when 'start_now' then 0 when 'verify' then 1 else 2 end, start_by nulls last
        limit ?""", [BY_CODE[code], *flags, limit])
    items = []
    for r in raw:
        items.append({"hospital": code, "contract_ref": token("C", r.pop("folder_id")),
                      "successor_ref": token("C", r.pop("successor_folder")), **r,
                      "title": scrub(r["title"]), "successor_title": scrub(r["successor_title"]),
                      "annual_budget": k1000(r["annual_budget"])})
    return {"hospital": code, "name": f"Public hospital {code}", "flags": flags,
            "as_of": health({})["as_of"], "count": len(items), "items": items}


def deserted(q: dict) -> dict:
    code = hospital_of(q)
    nif = BUYERS[BY_CODE[code]]["nif"]
    since = q.get("since", "2000-01-01")
    outcomes = [o for o in q.get("outcome", "not_republished,deserted_again").split(",") if o in OUTCOMES]
    limit = min(int(q.get("limit", 50)), 500)
    raw = rows(f"""
        select folder_id, lot_id, title, cpv4, procedure, budget,
               deserted_date::date::varchar as deserted_date, outcome, republished_folder, republished_title,
               bids_after, market_n, market_median_bids, round(market_single_bid_rate, 3) as market_single_bid_rate
        from deserted where buyer_nif = ? and deserted_date >= ?::timestamp
          and outcome in ({",".join("?" * len(outcomes))})
        order by deserted_date desc limit ?""", [nif, since, *outcomes, limit])
    items = []
    for r in raw:
        items.append({"hospital": code, "contract_ref": token("C", r.pop("folder_id")),
                      "republished_ref": token("C", r.pop("republished_folder")), **r,
                      "title": scrub(r["title"]), "republished_title": scrub(r["republished_title"]),
                      "budget": k1000(r["budget"])})
    return {"hospital": code, "name": f"Public hospital {code}", "count": len(items), "items": items}


ROUTES = {"/health": health, "/radar": radar, "/deserted": deserted}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        fn = ROUTES.get(url.path)
        q = {k: v[-1] for k, v in parse_qs(url.query).items()}
        try:
            status, body = (200, fn(q)) if fn else (404, {"error": "not found", "routes": list(ROUTES)})
        except (KeyError, ValueError) as e:
            status, body = 400, {"error": f"bad parameter: {e}"}
        data = json.dumps(body, ensure_ascii=False, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"licita-api on http://{HOST}:{PORT} reading {Path(SPINE).name}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
