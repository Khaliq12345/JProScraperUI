"""
components.py — reusable NiceGUI UI components for the lender dashboard
"""

from nicegui import ui


# ── Formatting helpers ──────────────────────────────────────────────────────────


def fmt_currency(val) -> str:
    if val is None:
        return "—"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,}"


def fmt_leverage(val) -> str:
    return f"{val * 100:.0f}%" if val is not None else "—"


def fmt_months(val) -> str:
    return f"{val} mo" if val is not None else "—"


# ── Sub-components ──────────────────────────────────────────────────────────────


def _tags_html(items: list[str], css_class: str = "") -> str:
    return (
        '<div class="tags">'
        + "".join(f'<span class="tag {css_class}">{i}</span>' for i in items)
        + "</div>"
    )


def _stat_grid_html(stats: list[tuple[str, str]]) -> str:
    inner = "".join(
        f'<div class="stat-item">'
        f'<span class="stat-label">{label}</span>'
        f'<span class="stat-value">{val}</span>'
        f"</div>"
        for label, val in stats
    )
    return f'<div class="stat-grid">{inner}</div>'


def _section_label(text: str, extra_style: str = "") -> str:
    return f'<div class="section-label" style="{extra_style}">{text}</div>'


# ── Credit-box card ─────────────────────────────────────────────────────────────


def render_credit_box(cb: dict) -> None:
    with ui.element("div").classes("cb-box"):
        ui.html(
            f'<div class="cb-name">'
            f'{cb["name"]} '
            f'<span style="opacity:.5;font-size:.75em">({cb.get("creditBoxType", "")})</span>'
            f"</div>"
        )

        stats = [
            ("Min Loan", fmt_currency(cb.get("minimumLoanAmount"))),
            ("Max Loan", fmt_currency(cb.get("maximumLoanAmount"))),
            ("Max Leverage", fmt_leverage(cb.get("maxLeverage"))),
            (
                "Min Credit",
                str(cb["minimumCreditScore"]) if cb.get("minimumCreditScore") else "—",
            ),
            ("Min Revenue", fmt_currency(cb.get("minimumAnnualRevenue"))),
            ("Min TIB", fmt_months(cb.get("minimumTimeInBusiness"))),
        ]
        ui.html(_stat_grid_html(stats))

        # Loan products
        products = [
            t["description"]
            for lpt in cb.get("loanProductTypes", [])
            for t in (lpt.get("types") or [{"description": lpt["description"]}])
        ]
        if products:
            ui.html(_section_label("Loan Products"))
            ui.html(_tags_html(products, "accent"))

        # Optional tag groups
        for label, key, css in [
            ("Property Types", "propertyTypes", ""),
            ("Execution", "executionTypes", "purple"),
            ("Business Types", "businessTypes", ""),
        ]:
            items = cb.get(key, [])
            if items:
                ui.html(_section_label(label, "margin-top:8px"))
                ui.html(_tags_html(items, css))

        # Geographic footprint
        fps = cb.get("footprints", [])
        if fps:
            with ui.expansion("Geographic Footprint!").classes("w-full"):
                ui.html(_section_label("Geographic Footprint", "margin-top:8px"))
                fp_html = '<div class="fp-list">'
                for fp in fps:
                    sc = fp.get("stateCode") or fp.get("description", "")
                    counties = [c["description"] for c in fp.get("types", [])]
                    fp_html += f'<div class="fp-state">{fp["description"]} ({sc})</div>'
                    fp_html += f'<div class="fp-counties">{" · ".join(counties)}</div>'
                fp_html += "</div>"
                ui.html(fp_html)

        # Notes
        if notes := cb.get("notes"):
            ui.html(_section_label("Notes", "margin-top:8px"))
            ui.html(
                f'<div style="font-size:.78rem;color:#a0a8c0;font-style:italic">{notes}</div>'
            )


# ── Lender card ─────────────────────────────────────────────────────────────────


