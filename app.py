"""
FAVV Retributie Calculator - Streamlit App
Berekent FAVV-kosten op basis van KB tarieven 2026
"""

import streamlit as st
import json
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

# ── PAGINA CONFIGURATIE ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FAVV Retributie Calculator",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background: #f0f3f7;
}

/* Header banner */
.favv-header {
    background: #003d7a;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.favv-logo {
    background: white;
    color: #003d7a;
    font-weight: 900;
    font-size: 26px;
    padding: 6px 14px;
    border-radius: 8px;
    letter-spacing: -1px;
}
.favv-title {
    color: white;
    font-size: 22px;
    font-weight: 700;
    margin: 0;
}
.favv-sub {
    color: #7eb8f7;
    font-size: 13px;
    margin: 2px 0 0 0;
}

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
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
}
.result-amount {
    color: white;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 48px;
    font-weight: 600;
    letter-spacing: -1px;
}

/* Breakdown rows */
.breakdown-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #e8ecf0;
    font-size: 14px;
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-label { color: #555; }
.breakdown-amount { color: #222; font-weight: 600; font-family: 'IBM Plex Mono', monospace; }

/* NZ badge */
.nz-badge {
    display: inline-block;
    background: #fff3cd;
    color: #856404;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 8px;
}

/* Section card */
.section-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid #e4e9f0;
}

/* Step indicator */
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
st.markdown("""
<div class="favv-header">
  <div class="favv-logo">FAVV</div>
  <div>
    <p class="favv-title">Retributie Calculator</p>
    <p class="favv-sub">Tarieven KB 2026 · Haven Antwerpen</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STAP 1: PRODUCTTYPE ────────────────────────────────────────────────────────
st.markdown('<div class="step-badge">① Producttype</div>', unsafe_allow_html=True)
with st.container():
    product_type = st.selectbox(
        "Kies het type product / controle",
        PRODUCT_TYPES,
        help="De categorie bepaalt welke FAVV-tarieven van toepassing zijn."
    )

st.markdown("---")

# ── STAP 2: DYNAMISCHE INVOER ──────────────────────────────────────────────────
st.markdown('<div class="step-badge">② Gegevens</div>', unsafe_allow_html=True)

invoer = {}
resultaat = None

is_veterinair = product_type in [
    "Vlees / Vis (veterinair)",
    "Andere dan vlees/vis - HC + NHC (veterinair)",
]
is_fyto = product_type.startswith("Plantaardige")
is_other = "Other controls" in product_type
is_verpakkingshout = product_type == "Verpakkingshout"

# ── Veterinair ─────────────────────────────────────────────────────────────────
if is_veterinair:
    col1, col2 = st.columns(2)
    with col1:
        flow = st.selectbox("Flow", FLOWS)
        invoer["Flow"] = flow
    with col2:
        locatie = st.selectbox("Herkomst", LOCATIONS)
        invoer["Herkomst"] = locatie

    if product_type == "Vlees / Vis (veterinair)":
        gewicht = st.number_input("Gewicht (kg)", min_value=0.0, value=15000.0, step=100.0)
        invoer["Gewicht"] = f"{gewicht:,.0f} kg"
        containers = st.number_input("Aantal containers", min_value=1, value=1, step=1)
        invoer["Containers"] = containers
        if st.button("🧮 Bereken FAVV kost"):
            resultaat = bereken_veterinair_vlees_vis(gewicht, flow, locatie, int(containers))

    else:  # Other than meat/fish
        col1, col2 = st.columns(2)
        with col1:
            containers = st.number_input("Aantal containers", min_value=1, value=1, step=1)
            invoer["Containers"] = containers
            halfuren = st.number_input("Halfuren controle", min_value=0, value=1, step=1,
                                       help="Aantal halfuren dat de controle duurt")
            invoer["Halfuren controle"] = halfuren
        with col2:
            volgende_partij = st.number_input("Volgende partij zelfde container", min_value=0,
                                               value=0, step=1)
            invoer["Volgende partij zelfde container"] = volgende_partij
        if st.button("🧮 Bereken FAVV kost"):
            resultaat = bereken_veterinair_other(flow, locatie, int(containers),
                                                  int(halfuren), int(volgende_partij))

# ── Fytosanitair ───────────────────────────────────────────────────────────────
elif is_fyto and not is_verpakkingshout:
    col1, col2 = st.columns(2)
    with col1:
        zendingen = st.number_input("Aantal zendingen (documenten)", min_value=1, value=1, step=1)
        invoer["Zendingen"] = zendingen
    with col2:
        containers = st.number_input("Aantal containers", min_value=1, value=1, step=1)
        invoer["Containers"] = containers

    if product_type in ["Plantaardige producten - Zaden",
                         "Plantaardige producten - Fruit & Groenten",
                         "Plantaardige producten - Aardappelen",
                         "Plantaardige producten - Granen (Cereals)"]:
        gewicht = st.number_input("Gewicht (kg)", min_value=0.0, value=15000.0, step=100.0)
        invoer["Gewicht"] = f"{gewicht:,.0f} kg"

    elif product_type == "Plantaardige producten - Hout":
        volume = st.number_input("Volume (m³)", min_value=0.0, value=50.0, step=1.0)
        invoer["Volume"] = f"{volume:,.1f} m³"

    if st.button("🧮 Bereken FAVV kost"):
        if product_type == "Plantaardige producten - Zaden":
            resultaat = bereken_fyto_zaden(gewicht, int(zendingen), int(containers))
        elif product_type == "Plantaardige producten - Fruit & Groenten":
            resultaat = bereken_fyto_fruit_groenten(gewicht, int(zendingen), int(containers))
        elif product_type == "Plantaardige producten - Aardappelen":
            resultaat = bereken_fyto_aardappelen(gewicht, int(zendingen), int(containers))
        elif product_type == "Plantaardige producten - Hout":
            resultaat = bereken_fyto_hout(volume, int(zendingen), int(containers))
        elif product_type == "Plantaardige producten - Granen (Cereals)":
            resultaat = bereken_fyto_granen(gewicht, int(zendingen), int(containers))

# ── Verpakkingshout ────────────────────────────────────────────────────────────
elif is_verpakkingshout:
    zendingen = st.number_input("Aantal zendingen", min_value=1, value=1, step=1)
    invoer["Zendingen"] = zendingen
    if st.button("🧮 Bereken FAVV kost"):
        resultaat = bereken_fyto_verpakkingshout(int(zendingen))

# ── Other controls ─────────────────────────────────────────────────────────────
elif is_other:
    col1, col2, col3 = st.columns(3)
    with col1:
        certs = st.number_input("Aantal certificaten", min_value=1, value=1, step=1)
        invoer["Certificaten"] = certs
    with col2:
        halfuren_controle = st.number_input("Halfuren controle", min_value=0, value=1, step=1)
        invoer["Halfuren controle"] = halfuren_controle
    with col3:
        halfuren_monster = st.number_input("Halfuren monsterneming", min_value=0, value=0, step=1)
        invoer["Halfuren monsterneming"] = halfuren_monster
    if st.button("🧮 Bereken FAVV kost"):
        resultaat = bereken_other_controls(int(certs), int(halfuren_controle), int(halfuren_monster))

# ── RESULTAAT ──────────────────────────────────────────────────────────────────
if resultaat:
    st.markdown("---")
    st.markdown('<div class="step-badge">③ Resultaat</div>', unsafe_allow_html=True)

    totaal = resultaat.get("TOTAAL", 0)
    nz = resultaat.get("NZ korting toegepast", False)

    nz_html = '<div class="nz-badge">✓ Nieuw-Zeeland korting 22,5% toegepast</div>' if nz else ""

    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">Totale FAVV retributie</div>
        <div class="result-amount">€ {totaal:,.2f}</div>
        {nz_html}
    </div>
    """, unsafe_allow_html=True)

    # Kostenuitsplitsing
    st.markdown("**Kostenuitsplitsing**")
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

    # Sla op in session state voor e-mail
    st.session_state["laatste_resultaat"] = resultaat
    st.session_state["laatste_invoer"] = invoer
    st.session_state["laatste_product"] = product_type

    # ── E-MAIL SECTIE ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="step-badge">④ Rapport versturen</div>', unsafe_allow_html=True)

    with st.expander("📧 Verstuur rapport via Gmail"):
        st.info("Je hebt een `credentials.json` bestand nodig van Google Cloud (OAuth2). "
                "Zie de README voor instructies.")

        ontvanger = st.text_input("Ontvanger e-mailadres", placeholder="naam@bedrijf.com")
        creds_file = st.file_uploader("Upload credentials.json", type=["json"])

        if st.button("📤 Verstuur rapport"):
            if not ontvanger:
                st.error("Vul een e-mailadres in.")
            elif not creds_file:
                st.error("Upload je credentials.json bestand.")
            else:
                from gmail_sender import verstuur_rapport
                creds_str = creds_file.read().decode("utf-8")
                with st.spinner("Rapport verzenden..."):
                    ok = verstuur_rapport(
                        ontvanger,
                        st.session_state["laatste_product"],
                        st.session_state["laatste_invoer"],
                        st.session_state["laatste_resultaat"],
                        creds_str,
                    )
                if ok:
                    st.success(f"✅ Rapport verstuurd naar {ontvanger}")
                else:
                    st.error("❌ Verzenden mislukt. Controleer je credentials en probeer opnieuw.")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<br>
<div style="text-align:center;color:#aaa;font-size:12px;">
    Tarieven KB Retributies 2026 · Gepubliceerd 29/12/2025 · Belgisch Staatsblad
</div>
""", unsafe_allow_html=True)
