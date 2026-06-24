#!/usr/bin/env python3
"""
Scarica il CSV pubblicato del foglio Google, calcola i conteggi (COUNT)
per le colonne richieste, suddivisi per fascia d'eta', e scrive data.json.
Le percentuali vengono calcolate lato client (cosi' il filtro per eta'
puo' ricalcolare tutto al volo). Solo stdlib: nessuna dipendenza esterna.
"""

import csv
import io
import json
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vRNGYPhLf0bh7DaxVKKfKAsGn3oHuwDOfD7ect3HYH96LzwwMBe1KbuMYXODuqUHXCXirOJQaCNxIZN"
    "/pub?gid=0&single=true&output=csv"
)

# Indici colonna (0-based) -> lettera del foglio
COL_C, COL_D, COL_E, COL_G, COL_H, COL_I, COL_N = 2, 3, 4, 6, 7, 8, 13

# Normalizzazione etichette eta' (colonna D = filtro)
AGE_RELABEL = {
    "Meno di 25 anni": "Under 25",
    "Oltre 65": "Over 65",
}
AGE_ORDER = ["Under 25", "25-34", "35-44", "45-54", "55-64", "Over 65"]

# Ordine logico imposto dove serve; per gli altri si ordina per frequenza.
ORDER_OVERRIDES = {
    "G": ["1-2 giorni", "3 giorni", "4 giorni", "5 giorni", "Più di 5 giorni"],
    "H": ["Meno di 15 minuti", "15-30 minuti", "30-45 minuti", "45-60 minuti", "Oltre 60 minuti"],
    "I": ["Meno di 5 km", "5-10 km", "10-20 km", "20-40 km", "Oltre 40 km", "Oltre 60 km"],
}

# Definizione dei grafici (titolo riscritto per il pubblico + tipo)
CHARTS = [
    {"key": "C", "idx": COL_C, "type": "donut",
     "title": "Per andare a lavoro o a studiare esci dal tuo comune?"},
    {"key": "E", "idx": COL_E, "type": "bars",
     "title": "Il mezzo che usi più spesso"},
    {"key": "N", "idx": COL_N, "type": "bars",
     "title": "Il problema principale negli spostamenti quotidiani"},
    {"key": "G", "idx": COL_G, "type": "columns",
     "title": "Quanti giorni a settimana fai questo spostamento"},
    {"key": "H", "idx": COL_H, "type": "columns",
     "title": "Quanto tempo impieghi mediamente"},
    {"key": "I", "idx": COL_I, "type": "columns",
     "title": "Quanti chilometri percorri ogni giorno (andata e ritorno)"},
]


def load_rows():
    if len(sys.argv) > 1 and sys.argv[1] == "--local":
        with open("data_raw.csv", encoding="utf-8") as f:
            return list(csv.reader(f))
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8")
    return list(csv.reader(io.StringIO(text)))


def cell(row, idx):
    return (row[idx] if idx < len(row) else "").strip()


def main():
    rows = load_rows()
    data = rows[1:]

    # Conteggio respondenti per fascia d'eta'
    age_count = defaultdict(int)
    for r in data:
        age = cell(r, COL_D)
        age = AGE_RELABEL.get(age, age)
        if age:
            age_count[age] += 1
    ages = [a for a in AGE_ORDER if a in age_count]

    out_charts = []
    for ch in CHARTS:
        idx = ch["idx"]
        # by_age[fascia][categoria] = conteggio
        by_age = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        for r in data:
            age = AGE_RELABEL.get(cell(r, COL_D), cell(r, COL_D))
            val = cell(r, idx)
            if not val or not age:
                continue
            by_age[age][val] += 1
            totals[val] += 1

        # Ordine categorie
        if ch["key"] in ORDER_OVERRIDES:
            cats = [c for c in ORDER_OVERRIDES[ch["key"]] if c in totals]
            cats += [c for c in totals if c not in cats]  # eventuali residui
        else:
            cats = [c for c, _ in sorted(totals.items(), key=lambda kv: -kv[1])]

        out_charts.append({
            "key": ch["key"],
            "type": ch["type"],
            "title": ch["title"],
            "categories": cats,
            "by_age": {a: {c: by_age[a].get(c, 0) for c in cats} for a in ages},
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "total": len(data),
        "small_sample_threshold": 15,
        "ages": ages,
        "age_count": {a: age_count[a] for a in ages},
        "charts": out_charts,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(data)} risposte -> data.json ({len(out_charts)} grafici, {len(ages)} fasce d'età)")


if __name__ == "__main__":
    main()
