"""
styles.py — injects all CSS into the NiceGUI app
"""

from nicegui import ui

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:          #0d0f14;
    --surface:     #151820;
    --surface2:    #1e2230;
    --border:      #2a2f42;
    --accent:      #4fffb0;
    --accent2:     #7b61ff;
    --text:        #e8eaf2;
    --muted:       #6b7294;
    --tag-bg:      #1a2535;
    --tag-border:  #2a3a55;
  }

  body { background: var(--bg) !important; font-family: 'Syne', sans-serif; color: var(--text); }
  .nicegui-content { background: var(--bg) !important; }

  ::-webkit-scrollbar       { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Header ── */
  .dash-header {
    background: linear-gradient(135deg, #0d0f14 0%, #111827 100%);
    border-bottom: 1px solid var(--border);
    padding: 28px 40px 20px;
  }
  .dash-title {
    font-size: 2rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .dash-subtitle {
    color: var(--muted); font-size: 0.85rem; margin-top: 4px;
    font-family: 'DM Mono', monospace;
  }

  /* ── Filter bar ── */
  .filter-bar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 16px 40px;
    gap: 12px;
  }

  /* NiceGUI / Quasar field overrides */
  .q-field__control            { background: var(--surface2) !important; border-radius: 8px !important; }
  .q-field__native,
  .q-field__input              { color: var(--text) !important; font-family: 'DM Mono', monospace !important; font-size: 0.85rem !important; }
  .q-field--outlined .q-field__control:before { border-color: var(--border) !important; }
  .q-field--outlined .q-field__control:after  { border-color: var(--accent) !important; }
  .q-field__label              { color: var(--muted) !important; font-family: 'Syne', sans-serif !important; font-size: 0.8rem !important; }
  .q-item__label               { color: var(--text) !important; font-family: 'DM Mono', monospace !important; }
  .q-menu                      { background: var(--surface2) !important; border: 1px solid var(--border) !important; }

  /* ── Results ── */
  .results-area   { padding: 24px 40px; }
  .results-count  { font-family: 'DM Mono', monospace; font-size: 0.8rem; color: var(--muted); margin-bottom: 16px; }
  .results-count span { color: var(--accent); font-weight: 500; }

  /* ── Lender card ── */
  .lender-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .lender-card:hover {
    border-color: var(--accent2);
    box-shadow: 0 0 24px rgba(123,97,255,0.12);
  }
  .lender-name  { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; color: var(--text); margin: 0 0 4px; }
  .lender-url   { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: var(--accent); text-decoration: none; }
  .lender-url:hover { text-decoration: underline; }

  .contact-row  { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 8px; }
  .contact-item { font-family: 'DM Mono', monospace; font-size: 0.78rem; color: var(--muted); }
  .contact-item strong { color: var(--text); }

  .divider { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

  /* ── Credit-box grid ── */
  .cb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
  .cb-box  { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; }
  .cb-name { font-size: 0.9rem; font-weight: 700; color: var(--accent); margin-bottom: 10px; letter-spacing: 0.02em; text-transform: uppercase; }

  .stat-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; margin-bottom: 10px; }
  .stat-item  { font-family: 'DM Mono', monospace; font-size: 0.75rem; }
  .stat-label { color: var(--muted); display: block; }
  .stat-value { color: var(--text); font-weight: 500; }

  /* ── Tags ── */
  .tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
  .tag  {
    background: var(--tag-bg); border: 1px solid var(--tag-border);
    border-radius: 4px; padding: 2px 8px;
    font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--text);
  }
  .tag.accent { border-color: var(--accent);  color: var(--accent); }
  .tag.purple { border-color: var(--accent2); color: var(--accent2); }

  /* ── Footprint ── */
  .fp-list    { margin-top: 8px; }
  .fp-state   { font-size: 0.78rem; font-weight: 600; color: var(--muted); margin-bottom: 4px; font-family: 'DM Mono', monospace; }
  .fp-counties { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--muted); line-height: 1.6; }

  /* ── Empty state ── */
  .no-results      { text-align: center; padding: 80px 20px; color: var(--muted); font-family: 'DM Mono', monospace; font-size: 0.9rem; }
  .no-results-icon { font-size: 3rem; margin-bottom: 12px; }

  /* ── Misc ── */
  .section-label {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 6px;
  }
</style>
"""


def inject():
    ui.add_head_html(CSS)
