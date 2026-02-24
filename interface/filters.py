"""
filters.py — filter bar widget and filter state container
"""

from dataclasses import dataclass, field
from nicegui import ui

from data import ALL_STATES, ALL_PRODUCTS


# ── Filter state ────────────────────────────────────────────────────────────────


@dataclass
class FilterState:
    search: str = ""
    state: str = "All States"
    product: str = "All Products"
    min_loan: float | None = field(default=None)
    max_loan: float | None = field(default=None)
    min_credit: float | None = field(default=None)

    def as_kwargs(self) -> dict:
        return {
            "search": self.search,
            "state": self.state,
            "product": self.product,
            "min_loan": self.min_loan,
            "max_loan": self.max_loan,
            "min_credit": self.min_credit,
        }


# ── Filter bar ──────────────────────────────────────────────────────────────────


def build_filter_bar(state: FilterState, on_change: callable) -> None:
    """Render the full filter bar and wire up all change handlers."""

    with (
        ui.element("div")
        .classes("filter-bar")
        .style("display:flex;align-items:flex-end;flex-wrap:wrap")
    ):
        search = ui.input(
            placeholder="Search lenders, counties, products…",
            on_change=lambda _: _update("search", search.value or ""),
        ).style("width:280px")
        state_sel = ui.select(
            ["All States"] + ALL_STATES, value="All States", label="State"
        ).style("width:160px")
        product_sel = ui.select(
            ["All Products"] + ALL_PRODUCTS, value="All Products", label="Product Type"
        ).style("width:200px")
        min_loan = ui.number(label="Min Loan ($)", format="%.0f", min=0).style(
            "width:140px"
        )
        max_loan = ui.number(label="Max Loan ($)", format="%.0f", min=0).style(
            "width:140px"
        )
        credit = ui.number(
            label="My Credit Score", format="%.0f", min=300, max=850
        ).style("width:150px")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update(attr: str, value):
        setattr(state, attr, value)
        on_change()

    def _safe_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            return None

    # Always read from the component's .value after the event fires —
    # avoids dealing with GenericEventArguments payload differences.
    # search.on("input", lambda _: _update("search", search.value or ""))
    state_sel.on(
        "update:model-value",
        lambda _: _update("state", state_sel.value or "All States"),
    )
    product_sel.on(
        "update:model-value",
        lambda _: _update("product", product_sel.value or "All Products"),
    )
    min_loan.on(
        "update:model-value", lambda _: _update("min_loan", _safe_float(min_loan.value))
    )
    max_loan.on(
        "update:model-value", lambda _: _update("max_loan", _safe_float(max_loan.value))
    )
    credit.on(
        "update:model-value", lambda _: _update("min_credit", _safe_float(credit.value))
    )
