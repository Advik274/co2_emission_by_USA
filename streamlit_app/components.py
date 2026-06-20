import streamlit as st
import os

# ──────────────────────────────────────────────────────────────────────────────
# Theme injection
# ──────────────────────────────────────────────────────────────────────────────

def inject_theme():
    """Inject the shared theme CSS and visual effects — call at the top of every page."""
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown("""
    <div class="scanline-overlay"></div>
    <div class="bg-grid"></div>
    <div class="glow-orb-1"></div>
    <div class="glow-orb-2"></div>
    <div class="glow-orb-3"></div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Page header
# ──────────────────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "FUTURE CARBON EMISSION HORIZONS"):
    """Render a consistent centered page header."""
    st.markdown(f"""
    <div style="text-align:center; padding: 32px 20px 24px;">
        <h1 style="margin-bottom: 8px;">{title}</h1>
        <p style="color:rgba(255,255,255,0.35); font-size:0.85rem; letter-spacing:5px;
                  font-family:'JetBrains Mono',monospace; margin:0;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ──────────────────────────────────────────────────────────────────────────────

NAV_ITEMS = {
    "Dashboard": "app.py",
    "Predictions": "pages/predictions.py",
    "Models": "pages/model_comparison.py",
    "Analytics": "pages/analytics.py",
}

def sidebar_navigation(current: str):
    """Render stable page navigation without radio state collisions."""
    st.markdown("""
    <p style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
              letter-spacing:2px; color:#00ff7f; text-transform:uppercase; padding:14px 0 8px;">
        // Navigation
    </p>
    """, unsafe_allow_html=True)

    for label, target in NAV_ITEMS.items():
        if st.button(
            label,
            key=f"nav_{label.lower()}",
            use_container_width=True,
            disabled=(label == current),
        ):
            st.switch_page(target)


# ──────────────────────────────────────────────────────────────────────────────
# Metric card (futuristic tile)
# ──────────────────────────────────────────────────────────────────────────────

def metric_card(label: str, value, unit: str = "", accent=False, delay: float = 0):
    """
    Render a futuristic metric card.
    accent: False | 'pink' | 'cyan' | 'orange'
    """
    palette = {
        "pink":   "color:#ff00ff!important;text-shadow:0 0 20px rgba(255,0,255,0.5)!important;",
        "cyan":   "color:#00ffd5!important;text-shadow:0 0 20px rgba(0,255,213,0.5)!important;",
        "orange": "color:#ffaa00!important;text-shadow:0 0 20px rgba(255,170,0,0.5)!important;",
    }
    extra_style = palette.get(accent, "") if isinstance(accent, str) else ""
    value_style = f"margin:0;{extra_style}"

    return f"""
    <div class="futuristic-card fade-in" style="animation-delay:{delay}s;">
        <p class="metric-label" style="margin:0 0 8px 0;">{label}</p>
        <p class="metric-value" style="{value_style}">{value}</p>
        <p class="metric-label" style="margin:6px 0 0 0;">{unit}</p>
    </div>
    """


# ──────────────────────────────────────────────────────────────────────────────
# KPI row
# ──────────────────────────────────────────────────────────────────────────────

def kpi_tile(label: str, value, delta: str = None, delta_positive: bool = None, delay: float = 0):
    """
    Render a compact KPI tile with optional delta.
    delta_positive=True → green, False → red, None → muted
    """
    if delta is not None:
        if delta_positive is True:
            delta_cls, delta_prefix = "pos", "▲ "
        elif delta_positive is False:
            delta_cls, delta_prefix = "neg", "▼ "
        else:
            delta_cls, delta_prefix = "neu", ""
        delta_html = f'<div class="kpi-delta {delta_cls}">{delta_prefix}{delta}</div>'
    else:
        delta_html = ""

    return f"""
    <div class="kpi-tile" style="animation-delay:{delay}s;">
        <div class="kpi-num">{value}</div>
        <div class="kpi-lbl">{label}</div>
        {delta_html}
    </div>
    """


# ──────────────────────────────────────────────────────────────────────────────
# Story card (chart narrative)
# ──────────────────────────────────────────────────────────────────────────────

def story_card(icon: str, title: str, body: str):
    """Render a narrative story card to explain what a chart means."""
    return f"""
    <div class="story-card">
        <span class="story-icon">{icon}</span>
        <div class="story-title">{title}</div>
        <div class="story-body">{body}</div>
    </div>
    """


# ──────────────────────────────────────────────────────────────────────────────
# Insight card (compact)
# ──────────────────────────────────────────────────────────────────────────────

def insight_card(text: str):
    """Render a compact insight/takeaway card."""
    return f"""
    <div class="futuristic-card" style="margin-bottom:16px; padding:18px 22px !important;">
        <p style="color:rgba(255,255,255,0.65); font-family:'Inter',sans-serif;
                  font-size:0.88rem; margin:0; line-height:1.6;">
            {text}
        </p>
    </div>
    """


# ──────────────────────────────────────────────────────────────────────────────
# Model status banner
# ──────────────────────────────────────────────────────────────────────────────

def model_status_banner(available: dict):
    """
    Show a banner about which ML models are loaded vs. missing.
    available = {'RF': bool, 'XGBoost': bool, 'ANN': list_of_names}
    """
    rf_ok  = available.get('RF', False)
    xgb_ok = available.get('XGBoost', False)
    ann_ok = len(available.get('ANN', [])) > 0

    if rf_ok and xgb_ok and ann_ok:
        st.markdown("""
        <div class="banner-card ok">
            <span>✅</span>
            <span>All ML models loaded successfully — predictions use trained models.</span>
        </div>
        """, unsafe_allow_html=True)
        return

    lines = []
    if not rf_ok:
        lines.append("❌ <b>Random Forest</b> — LFS pointer (run <code>git lfs pull</code> to download)")
    else:
        lines.append("✅ <b>Random Forest</b> — loaded")
    if not xgb_ok:
        lines.append("❌ <b>XGBoost</b> — LFS pointer (run <code>git lfs pull</code> to download)")
    else:
        lines.append("✅ <b>XGBoost</b> — loaded")
    if ann_ok:
        lines.append(f"✅ <b>ANN models</b> — {len(available.get('ANN', []))} model(s) available")
    else:
        lines.append("❌ <b>ANN</b> — no .keras files found")

    items = "".join(f"<div style='margin-bottom:4px;'>{l}</div>" for l in lines)
    st.markdown(f"""
    <div class="banner-card warn">
        <span>⚠️</span>
        <div>
            <b>Some models not available locally — using trend-based estimates for missing ones.</b>
            <div style="margin-top:10px; font-size:0.75rem; opacity:0.85;">{items}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Section divider
# ──────────────────────────────────────────────────────────────────────────────

def section_divider():
    st.markdown("---")