def render_lender_card(lender: dict) -> None:
    c = lender["contact"]

    with ui.element("div").classes("lender-card"):
        # ── Header row ───────────────────────────────────────────────────────
        with ui.element("div").style(
            "display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px"
        ):
            with ui.element("div"):
                ui.html(f'<h3 class="lender-name">{lender["lenderName"]}</h3>')
                if url := lender.get("lenderUri"):
                    ui.html(
                        f'<a class="lender-url" href="{url}" target="_blank">{url}</a>'
                    )

            cb_types = list(
                {
                    cb.get("creditBoxType", "")
                    for cb in lender.get("creditBoxes", [])
                    if cb.get("creditBoxType")
                }
            )
            if cb_types:
                ui.html(_tags_html([t.upper() for t in cb_types], "purple"))

        # ── Contact ──────────────────────────────────────────────────────────
        parts = []
        if email := c.get("email"):
            parts.append(
                f'<span class="contact-item">✉ <strong>{email}</strong></span>'
            )
        if phone := c.get("phone"):
            parts.append(
                f'<span class="contact-item">☎ <strong>{phone}</strong></span>'
            )
        if li := c.get("linkedInUrl"):
            parts.append(
                f'<span class="contact-item">🔗 '
                f'<a href="{li}" target="_blank" style="color:#7b61ff">LinkedIn</a></span>'
            )
        if parts:
            ui.html('<div class="contact-row">' + "".join(parts) + "</div>")

        ui.html('<hr class="divider">')

        # ── Credit boxes ─────────────────────────────────────────────────────
        ui.html(_section_label("Credit Boxes"))
        with ui.element("div").classes("cb-grid"):
            for cb in lender.get("creditBoxes", []):
                render_credit_box(cb)


# ── Empty state ─────────────────────────────────────────────────────────────────


def render_empty_state() -> None:
    ui.html(
        '<div class="no-results">'
        '<div class="no-results-icon">🔍</div>'
        "<div>No lenders match your current filters.</div>"
        '<div style="margin-top:6px;font-size:.75rem">Try relaxing the search criteria.</div>'
        "</div>"
    )


# ── Pagination controls ─────────────────────────────────────────────────────────


def render_pagination(current: int, total: int, go_page: callable) -> None:
    """Render prev / page-numbers / next controls."""

    with ui.element("div").style(
        "display:flex;align-items:center;justify-content:center;"
        "gap:6px;padding:24px 0 8px;flex-wrap:wrap"
    ):
        # Prev
        prev = ui.button("← Prev", on_click=lambda: go_page(current - 1))
        prev.style(_btn_style(disabled=(current == 1)))
        if current == 1:
            prev.disable()

        # Page number buttons — show window around current page
        pages = _page_window(current, total)
        for p in pages:
            if p is None:
                ui.html(
                    '<span style="color:#6b7294;padding:0 4px;font-family:DM Mono,monospace">…</span>'
                )
            else:
                active = p == current
                btn = ui.button(str(p), on_click=lambda _, p=p: go_page(p))
                btn.style(_btn_style(active=active))

        # Next
        nxt = ui.button("Next →", on_click=lambda: go_page(current + 1))
        nxt.style(_btn_style(disabled=(current == total)))
        if current == total:
            nxt.disable()


def _btn_style(active=False, disabled=False) -> str:
    base = (
        "font-family:'DM Mono',monospace;font-size:.8rem;"
        "border-radius:6px;padding:6px 14px;cursor:pointer;border:1px solid;"
        "transition:all .15s;"
    )
    if active:
        return (
            base
            + "background:#4fffb0;color:#0d0f14;border-color:#4fffb0;font-weight:700;"
        )
    if disabled:
        return (
            base
            + "background:#151820;color:#3a3f55;border-color:#2a2f42;cursor:default;"
        )
    return base + "background:#1e2230;color:#e8eaf2;border-color:#2a2f42;"


def _page_window(current: int, total: int) -> list:
    """Return a list of page numbers with None as ellipsis placeholders."""
    if total <= 7:
        return list(range(1, total + 1))
    pages = set()
    pages.update([1, 2, total - 1, total])
    for p in range(max(1, current - 1), min(total, current + 2)):
        pages.add(p)
    result = []
    prev = 0
    for p in sorted(pages):
        if p - prev > 1:
            result.append(None)  # ellipsis
        result.append(p)
        prev = p
    return result
