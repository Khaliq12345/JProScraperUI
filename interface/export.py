"""
export.py — builds an Excel file from filtered lender data using pandas
"""

import io
import pandas as pd


# ── Flatten helpers ─────────────────────────────────────────────────────────────


def _join(items: list, sep=", ") -> str:
    return sep.join(str(i) for i in items if i) if items else "—"


def _products(cb: dict) -> str:
    out = []
    for lpt in cb.get("loanProductTypes", []):
        for t in lpt.get("types", []):
            out.append(t["description"])
        if not lpt.get("types"):
            out.append(lpt["description"])
    return _join(out)


def _footprint(cb: dict) -> str:
    parts = []
    for fp in cb.get("footprints", []):
        sc = fp.get("stateCode") or fp.get("description", "")
        counties = [c["description"] for c in fp.get("types", [])]
        parts.append(f'{sc}: {", ".join(counties)}')
    return " | ".join(parts) if parts else "—"


def _fmt_currency(val) -> str:
    if val is None:
        return "—"
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:,}"


def _fmt_pct(val) -> str:
    return f"{val*100:.0f}%" if val is not None else "—"


# ── Flatten lenders → rows ──────────────────────────────────────────────────────


def _flatten(lenders: list[dict]) -> list[dict]:
    rows = []
    for lender in lenders:
        c = lender.get("contact", {})
        base = {
            "Lender Name": lender.get("lenderName", ""),
            "Website": lender.get("lenderUri", "") or "—",
            "Email": c.get("email", "") or "—",
            "Phone": c.get("phone", "") or "—",
        }
        boxes = lender.get("creditBoxes", []) or [{}]
        for cb in boxes:
            rows.append(
                {
                    **base,
                    "Credit Box": cb.get("name", "—"),
                    "Box Type": cb.get("creditBoxType", "—"),
                    "Min Loan": _fmt_currency(cb.get("minimumLoanAmount")),
                    "Max Loan": _fmt_currency(cb.get("maximumLoanAmount")),
                    "Max Leverage": _fmt_pct(cb.get("maxLeverage")),
                    "Min Credit Score": (
                        str(cb["minimumCreditScore"])
                        if cb.get("minimumCreditScore")
                        else "—"
                    ),
                    "Min Annual Revenue": _fmt_currency(cb.get("minimumAnnualRevenue")),
                    "Min Time in Biz": (
                        f'{cb["minimumTimeInBusiness"]} mo'
                        if cb.get("minimumTimeInBusiness")
                        else "—"
                    ),
                    "Loan Products": _products(cb),
                    "Property Types": _join(cb.get("propertyTypes", [])),
                    "Execution Types": _join(cb.get("executionTypes", [])),
                    "Business Types": _join(cb.get("businessTypes", [])),
                    "Footprint": _footprint(cb),
                    "Notes": cb.get("notes") or "—",
                }
            )
    return rows


# ── Main export function ────────────────────────────────────────────────────────


def build_excel(lenders: list[dict]) -> bytes:
    rows = _flatten(lenders)
    df = pd.DataFrame(rows)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Lenders")

        ws = writer.sheets["Lenders"]

        # Column widths
        col_widths = {
            "A": 28,
            "B": 30,
            "C": 28,
            "D": 18,  # lender info
            "E": 18,
            "F": 10,
            "G": 12,
            "H": 12,  # credit box basics
            "I": 14,
            "J": 16,
            "K": 18,
            "L": 16,  # numeric criteria
            "M": 30,
            "N": 22,
            "O": 18,
            "P": 20,  # types
            "Q": 50,
            "R": 35,  # footprint, notes
        }
        for col, width in col_widths.items():
            ws.column_dimensions[col].width = width

        # Freeze header row
        ws.freeze_panes = "A2"

        # Auto-filter
        ws.auto_filter.ref = ws.dimensions

    buf.seek(0)
    return buf.read()
