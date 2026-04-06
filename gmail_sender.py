"""
Gmail verzender - gebruikt OAuth2 credentials om rapporten te sturen
"""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def maak_rapport_html(product_type: str, invoer: dict, resultaat: dict) -> str:
    """Genereer een mooi HTML rapport van de berekening."""
    datum = datetime.now().strftime("%d/%m/%Y %H:%M")
    totaal = resultaat.get("TOTAAL", 0)

    rijen = ""
    for k, v in resultaat.items():
        if k == "TOTAAL" or k == "NZ korting toegepast":
            continue
        rijen += f"""
        <tr>
            <td style="padding:10px 16px;border-bottom:1px solid #e8ecf0;color:#444;">{k}</td>
            <td style="padding:10px 16px;border-bottom:1px solid #e8ecf0;text-align:right;color:#222;font-weight:500;">€ {v:,.2f}</td>
        </tr>"""

    nz_badge = ""
    if resultaat.get("NZ korting toegepast"):
        nz_badge = '<span style="background:#fff3cd;color:#856404;padding:3px 10px;border-radius:12px;font-size:12px;margin-left:10px;">✓ NZ korting 22,5% toegepast</span>'

    invoer_html = "".join(
        f'<li style="margin:4px 0;color:#555;">'
        f'<strong style="color:#333;">{k}:</strong> {v}</li>'
        for k, v in invoer.items()
    )

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f4f6f9;margin:0;padding:20px;">
  <div style="max-width:620px;margin:auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 20px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#003d7a;padding:28px 32px;">
      <div style="display:flex;align-items:center;gap:16px;">
        <div style="background:#fff;border-radius:8px;padding:8px 12px;font-size:22px;font-weight:900;color:#003d7a;letter-spacing:-1px;">FAVV</div>
        <div>
          <div style="color:#fff;font-size:20px;font-weight:700;">Retributie Berekening</div>
          <div style="color:#7eb8f7;font-size:13px;">{datum}</div>
        </div>
      </div>
    </div>

    <!-- Product info -->
    <div style="padding:20px 32px 0;">
      <div style="background:#f0f4ff;border-left:4px solid #003d7a;border-radius:0 8px 8px 0;padding:14px 18px;">
        <div style="font-size:13px;color:#666;text-transform:uppercase;letter-spacing:0.5px;">Producttype</div>
        <div style="font-size:17px;font-weight:700;color:#003d7a;margin-top:2px;">{product_type} {nz_badge}</div>
      </div>
    </div>

    <!-- Invoerparameters -->
    <div style="padding:20px 32px 0;">
      <div style="font-size:12px;text-transform:uppercase;letter-spacing:0.8px;color:#999;margin-bottom:8px;">Invoerparameters</div>
      <ul style="margin:0;padding-left:18px;list-style:none;">
        {invoer_html}
      </ul>
    </div>

    <!-- Kostenoverzicht -->
    <div style="padding:20px 32px 0;">
      <div style="font-size:12px;text-transform:uppercase;letter-spacing:0.8px;color:#999;margin-bottom:8px;">Kostenoverzicht</div>
      <table style="width:100%;border-collapse:collapse;border:1px solid #e8ecf0;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#f7f9fc;">
            <th style="padding:10px 16px;text-align:left;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px;">Omschrijving</th>
            <th style="padding:10px 16px;text-align:right;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px;">Bedrag</th>
          </tr>
        </thead>
        <tbody>{rijen}</tbody>
      </table>
    </div>

    <!-- Totaal -->
    <div style="margin:20px 32px;background:#003d7a;border-radius:10px;padding:18px 24px;display:flex;justify-content:space-between;align-items:center;">
      <div style="color:#7eb8f7;font-size:14px;text-transform:uppercase;letter-spacing:1px;">TOTAAL FAVV RETRIBUTIE</div>
      <div style="color:#fff;font-size:28px;font-weight:800;">€ {totaal:,.2f}</div>
    </div>

    <!-- Footer -->
    <div style="padding:16px 32px;background:#f7f9fc;border-top:1px solid #e8ecf0;">
      <p style="margin:0;font-size:12px;color:#888;">Berekend op basis van KB Retributies 2026 (gepubliceerd 29/12/2025, Belgisch Staatsblad). Gegenereerd via FAVV Calculator app.</p>
    </div>

  </div>
</body>
</html>
"""


def verstuur_rapport(ontvanger: str, product_type: str, invoer: dict,
                     resultaat: dict, credentials_json: str) -> bool:
    """
    Verstuur een FAVV rapport via Gmail API.
    credentials_json: de inhoud van het OAuth2 credentials bestand als string
    """
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds_data = json.loads(credentials_json)
        creds = Credentials(
            token=creds_data.get("token"),
            refresh_token=creds_data.get("refresh_token"),
            token_uri=creds_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=creds_data.get("client_id"),
            client_secret=creds_data.get("client_secret"),
        )

        service = build("gmail", "v1", credentials=creds)

        totaal = resultaat.get("TOTAAL", 0)
        datum = datetime.now().strftime("%d/%m/%Y")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"FAVV Retributie – {product_type} – € {totaal:,.2f} – {datum}"
        msg["To"] = ontvanger

        html_body = maak_rapport_html(product_type, invoer, resultaat)
        msg.attach(MIMEText(html_body, "html"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True

    except Exception as e:
        print(f"Gmail fout: {e}")
        return False
