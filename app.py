"""
FAVV Retribution Calculator - Streamlit App
Calculates FAVV charges based on Royal Decree tariffs 2026
"""

import streamlit as st
import base64
import os
from berekeningen import (
    PRODUCT_TYPES, FLOWS, LOCATIONS,
    bereken_veterinair_vlees_vis,
    bereken_veterinair_other,
    bereken_fyto_zaden,
    bereken_fyto_fruit_groenten,
    bereken_fyto_aardappelen,
    bereken_fyto_hout,
    bereken_fyto_granen,
    bereken_fyto_verpakkingshout,
    bereken_other_controls,
)

# ── ENGLISH LABELS ─────────────────────────────────────────────────────────────
PRODUCT_LABELS_EN = {
    "Vlees / Vis (veterinair)": "Meat / Fish (veterinary)",
    "Andere dan vlees/vis - HC + NHC (veterinair)": "Other than Meat/Fish – HC + NHC (veterinary)",
    "Plantaardige producten - Zaden": "Vegetable Products – Seeds",
    "Plantaardige producten - Fruit & Groenten": "Vegetable Products – Fruit & Vegetables",
    "Plantaardige producten - Aardappelen": "Vegetable Products – Potatoes",
    "Plantaardige producten - Hout": "Vegetable Products – Wood",
    "Plantaardige producten - Granen (Cereals)": "Vegetable Products – Cereals",
    "Verpakkingshout": "Packaging Wood",
    "Handelsnorm / Levensmiddelen niet-dierlijk (Other controls)": "Trade Standards / Non-animal Food (Other controls)",
}
PRODUCT_TYPES_EN = list(PRODUCT_LABELS_EN.values())
NL_FROM_EN = {v: k for k, v in PRODUCT_LABELS_EN.items()}
LOCATIONS_EN = ["Rest of the World", "New Zealand"]
LOCATIONS_MAP = {"Rest of the World": "Rest of the World", "New Zealand": "Nieuw-Zeeland"}

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FAVV Retribution Calculator · DKM Customs",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── LOGO HELPER ────────────────────────────────────────────────────────────────
def get_logo_b64():
    for path in [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "dkm_logo.png"),
        os.path.join(os.getcwd(), "dkm_logo.png"),
        "dkm_logo.png",
    ]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" style="height:34px;filter:brightness(0) invert(1);opacity:0.92;">'
    if logo_b64 else '<span style="color:white;font-weight:800;font-size:18px;">DKM</span>'
)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "resultaat" not in st.session_state:
    st.session_state["resultaat"] = None
if "invoer" not in st.session_state:
    st.session_state["invoer"] = {}
if "product_en" not in st.session_state:
    st.session_state["product_en"] = ""

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background: #f4f6f9; }

