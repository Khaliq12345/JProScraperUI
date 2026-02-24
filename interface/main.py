"""
main.py — entry point for the Lender Research Dashboard

Run:
    pip install nicegui openpyxl
    python main.py
"""

import tempfile, os
from nicegui import ui

import styles
from data import LENDERS, filter_lenders
from filters import FilterState, build_filter_bar
from components import render_lender_card, render_empty_state, render_pagination
from export import build_excel

# ── Bootstrap ───────────────────────────────────────────────────────────────────

styles.inject()

filter_state = FilterState()
PAGE_SIZE = 10
current_page = {"n": 1}  # mutable int via dict so lambdas can write to it


# ── Layout ───────────────────────────────────────────────────────────────────────

with ui.element("div").classes("mx-auto").style("min-height:100vh"):

    # Header
    with ui.element("div").classes("dash-header"):
        with ui.element("div").style(
            "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px"
        ):
            with ui.element("div"):
                ui.html('<h1 class="dash-title">Lender Research</h1>')
                ui.html(
                    f'<p class="dash-subtitle">'
                    f"// {len(LENDERS)} lenders loaded · search, filter, explore"
                    f"</p>"
                )
            # Download button — placed in header
            dl_btn = ui.button(
                "⬇ Export to Excel", on_click=lambda: download_excel()
            ).style(
                "background:linear-gradient(135deg,#4fffb0,#7b61ff);"
                "color:#0d0f14;font-weight:700;font-family:'Syne',sans-serif;"
                "border:none;border-radius:8px;padding:10px 20px;cursor:pointer;"
                "font-size:.85rem;letter-spacing:.02em;"
            )

    # Filter bar
    build_filter_bar(filter_state, on_change=lambda: go_page(1))

    # Results container
    results_area = ui.element("div").classes("results-area")


# ── Pagination helper ────────────────────────────────────────────────────────────


def go_page(n: int):
    current_page["n"] = n
    refresh()


# ── Download ─────────────────────────────────────────────────────────────────────


def download_excel():
    matched = filter_lenders(LENDERS, **filter_state.as_kwargs())
    data = build_excel(matched)
    # Write to a temp file and serve it
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    tmp.write(data)
    tmp.close()
    ui.download(tmp.name, "lenders_export.xlsx")


# ── Refresh ──────────────────────────────────────────────────────────────────────


def refresh() -> None:
    results_area.clear()
    matched = filter_lenders(LENDERS, **filter_state.as_kwargs())
    total = len(matched)
    page = current_page["n"]
    total_pages = max(1, -(-total // PAGE_SIZE))  # ceiling division

    # Clamp page if filters reduced total
    if page > total_pages:
        current_page["n"] = 1
        page = 1

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    paged = matched[start:end]

    with results_area:
        # Count + page info
        ui.html(
            f'<p class="results-count">'
            f"<span>{total}</span> lenders match · "
            f"showing <span>{start+1}–{min(end,total)}</span> · "
            f"page <span>{page}</span> of <span>{total_pages}</span>"
            f"</p>"
        )

        if not matched:
            render_empty_state()
        else:
            for lender in paged:
                render_lender_card(lender)

            # Pagination controls
            if total_pages > 1:
                render_pagination(page, total_pages, go_page)


# Initial render
refresh()

# ── Run ──────────────────────────────────────────────────────────────────────────

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Lender Research Dashboard", dark=True, port=8080)
