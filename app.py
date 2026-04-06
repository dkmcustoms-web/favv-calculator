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
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── LOGO HELPER ────────────────────────────────────────────────────────────────
def get_logo_b64():
    logo_path = os.path.join(os.path.dirname(__file__), "dkm_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" style="height:34px;filter:brightness(0) invert(1);opacity:0.92;">'
    if logo_b64 else '<span style="color:white;font-weight:800;font-size:18px;">DKM</span>'
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
.stApp { background: #f4f6f9; }

/* Header */
.favv-header {
    background: #003d7a;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 28px;
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

/* Result card */
.result-card {
    background: #003d7a;
    border-radius: 14px;
    padding: 24px 28px;
    margin: 20px 0;
    text-align: center;
}
.result-label {
    color: #7eb8f7;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.result-amount {
    color: white;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 52px;
    font-weight: 600;
    letter-spacing: -2px;
}
.nz-badge {
    display: inline-block;
    background: #fff3cd;
    color: #856404;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 10px;
}

/* Breakdown */
.breakdown-row {
    display: flex;
    justify-content: space-between;
    padding: 11px 0;
    border-bottom: 1px solid #e8ecf0;
    font-size: 14px;
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-label { color: #555; }
.breakdown-amount {
    color: #222;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
}

/* Step badge */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #e8f0fe;
    color: #003d7a;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 16px;
}

/* Streamlit overrides */
.stSelectbox label, .stNumberInput label, .stRadio label {
    font-weight: 600 !important;
    color: #222 !important;
    font-size: 14px !important;
}
.stButton > button {
    background: #003d7a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88 !important; }
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

# ── STEP 1: PRODUCT TYPE ───────────────────────────────────────────────────────
st.markdown('<div class="step-badge">① Product type</div>', unsafe_allow_html=True)
product_type_en = st.selectbox(
    "Select the product / control type",
    PRODUCT_TYPES_EN,
    help="The category determines which FAVV tariffs apply."
)
product_type_nl = NL_FROM_EN[product_type_en]

st.markdown("---")

# ── STEP 2: DYNAMIC INPUT ─────────────────────────────────────────────────────
st.markdown('<div class="step-badge">② Details</div>', unsafe_allow_html=True)

invoer = {}
resultaat = None

is_veterinair    = product_type_nl in ["Vlees / Vis (veterinair)", "Andere dan vlees/vis - HC + NHC (veterinair)"]
is_verpakkingshout = product_type_nl == "Verpakkingshout"
is_fyto          = product_type_nl.startswith("Plantaardige") and not is_verpakkingshout
is_other         = "Other controls" in product_type_nl

# ── Veterinary ────────────────────────────────────────────────────────────────
if is_veterinair:
    col1, col2 = st.columns(2)
    with col1:
        flow = st.selectbox("Flow", ["Import", "Transit"])
        invoer["Flow"] = flow
    with col2:
        locatie_en = st.selectbox("Origin", LOCATIONS_EN)
        locatie_nl = LOCATIONS_MAP[locatie_en]
        invoer["Origin"] = locatie_en

    if product_type_nl == "Vlees / Vis (veterinair)":
        gewicht = st.number_input("Weight (kg)", min_value=0.0, value=15000.0, step=100.0)
        invoer["Weight"] = f"{gewicht:,.0f} kg"
        containers = st.number_input("Number of containers", min_value=1, value=1, step=1)
        invoer["Containers"] = int(containers)
        if st.button("🧮 Calculate FAVV charge"):
            resultaat = bereken_veterinair_vlees_vis(gewicht, flow, locatie_nl, int(containers))
    else:
        col1, col2 = st.columns(2)
        with col1:
            containers = st.number_input("Number of containers", min_value=1, value=1, step=1)
            invoer["Containers"] = int(containers)
            halfuren = st.number_input("Half-hours of inspection", min_value=0, value=1, step=1,
                                       help="Number of half-hour periods the inspection takes")
            invoer["Half-hours inspection"] = int(halfuren)
        with col2:
            volgende_partij = st.number_input("Next shipment same container", min_value=0, value=0, step=1)
            invoer["Next shipment same container"] = int(volgende_partij)
        if st.button("🧮 Calculate FAVV charge"):
            resultaat = bereken_veterinair_other(flow, locatie_nl, int(containers), int(halfuren), int(volgende_partij))

# ── Phytosanitary ─────────────────────────────────────────────────────────────
elif is_fyto:
    col1, col2 = st.columns(2)
    with col1:
        zendingen = st.number_input("Number of shipments (documents)", min_value=1, value=1, step=1)
        invoer["Shipments"] = int(zendingen)
    with col2:
        containers = st.number_input("Number of containers", min_value=1, value=1, step=1)
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
            resultaat = bereken_fyto_zaden(gewicht, int(zendingen), int(containers))
        elif product_type_nl == "Plantaardige producten - Fruit & Groenten":
            resultaat = bereken_fyto_fruit_groenten(gewicht, int(zendingen), int(containers))
        elif product_type_nl == "Plantaardige producten - Aardappelen":
            resultaat = bereken_fyto_aardappelen(gewicht, int(zendingen), int(containers))
        elif product_type_nl == "Plantaardige producten - Hout":
            resultaat = bereken_fyto_hout(volume, int(zendingen), int(containers))
        elif product_type_nl == "Plantaardige producten - Granen (Cereals)":
            resultaat = bereken_fyto_granen(gewicht, int(zendingen), int(containers))

# ── Packaging Wood ────────────────────────────────────────────────────────────
elif is_verpakkingshout:
    zendingen = st.number_input("Number of shipments", min_value=1, value=1, step=1)
    invoer["Shipments"] = int(zendingen)
    if st.button("🧮 Calculate FAVV charge"):
        resultaat = bereken_fyto_verpakkingshout(int(zendingen))

# ── Other controls ────────────────────────────────────────────────────────────
elif is_other:
    col1, col2, col3 = st.columns(3)
    with col1:
        certs = st.number_input("Number of certificates", min_value=1, value=1, step=1)
        invoer["Certificates"] = int(certs)
    with col2:
        halfuren_controle = st.number_input("Half-hours inspection", min_value=0, value=1, step=1)
        invoer["Half-hours inspection"] = int(halfuren_controle)
    with col3:
        halfuren_monster = st.number_input("Half-hours sampling", min_value=0, value=0, step=1)
        invoer["Half-hours sampling"] = int(halfuren_monster)
    if st.button("🧮 Calculate FAVV charge"):
        resultaat = bereken_other_controls(int(certs), int(halfuren_controle), int(halfuren_monster))

# ── RESULT ─────────────────────────────────────────────────────────────────────
if resultaat:
    st.markdown("---")
    st.markdown('<div class="step-badge">③ Result</div>', unsafe_allow_html=True)

    totaal = resultaat.get("TOTAAL", 0)
    nz = resultaat.get("NZ korting toegepast", False)
    nz_html = '<div class="nz-badge">✓ New Zealand discount 22.5% applied</div>' if nz else ""

    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">Total FAVV retribution</div>
        <div class="result-amount">€ {totaal:,.2f}</div>
        {nz_html}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Cost breakdown**")
    breakdown_html = '<div style="background:white;border-radius:10px;padding:16px 20px;border:1px solid #e4e9f0;">'
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

    st.session_state["laatste_resultaat"] = resultaat
    st.session_state["laatste_invoer"] = invoer
    st.session_state["laatste_product"] = product_type_en

    # ── EMAIL ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="step-badge">④ Send report</div>', unsafe_allow_html=True)

    with st.expander("📧 Send report via Gmail"):
        st.info("You need a `credentials.json` file from Google Cloud (OAuth2). See the README for setup instructions.")
        ontvanger = st.text_input("Recipient email address", placeholder="name@company.com")
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
                        st.session_state["laatste_product"],
                        st.session_state["laatste_invoer"],
                        st.session_state["laatste_resultaat"],
                        creds_str,
                    )
                if ok:
                    st.success(f"✅ Report sent to {ontvanger}")
                else:
                    st.error("❌ Sending failed. Please check your credentials and try again.")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<br>
<div style="text-align:center;color:#aaa;font-size:12px;">
    Royal Decree Retributions 2026 · Published 29/12/2025 · Belgian Official Gazette &nbsp;·&nbsp; DKM Customs
</div>
""", unsafe_allow_html=True)