.favv-header {
    background: #003d7a;
    border-radius: 14px;
    padding: 22px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.favv-header-left { display: flex; align-items: center; gap: 20px; }
.favv-logo {
    background: #fff;
    color: #003d7a;
    font-weight: 900;
    font-size: 22px;
    padding: 6px 14px;
    border-radius: 8px;
    letter-spacing: -1px;
}
.favv-title { color: #fff; font-size: 20px; font-weight: 700; margin: 0; }
.favv-sub   { color: #7eb8f7; font-size: 13px; margin: 2px 0 0 0; }

/* Panel cards */
.panel {
    background: white;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e4e9f0;
    height: 100%;
}
.panel-title {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #003d7a;
    margin-bottom: 18px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e8f0fe;
}

/* Result card */
.result-card {
    background: #003d7a;
    border-radius: 12px;
    padding: 22px 20px;
    text-align: center;
    margin-bottom: 16px;
}
.result-label {
    color: #7eb8f7;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 6px;
}
.result-amount {
    color: white;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 42px;
    font-weight: 600;
    letter-spacing: -2px;
    line-height: 1;
}
.nz-badge {
    display: inline-block;
    background: #fff3cd;
    color: #856404;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 8px;
}

/* Breakdown */
.breakdown-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #f0f3f7;
    font-size: 13px;
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-label { color: #555; }
.breakdown-amount { color: #222; font-weight: 600; font-family: 'IBM Plex Mono', monospace; }

/* Placeholder */
.result-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 220px;
    color: #bbb;
    font-size: 14px;
    gap: 12px;
}
.result-placeholder-icon { font-size: 48px; opacity: 0.3; }

/* Step badge */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #e8f0fe;
    color: #003d7a;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Buttons */
.stSelectbox label, .stNumberInput label {
    font-weight: 600 !important;
    color: #222 !important;
    font-size: 13px !important;
}
.stButton > button {
    background: #003d7a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* New calculation button – lighter style */
.btn-reset button {
    background: #f0f3f7 !important;
    color: #003d7a !important;
    border: 1.5px solid #c5d5e8 !important;
}
.btn-reset button:hover { background: #e0eaf5 !important; opacity: 1 !important; }

/* Remove extra padding Streamlit adds */
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }

/* Make the top Streamlit toolbar match our blue */
header[data-testid="stHeader"] {
    background: #003d7a !important;
}
header[data-testid="stHeader"] * {
    color: white !important;
    stroke: white !important;
}
/* Top toolbar buttons/icons */
.stToolbar { background: #003d7a !important; }
[data-testid="stToolbar"] { background: #003d7a !important; }
[data-testid="stDecoration"] { background: #003d7a !important; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="favv-header">
  <div class="favv-header-left">
    <div class="favv-logo">FAVV</div>
    <div>
      <p class="favv-title">Retribution Calculator</p>
      <p class="favv-sub">Royal Decree Tariffs 2026 · Port of Antwerp</p>
    </div>
  </div>
  <div>{logo_html}</div>
</div>
""", unsafe_allow_html=True)

# ── MAIN LAYOUT: left = input, right = result ──────────────────────────────────
left, right = st.columns([1.1, 0.9], gap="large")

# ════════════════════════════════════════════════════════════════════
# LEFT PANEL — Input
# ════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="panel-title">① Select product type</div>', unsafe_allow_html=True)

    product_type_en = st.selectbox(
        "Product / control type",
        PRODUCT_TYPES_EN,
        label_visibility="collapsed",
        help="The category determines which FAVV tariffs apply.",
        key="product_select",
    )
    product_type_nl = NL_FROM_EN[product_type_en]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title">② Enter details</div>', unsafe_allow_html=True)

    invoer = {}
    calc_result = None

    is_veterinair      = product_type_nl in ["Vlees / Vis (veterinair)", "Andere dan vlees/vis - HC + NHC (veterinair)"]
    is_verpakkingshout = product_type_nl == "Verpakkingshout"
    is_fyto            = product_type_nl.startswith("Plantaardige") and not is_verpakkingshout
    is_other           = "Other controls" in product_type_nl

    # ── Veterinary ────────────────────────────────────────────────
    if is_veterinair:
        c1, c2 = st.columns(2)
        with c1:
            flow = st.selectbox("Flow", ["Import", "Transit"])
            invoer["Flow"] = flow
        with c2:
            locatie_en = st.selectbox("Origin", LOCATIONS_EN)
            locatie_nl = LOCATIONS_MAP[locatie_en]
            invoer["Origin"] = locatie_en

        if product_type_nl == "Vlees / Vis (veterinair)":
            c1, c2 = st.columns(2)
            with c1:
                gewicht = st.number_input("Weight (kg)", min_value=0.0, value=15000.0, step=100.0)
                invoer["Weight"] = f"{gewicht:,.0f} kg"
            with c2:
                containers = st.number_input("Containers", min_value=1, value=1, step=1)
                invoer["Containers"] = int(containers)
            if st.button("🧮 Calculate FAVV charge"):
                calc_result = bereken_veterinair_vlees_vis(gewicht, flow, locatie_nl, int(containers))
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                containers = st.number_input("Containers", min_value=1, value=1, step=1)
                invoer["Containers"] = int(containers)
            with c2:
                halfuren = st.number_input("Half-hours inspection", min_value=0, value=1, step=1)
                invoer["Half-hours"] = int(halfuren)
            with c3:
                volgende_partij = st.number_input("Next shipment same cont.", min_value=0, value=0, step=1)
                invoer["Next shipment same cont."] = int(volgende_partij)
            if st.button("🧮 Calculate FAVV charge"):
                calc_result = bereken_veterinair_other(flow, locatie_nl, int(containers), int(halfuren), int(volgende_partij))

    # ── Phytosanitary ─────────────────────────────────────────────
    elif is_fyto:
        c1, c2 = st.columns(2)
        with c1:
            zendingen = st.number_input("Shipments (documents)", min_value=1, value=1, step=1)
            invoer["Shipments"] = int(zendingen)
        with c2:
            containers = st.number_input("Containers", min_value=1, value=1, step=1)
            invoer["Containers"] = int(containers)

        if product_type_nl in [
            "Plantaardige producten - Zaden",
            "Plantaardige producten - Fruit & Groenten",
            "Plantaardige producten - Aardappelen",
            "Plantaardige producten - Granen (Cereals)",
        ]:
            gewicht = st.number_input("Weight (kg)", min_value=0.0, value=15000.0, step=100.0)
            invoer["Weight"] = f"{gewicht:,.0f} kg"
        elif product_type_nl == "Plantaardige producten - Hout":
            volume = st.number_input("Volume (m³)", min_value=0.0, value=50.0, step=1.0)
            invoer["Volume"] = f"{volume:,.1f} m³"

        if st.button("🧮 Calculate FAVV charge"):
            if product_type_nl == "Plantaardige producten - Zaden":
                calc_result = bereken_fyto_zaden(gewicht, int(zendingen), int(containers))
            elif product_type_nl == "Plantaardige producten - Fruit & Groenten":
                calc_result = bereken_fyto_fruit_groenten(gewicht, int(zendingen), int(containers))
            elif product_type_nl == "Plantaardige producten - Aardappelen":
                calc_result = bereken_fyto_aardappelen(gewicht, int(zendingen), int(containers))
            elif product_type_nl == "Plantaardige producten - Hout":
                calc_result = bereken_fyto_hout(volume, int(zendingen), int(containers))
            elif product_type_nl == "Plantaardige producten - Granen (Cereals)":
                calc_result = bereken_fyto_granen(gewicht, int(zendingen), int(containers))

    # ── Packaging Wood ────────────────────────────────────────────
    elif is_verpakkingshout:
        zendingen = st.number_input("Number of shipments", min_value=1, value=1, step=1)
        invoer["Shipments"] = int(zendingen)
        if st.button("🧮 Calculate FAVV charge"):
            calc_result = bereken_fyto_verpakkingshout(int(zendingen))

    # ── Other controls ────────────────────────────────────────────
    elif is_other:
        c1, c2, c3 = st.columns(3)
        with c1:
            certs = st.number_input("Certificates", min_value=1, value=1, step=1)
            invoer["Certificates"] = int(certs)
        with c2:
            halfuren_controle = st.number_input("Half-hours inspection", min_value=0, value=1, step=1)
            invoer["Half-hours inspection"] = int(halfuren_controle)
        with c3:
            halfuren_monster = st.number_input("Half-hours sampling", min_value=0, value=0, step=1)
            invoer["Half-hours sampling"] = int(halfuren_monster)
        if st.button("🧮 Calculate FAVV charge"):
            calc_result = bereken_other_controls(int(certs), int(halfuren_controle), int(halfuren_monster))

    # Store result in session state when calculated
    if calc_result is not None:
        st.session_state["resultaat"] = calc_result
        st.session_state["invoer"] = invoer
        st.session_state["product_en"] = product_type_en

# ════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Result
# ════════════════════════════════════════════════════════════════════
with right:
    resultaat = st.session_state.get("resultaat")

    if resultaat is None:
        # Placeholder
        st.markdown('<div class="panel-title">③ Result</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="result-placeholder">
            <div class="result-placeholder-icon">🧮</div>
            <div>Fill in the details and press<br><strong>Calculate FAVV charge</strong></div>
        </div>
        """, unsafe_allow_html=True)

    else:
        totaal = resultaat.get("TOTAAL", 0)
        nz = resultaat.get("NZ korting toegepast", False)
        nz_html = '<div class="nz-badge">✓ New Zealand discount 22.5% applied</div>' if nz else ""

        st.markdown('<div class="panel-title">③ Result</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Total FAVV retribution</div>
            <div class="result-amount">€ {totaal:,.2f}</div>
            {nz_html}
        </div>
        """, unsafe_allow_html=True)

        # Cost breakdown
        breakdown_html = '<div style="background:#f8fafc;border-radius:10px;padding:12px 16px;border:1px solid #e4e9f0;margin-bottom:16px;">'
        for k, v in resultaat.items():
            if k in ("TOTAAL", "NZ korting toegepast"):
                continue
            breakdown_html += f"""
            <div class="breakdown-row">
                <span class="breakdown-label">{k}</span>
                <span class="breakdown-amount">€ {v:,.2f}</span>
            </div>"""
        breakdown_html += "</div>"
        st.markdown(breakdown_html, unsafe_allow_html=True)

        # New calculation button
        st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
        if st.button("↩ New calculation"):
            st.session_state["resultaat"] = None
            st.session_state["invoer"] = {}
            st.session_state["product_en"] = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Email section
        with st.expander("📧 Send report via Gmail"):
            st.info("Upload your Google Cloud OAuth2 `credentials.json` to send reports by email.")
            ontvanger = st.text_input("Recipient email", placeholder="name@company.com")
            creds_file = st.file_uploader("Upload credentials.json", type=["json"])
            if st.button("📤 Send report"):
                if not ontvanger:
                    st.error("Please enter a recipient email address.")
                elif not creds_file:
                    st.error("Please upload your credentials.json file.")
                else:
                    from gmail_sender import verstuur_rapport
                    creds_str = creds_file.read().decode("utf-8")
                    with st.spinner("Sending report..."):
                        ok = verstuur_rapport(
                            ontvanger,
                            st.session_state["product_en"],
                            st.session_state["invoer"],
                            st.session_state["resultaat"],
                            creds_str,
                        )
                    if ok:
                        st.success(f"✅ Report sent to {ontvanger}")
                    else:
                        st.error("❌ Sending failed. Please check your credentials and try again.")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#bbb;font-size:11px;margin-top:24px;">
    Royal Decree Retributions 2026 · Published 29/12/2025 · Belgian Official Gazette &nbsp;·&nbsp; DKM Customs
</div>
""", unsafe_allow_html=True)
