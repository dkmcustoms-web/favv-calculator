# FAVV Retributie Calculator 🔍

Streamlit app om FAVV-retributies te berekenen op basis van de **KB-tarieven 2026** (gepubliceerd 29/12/2025, Belgisch Staatsblad). Inclusief Gmail-integratie om rapporten automatisch te versturen.

---

## 📁 Bestandsoverzicht

| Bestand | Functie |
|---|---|
| `app.py` | Streamlit gebruikersinterface |
| `berekeningen.py` | Alle FAVV-tarieflogica (vervangt de Excel) |
| `gmail_sender.py` | Gmail API integratie |
| `requirements.txt` | Python packages |

---

## 🚀 Stap 1 — GitHub repository aanmaken

1. Ga naar [github.com](https://github.com) en log in
2. Klik op **"New repository"** (groene knop rechtsboven)
3. Geef het de naam: `favv-calculator`
4. Zet op **Public** (nodig voor gratis Streamlit hosting)
5. Klik **"Create repository"**
6. Upload alle bestanden via **"Add file → Upload files"**

---

## 🔑 Stap 2 — Gmail API instellen (eenmalig, ~10 minuten)

### 2a. Google Cloud project aanmaken
1. Ga naar [console.cloud.google.com](https://console.cloud.google.com)
2. Klik bovenaan op **"Select a project" → "New Project"**
3. Naam: `favv-calculator` → **Create**

### 2b. Gmail API inschakelen
1. Ga naar **"APIs & Services" → "Library"**
2. Zoek **"Gmail API"** → klik erop → **"Enable"**

### 2c. OAuth2 credentials aanmaken
1. Ga naar **"APIs & Services" → "Credentials"**
2. Klik **"+ Create Credentials" → "OAuth client ID"**
3. Als gevraagd: stel eerst de **OAuth consent screen** in:
   - User Type: **External**
   - App name: `FAVV Calculator`
   - Support email: jouw Gmail
   - Voeg je Gmail toe als **Test user**
4. Terug bij credentials:
   - Application type: **Desktop app**
   - Name: `favv-calculator`
   - Klik **Create**
5. Download het JSON bestand → sla op als `credentials.json`

> ⚠️ Deel dit bestand **nooit** publiek. Upload het alleen rechtstreeks in de app.

---

## 🌐 Stap 3 — Deployen op Streamlit Cloud (gratis)

1. Ga naar [share.streamlit.io](https://share.streamlit.io)
2. Log in met je GitHub account
3. Klik **"New app"**
4. Kies:
   - Repository: `jouw-gebruikersnaam/favv-calculator`
   - Branch: `main`
   - Main file: `app.py`
5. Klik **"Deploy!"**

Na 1-2 minuten is je app live op een link zoals:
`https://jouw-naam-favv-calculator.streamlit.app`

---

## 💻 Lokaal draaien (optioneel)

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧮 Ondersteunde productcategorieën

### Veterinaire controles
- **Vlees / Vis** — import & transit, per kg (min. €117,32), NZ korting
- **Andere dan vlees/vis** — HC + NHC, forfait + halfuurkosten

### Fytosanitaire controles
- **Zaden** — basis €30,90 / 100 kg, max €247,18
- **Fruit & Groenten** — basis €30,90 / 25.000 kg
- **Aardappelen** — €92,69 per 25 ton
- **Hout** — basis €30,90 / 100 m³
- **Granen** — basis €30,90 / 25.000 kg, max €1.235,88
- **Verpakkingshout** — €30,90 per zending

### Andere controles
- **Handelsnorm / Levensmiddelen niet-dierlijk** — cert + forfait + monsterneming

---

## 📬 Gmail rapport

Na de berekening kan je op één klik een professioneel HTML-rapport versturen naar een e-mailadres. Upload je `credentials.json` tijdelijk in de app-interface.

---

## 📋 Tarieven

Alle tarieven zijn gebaseerd op het KB Retributies 2026:
- Gepubliceerd: 29/12/2025 in het Belgisch Staatsblad
- Bron: FAVV Antwerpen, brief d.d. 06/01/2026
- Nieuw-Zeeland korting: 22,5% op het volledige bedrag

---

*Vragen of aanpassingen? Open een GitHub Issue in de repository.*
