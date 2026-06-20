import streamlit as st
import os

def inject_theme():
    """Inject the shared theme CSS and visual effects - call this at the start of every page."""
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="scanline-overlay"></div>
    <div class="bg-grid"></div>
    <div class="glow-orb-1"></div>
    <div class="glow-orb-2"></div>
    <div class="glow-orb-3"></div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle=None):
    """Render a consistent page header."""
    subtitle_html = subtitle if subtitle else "FUTURE CARBON EMISSION HORIZONS"
    st.markdown(f"""
    <div style="text-align: center; padding: 30px 20px 20px;">
        <h1>{title}</h1>
        <p style="color: rgba(255,255,255,0.4); font-size: 1rem; letter-spacing: 6px; font-family: 'JetBrains Mono', monospace;">
            {subtitle_html}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

def metric_card(label, value, unit="", accent_color=False, delay=0):
    """Render a futuristic metric card."""
    if accent_color == "pink":
        color_style = "color: #ff00ff !important; text-shadow: 0 0 20px rgba(255,0,255,0.5) !important;"
    elif accent_color == "cyan":
        color_style = "color: #00ffd5 !important; text-shadow: 0 0 20px rgba(0,255,213,0.5) !important;"
    else:
        color_style = ""
    
    color_style = f' style="{color_style}"' if color_style else ""
    
    return f"""
    <div class="futuristic-card fade-in" style="animation-delay: {delay}s;">
        <p class="metric-label">{label}</p>
        <p class="metric-value"{color_style}>{value}</p>
        <p class="metric-label">{unit}</p>
    </div>
    """

def insight_card(text):
    """Render an insight/story card."""
    return f"""
    <div class="futuristic-card" style="margin-bottom: 20px;">
        <p style="color: #888; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; margin: 0;">
            {text}
        </p>
    </div>
    """

def section_divider():
    """Render a section divider."""
    st.markdown("---")