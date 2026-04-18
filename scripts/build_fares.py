"""
build_fares.py — CSV → Prolog preprocessor for NavLogic fare reasoning.

Reads `back-end/engine/electric_train_fares.csv` and emits
`back-end/engine/fares.pl` as a set of `fare(Agency, A, B, PriceTHB).`
facts keyed by KB station atoms (see `knowledge_base.pl`).

Rows are dropped when either endpoint is not represented in the KB,
when the agency is not modeled (MRTA Pink/Yellow, BEM Purple, SRTET
Red — none of these lines appear in the KB), or when the fare is a
same-station self-pair (A == B, price 0 noise).

Idempotent: run repeatedly; output file is overwritten from scratch.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "back-end" / "engine" / "electric_train_fares.csv"
OUT_PATH = ROOT / "back-end" / "engine" / "fares.pl"

# Agencies we model (CSV agency_id -> KB atom). BEM's Purple and
# SRTET's Red line share an agency with our modelled lines; we only
# emit rows whose stop_name prefix matches a station in the KB, so
# non-Blue/non-ARL rows get filtered by the stop map below.
AGENCY_MAP = {
    "BTSC": "bts",
    "BEM": "bem",
    "SRTET": "srtet",
}

# CSV English stop_name (the part after the `;` in "Thai;English") ->
# KB station atom (appears verbatim in knowledge_base.pl `station/2`).
#
# Only stations in the KB graph are listed. Everything else is dropped
# at ingest. When the KB grows, extend this table.
STOP_MAP = {
    # --- BTS Sukhumvit line ---
    "BTS Mo Chit":            "Mo Chit (N8)",
    "BTS Saphan Khwai":       "Saphan Khwai (N7)",
    "BTS Ari":                "Ari (N5)",
    "BTS Sanam Pao":          "Sanam Pao (N4)",
    "BTS Victory Monument":   "Victory Monument (N3)",
    "BTS Phaya Thai":         "Phaya Thai (N2)",
    "BTS Ratchathewi":        "Ratchathevi (N1)",
    "BTS Siam":               "Siam (CEN)",
    "BTS Chit Lom":           "Chit Lom (E1)",
    "BTS Phloen Chit":        "Phloen Chit (E2)",
    "BTS Nana":               "Nana (E3)",
    "BTS Asok":               "Asok (E4)",
    "BTS Phrom Phong":        "Phrom Phong (E5)",
    "BTS Thong Lo":           "Thong Lo (E6)",
    "BTS Ekkamai":            "Ekkamai (E7)",
    "BTS Phra Khanong":       "Phra Khanong (E8)",
    "BTS On Nut":             "On Nut (E9)",
    # --- BTS Silom line ---
    "BTS National Stadium":   "National Stadium (W1)",
    "BTS Ratchadamri":        "Ratchadamri (S1)",
    "BTS Sala Daeng":         "Sala Daeng (S2)",
    "BTS Chong Nonsi":        "Chong Nonsi (S3)",
    "BTS Surasak":            "Surasak (S5)",
    "BTS Saphan Taksin":      "Saphan Taksin (S6)",
    # --- MRT Blue line ---
    "MRT Phra Ram 9":         "Phra Ram 9 (BL20)",
    "MRT Phetchaburi":        "Phetchaburi (BL21)",
    "MRT Sukhumvit":          "Sukhumvit (BL22)",
    "MRT Queen Sirikit National Convention Centre": "Queen Sirikit (BL23)",
    "MRT Khlong Toei":        "Khlong Toei (BL24)",
    "MRT Lumphini":           "Lumphini (BL25)",
    "MRT Si Lom":             "Silom (BL26)",
    "MRT Sam Yan":            "Sam Yan (BL27)",
    "MRT Hua Lamphong":       "Hua Lamphong (BL28)",
    "MRT wat Mangkon":        "Wat Mangkon (BL29)",
    "MRT Sam Yot":            "Sam Yot (BL30)",
    "MRT Sanam Chai":         "Sanam Chai (BL31)",
    # --- Airport Rail Link ---
    "ARL Phaya Thai":         "Phaya Thai (A8)",
    "ARL Ratchaprarop":       "Ratchaprarop (A7)",
    "ARL Makkasan":           "Makkasan (A6)",
}


def english_name(stop_name: str) -> str:
    """CSV stop_name is "ThaiName;EnglishName" — take the English half."""
    if ";" in stop_name:
        return stop_name.split(";", 1)[1].strip()
    return stop_name.strip()


def quote(atom: str) -> str:
    """Emit a Prolog-quoted atom. Escape single quotes by doubling."""
    return "'" + atom.replace("'", "''") + "'"


def build() -> int:
    if not CSV_PATH.exists():
        sys.stderr.write(f"CSV not found: {CSV_PATH}\n")
        return 1

    total = 0
    kept: dict[tuple[str, str, str], int] = {}
    dropped_agency = 0
    dropped_stop = 0
    dropped_self = 0

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            agency_id = row["agency_id"].strip()
            agency = AGENCY_MAP.get(agency_id)
            if agency is None:
                dropped_agency += 1
                continue

            a_name = english_name(row["origin_stop_name"])
            b_name = english_name(row["destination_stop_name"])
            a_atom = STOP_MAP.get(a_name)
            b_atom = STOP_MAP.get(b_name)
            if a_atom is None or b_atom is None:
                dropped_stop += 1
                continue
            if a_atom == b_atom:
                dropped_self += 1
                continue

            try:
                price = int(round(float(row["price"])))
            except (TypeError, ValueError):
                continue

            key = (agency, a_atom, b_atom)
            prev = kept.get(key)
            if prev is None or price < prev:
                kept[key] = price

    lines: list[str] = []
    lines.append("/*")
    lines.append("====================================================================")
    lines.append("fares.pl — Auto-generated from electric_train_fares.csv.")
    lines.append("")
    lines.append("DO NOT EDIT BY HAND. Regenerate with `python scripts/build_fares.py`.")
    lines.append("")
    lines.append("One `fare(Agency, Origin, Destination, PriceTHB).` fact per")
    lines.append("(agency, station-pair) whose endpoints are both modelled in")
    lines.append("knowledge_base.pl. Non-modelled stations/agencies are dropped")
    lines.append("at ingest; see scripts/build_fares.py for the mapping.")
    lines.append("")
    lines.append(f"Source rows read:      {total}")
    lines.append(f"Facts emitted:         {len(kept)}")
    lines.append(f"Dropped (agency):      {dropped_agency}")
    lines.append(f"Dropped (stop):        {dropped_stop}")
    lines.append(f"Dropped (self-pair):   {dropped_self}")
    lines.append("====================================================================")
    lines.append("*/")
    lines.append("")
    lines.append(":- discontiguous fare/4.")
    lines.append("")

    by_agency: dict[str, list[tuple[str, str, int]]] = {}
    for (agency, a, b), p in kept.items():
        by_agency.setdefault(agency, []).append((a, b, p))

    for agency in sorted(by_agency):
        rows = sorted(by_agency[agency])
        lines.append(f"% --- {agency} ({len(rows)} fares) ---")
        for a, b, p in rows:
            lines.append(f"fare({agency}, {quote(a)}, {quote(b)}, {p}).")
        lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    sys.stderr.write(
        f"Wrote {OUT_PATH.relative_to(ROOT)}: {len(kept)} facts "
        f"(read {total}, dropped agency={dropped_agency} stop={dropped_stop} self={dropped_self})\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(build())
