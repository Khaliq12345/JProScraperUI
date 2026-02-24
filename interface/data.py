"""
data.py — loads lenders from JSON, normalizes shape, and exposes query helpers

Real API shape:
  {
    info: {
      lenderName, lenderUri, lenderLogoUri, lenderFirmTypes,
      creditBoxes: [
        { executionTypes: [{id, description}], propertyTypes: [{id, description}], ... }
      ]
    },
    contact: { email, phone, linkedInUrl }
  }

Normalized shape (what the rest of the app uses):
  {
    lenderName, lenderUri, lenderLogoUri,
    contact: { email, phone, linkedInUrl },
    creditBoxes: [
      { executionTypes: ["string", ...], propertyTypes: ["string", ...], ... }
    ]
  }
"""

import json
from pathlib import Path
from typing import Any

# ── Load ────────────────────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent / "lenders.json"


def load_lenders() -> list[dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)[0]


# ── Normalization ────────────────────────────────────────────────────────────────


def _extract_strings(items: list) -> list[str]:
    """
    Accepts either a list of strings OR a list of {id, description} objects
    and always returns a flat list of strings.
    """
    out = []
    for item in items or []:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            out.append(item.get("description") or item.get("id") or "")
    return [s for s in out if s]


def _normalize_credit_box(cb: dict) -> dict:
    return {
        **cb,
        "executionTypes": _extract_strings(cb.get("executionTypes", [])),
        "propertyTypes": _extract_strings(cb.get("propertyTypes", [])),
        "businessTypes": _extract_strings(cb.get("businessTypes", [])),
    }


def _normalize(raw: dict) -> dict:
    """
    Accept either the real API shape { info: {...}, contact: {...} }
    or the flat shape { lenderName, contact, ... } and return the flat shape.
    """
    # ── real API shape ────────────────────────────────────────────────────────
    if "info" in raw:
        info = raw["info"]
        return {
            "lenderName": info.get("lenderName", ""),
            "lenderUri": info.get("lenderUri"),
            "lenderLogoUri": info.get("lenderLogoUri"),
            "contact": raw.get("contact", {}),
            "creditBoxes": [
                _normalize_credit_box(cb) for cb in info.get("creditBoxes", [])
            ],
        }

    # ── already flat shape ────────────────────────────────────────────────────
    return {
        **raw,
        "creditBoxes": [_normalize_credit_box(cb) for cb in raw.get("creditBoxes", [])],
    }


LENDERS: list[dict[str, Any]] = [_normalize(r) for r in load_lenders()]


# ── Field extractors ────────────────────────────────────────────────────────────


def get_states(lender: dict) -> set[str]:
    return {
        fp.get("stateCode") or fp.get("description", "")
        for cb in lender.get("creditBoxes", [])
        for fp in cb.get("footprints", [])
        if fp.get("stateCode") or fp.get("description")
    }


def get_counties(lender: dict) -> set[str]:
    return {
        county["description"].lower()
        for cb in lender.get("creditBoxes", [])
        for fp in cb.get("footprints", [])
        for county in fp.get("types", [])
    }


def get_products(lender: dict) -> set[str]:
    products = set()
    for cb in lender.get("creditBoxes", []):
        for lpt in cb.get("loanProductTypes", []):
            products.add(lpt["description"].lower())
            for t in lpt.get("types", []):
                products.add(t["description"].lower())
    return products


# ── Derived option lists ─────────────────────────────────────────────────────────

ALL_STATES: list[str] = sorted({sc for l in LENDERS for sc in get_states(l)})

ALL_PRODUCTS: list[str] = sorted(
    {p for l in LENDERS for p in get_products(l) if len(p) > 3}
)


# ── Filtering ────────────────────────────────────────────────────────────────────


def _any_box_matches_numerics(
    lender: dict,
    min_loan: float | None,
    max_loan: float | None,
    min_credit: float | None,
) -> bool:
    for cb in lender.get("creditBoxes", []):
        cb_min = cb.get("minimumLoanAmount") or 0
        cb_max = cb.get("maximumLoanAmount") or float("inf")
        cb_cs = cb.get("minimumCreditScore") or 0

        loan_ok = (min_loan is None or cb_max >= min_loan) and (
            max_loan is None or cb_min <= max_loan
        )
        credit_ok = min_credit is None or cb_cs <= min_credit

        if loan_ok and credit_ok:
            return True
    return False


def filter_lenders(
    lenders: list[dict],
    *,
    search: str = "",
    state: str = "All States",
    product: str = "All Products",
    min_loan: float | None = None,
    max_loan: float | None = None,
    min_credit: float | None = None,
) -> list[dict]:
    results = []
    q = search.strip().lower()

    for lender in lenders:
        if q:
            haystack = lender.get("lenderName", "").lower()
            haystack += " " + (lender.get("contact") or {}).get("email", "").lower()
            haystack += " " + " ".join(get_counties(lender))
            haystack += " " + " ".join(get_products(lender))
            for cb in lender.get("creditBoxes", []):
                haystack += " " + (cb.get("notes") or "").lower()
            if q not in haystack:
                continue

        if state and state != "All States":
            if state not in get_states(lender):
                continue

        if product and product != "All Products":
            if product.lower() not in get_products(lender):
                continue

        has_numerics = any(v is not None for v in (min_loan, max_loan, min_credit))
        if has_numerics and not _any_box_matches_numerics(
            lender, min_loan, max_loan, min_credit
        ):
            continue

        results.append(lender)

    return results
