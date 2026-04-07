"""
FAVV Retributie Berekeningen - gebaseerd op KB tarieven 2026
"""

# ── TARIEVEN 2026 ─────────────────────────────────────────────────────────────

TARIEVEN = {
    # Veterinair - Import
    "vet_import_vlees_vis_per_kg": 0.0085,
    "vet_import_vlees_vis_minimum": 117.32,
    "vet_import_other_eerste_cert": 66.20,
    "vet_import_other_halfuur": 44.30,
    "vet_import_other_forfait": 58.66,
    "vet_volgende_partij_zelfde_container": 44.14,
    "vet_extra_container": 44.30,
    # Veterinair - Transit
    "vet_transit_vlees_vis_per_kg": 51.3752,
    # NZ korting
    "nz_korting": 0.225,
    # Fytosanitair
    "fyto_document_per_zending": 12.35,
    "fyto_identiteit_1_container": 12.35,
    "fyto_identiteit_meer_containers": 24.72,
    "fyto_seeds_basis": 30.90,
    "fyto_seeds_per_10kg_extra": 0.32,
    "fyto_seeds_max": 247.18,
    "fyto_seeds_basis_tot_kg": 100,
    "fyto_fruit_groenten_basis": 30.90,
    "fyto_fruit_groenten_per_1000kg_extra": 1.22,
    "fyto_fruit_groenten_basis_tot_kg": 25000,
    "fyto_aardappelen_per_25t": 92.69,
    "fyto_hout_basis": 30.90,
    "fyto_hout_per_m3_extra": 0.32,
    "fyto_cereals_basis": 30.90,
    "fyto_cereals_per_1000kg_extra": 1.22,
    "fyto_cereals_max": 1235.88,
    "fyto_cereals_basis_tot_kg": 25000,
    "fyto_verpakkingshout_per_zending": 30.90,
    # Other controls
    "other_eerste_cert": 66.20,
    "other_halfuur": 44.30,
    "other_forfait": 58.66,
    "other_bijkomend_cert": 44.14,
    "other_monsterneming_per_halfuur": 33.38,
}

PRODUCT_TYPES = [
    "Vlees / Vis (veterinair)",
    "Andere dan vlees/vis - HC + NHC (veterinair)",
    "Plantaardige producten - Zaden",
    "Plantaardige producten - Fruit & Groenten",
    "Plantaardige producten - Aardappelen",
    "Plantaardige producten - Hout",
    "Plantaardige producten - Granen (Cereals)",
    "Verpakkingshout",
    "Handelsnorm / Levensmiddelen niet-dierlijk (Other controls)",
]

FLOWS = ["Import", "Transit"]
LOCATIONS = ["Rest of the World", "Nieuw-Zeeland"]


def _nz_korting(bedrag: float, locatie: str) -> float:
    if locatie == "Nieuw-Zeeland":
        return bedrag * (1 - TARIEVEN["nz_korting"])
    return bedrag


def bereken_veterinair_vlees_vis(gewicht_kg: float, flow: str, locatie: str) -> dict:
    t = TARIEVEN
    if flow == "Import":
        basis = max(gewicht_kg * t["vet_import_vlees_vis_per_kg"],
                    t["vet_import_vlees_vis_minimum"])
        totaal = _nz_korting(basis, locatie)
        return {
            "Import cost meat/fish (per kg, min €117.32)": round(basis, 2),
            "TOTAAL": round(totaal, 2),
            "NZ korting toegepast": locatie == "Nieuw-Zeeland",
        }
    else:  # Transit — NZ discount not applicable
        basis = gewicht_kg * t["vet_transit_vlees_vis_per_kg"]
        return {
            "Transit cost meat/fish (per kg)": round(basis, 2),
            "TOTAAL": round(basis, 2),
            "NZ korting toegepast": False,
        }


def bereken_veterinair_other(flow: str, locatie: str, aantal_containers: int,
                               halfuren_controle: int, volgende_partij_zelfde: int) -> dict:
    t = TARIEVEN
    if flow == "Import":
        eerste_cert = t["vet_import_other_eerste_cert"]
        halfuur_kost = halfuren_controle * t["vet_import_other_halfuur"]
        forfait = t["vet_import_other_forfait"]
        extra_containers = max(0, aantal_containers - 1) * t["vet_extra_container"]
        partij_zelfde = volgende_partij_zelfde * t["vet_volgende_partij_zelfde_container"]
        totaal = eerste_cert + halfuur_kost + forfait + extra_containers + partij_zelfde
        totaal = _nz_korting(totaal, locatie)
        return {
            "1ste certificaat": round(eerste_cert, 2),
            f"Halfuurkosten ({halfuren_controle}x)": round(halfuur_kost, 2),
            "Forfait": round(forfait, 2),
            f"Extra containers ({max(0,aantal_containers-1)}x)": round(extra_containers, 2),
            f"Volgende partij zelfde container ({volgende_partij_zelfde}x)": round(partij_zelfde, 2),
            "TOTAAL": round(totaal, 2),
            "NZ korting toegepast": locatie == "Nieuw-Zeeland",
        }
    else:  # Transit
        eerste_cert = t["vet_import_other_eerste_cert"]
        forfait = t["vet_import_other_forfait"]
        extra_halfuren = max(0, halfuren_controle - 1) * t["vet_import_other_halfuur"]
        totaal = eerste_cert + forfait + extra_halfuren
        totaal = _nz_korting(totaal, locatie)
        return {
            "Certificaat": round(eerste_cert, 2),
            "Forfait": round(forfait, 2),
            f"Extra halfuren boven 30 min ({max(0,halfuren_controle-1)}x)": round(extra_halfuren, 2),
            "TOTAAL": round(totaal, 2),
            "NZ korting toegepast": locatie == "Nieuw-Zeeland",
        }


def bereken_fyto_zaden(gewicht_kg: float, aantal_zendingen: int, aantal_containers: int) -> dict:
    t = TARIEVEN
    doc = t["fyto_document_per_zending"] * aantal_zendingen
    identiteit = (t["fyto_identiteit_1_container"] if aantal_containers <= 1
                  else t["fyto_identiteit_meer_containers"] * aantal_containers)
    if gewicht_kg <= t["fyto_seeds_basis_tot_kg"]:
        materieel = t["fyto_seeds_basis"]
    else:
        extra_kg = gewicht_kg - t["fyto_seeds_basis_tot_kg"]
        extra = (extra_kg / 10) * t["fyto_seeds_per_10kg_extra"]
        materieel = min(t["fyto_seeds_basis"] + extra, t["fyto_seeds_max"])
    totaal = doc + identiteit + materieel
    return {
        f"Documentcontrole ({aantal_zendingen} zendingen)": round(doc, 2),
        "Identiteitscontrole": round(identiteit, 2),
        "Materiële controle": round(materieel, 2),
        "TOTAAL": round(totaal, 2),
    }


def bereken_fyto_fruit_groenten(gewicht_kg: float, aantal_zendingen: int,
                                 aantal_containers: int) -> dict:
    t = TARIEVEN
    doc = t["fyto_document_per_zending"] * aantal_zendingen
    identiteit = (t["fyto_identiteit_1_container"] if aantal_containers <= 1
                  else t["fyto_identiteit_meer_containers"] * aantal_containers)
    if gewicht_kg <= t["fyto_fruit_groenten_basis_tot_kg"]:
        materieel = t["fyto_fruit_groenten_basis"]
    else:
        extra_kg = gewicht_kg - t["fyto_fruit_groenten_basis_tot_kg"]
        extra = (extra_kg / 1000) * t["fyto_fruit_groenten_per_1000kg_extra"]
        materieel = t["fyto_fruit_groenten_basis"] + extra
    totaal = doc + identiteit + materieel
    return {
        f"Documentcontrole ({aantal_zendingen} zendingen)": round(doc, 2),
        "Identiteitscontrole": round(identiteit, 2),
        "Materiële controle": round(materieel, 2),
        "TOTAAL": round(totaal, 2),
    }


def bereken_fyto_aardappelen(gewicht_kg: float, aantal_zendingen: int,
                              aantal_containers: int) -> dict:
    t = TARIEVEN
    doc = t["fyto_document_per_zending"] * aantal_zendingen
    identiteit = (t["fyto_identiteit_1_container"] if aantal_containers <= 1
                  else t["fyto_identiteit_meer_containers"] * aantal_containers)
    eenheden_25t = (gewicht_kg / 25000)
    materieel = max(1, eenheden_25t) * t["fyto_aardappelen_per_25t"]
    totaal = doc + identiteit + materieel
    return {
        f"Documentcontrole ({aantal_zendingen} zendingen)": round(doc, 2),
        "Identiteitscontrole": round(identiteit, 2),
        f"Materiële controle ({gewicht_kg:,.0f} kg)": round(materieel, 2),
        "TOTAAL": round(totaal, 2),
    }


def bereken_fyto_hout(volume_m3: float, aantal_zendingen: int, aantal_containers: int) -> dict:
    t = TARIEVEN
    doc = t["fyto_document_per_zending"] * aantal_zendingen
    identiteit = (t["fyto_identiteit_1_container"] if aantal_containers <= 1
                  else t["fyto_identiteit_meer_containers"] * aantal_containers)
    if volume_m3 <= 100:
        materieel = t["fyto_hout_basis"]
    else:
        extra_m3 = volume_m3 - 100
        materieel = t["fyto_hout_basis"] + extra_m3 * t["fyto_hout_per_m3_extra"]
    totaal = doc + identiteit + materieel
    return {
        f"Documentcontrole ({aantal_zendingen} zendingen)": round(doc, 2),
        "Identiteitscontrole": round(identiteit, 2),
        "Materiële controle": round(materieel, 2),
        "TOTAAL": round(totaal, 2),
    }


def bereken_fyto_granen(gewicht_kg: float, aantal_zendingen: int, aantal_containers: int) -> dict:
    t = TARIEVEN
    doc = t["fyto_document_per_zending"] * aantal_zendingen
    identiteit = (t["fyto_identiteit_1_container"] if aantal_containers <= 1
                  else t["fyto_identiteit_meer_containers"] * aantal_containers)
    if gewicht_kg <= t["fyto_cereals_basis_tot_kg"]:
        materieel = t["fyto_cereals_basis"]
    else:
        extra_kg = gewicht_kg - t["fyto_cereals_basis_tot_kg"]
        extra = (extra_kg / 1000) * t["fyto_cereals_per_1000kg_extra"]
        materieel = min(t["fyto_cereals_basis"] + extra, t["fyto_cereals_max"])
    totaal = doc + identiteit + materieel
    return {
        f"Documentcontrole ({aantal_zendingen} zendingen)": round(doc, 2),
        "Identiteitscontrole": round(identiteit, 2),
        "Materiële controle": round(materieel, 2),
        "TOTAAL": round(totaal, 2),
    }


def bereken_fyto_verpakkingshout(aantal_zendingen: int) -> dict:
    t = TARIEVEN
    kost = t["fyto_verpakkingshout_per_zending"] * aantal_zendingen
    return {
        f"Verpakkingshout ({aantal_zendingen} zendingen × €30,90)": round(kost, 2),
        "TOTAAL": round(kost, 2),
    }


def bereken_other_controls(aantal_certificaten: int, halfuren_controle: int,
                            halfuren_monsterneming: int) -> dict:
    t = TARIEVEN
    eerste_cert = t["other_eerste_cert"]
    forfait = t["other_forfait"]
    halfuur_kost = halfuren_controle * t["other_halfuur"]
    bijkomende_certs = max(0, aantal_certificaten - 1) * t["other_bijkomend_cert"]
    monsterneming = halfuren_monsterneming * t["other_monsterneming_per_halfuur"]
    totaal = eerste_cert + forfait + halfuur_kost + bijkomende_certs + monsterneming
    return {
        "1ste certificaat": round(eerste_cert, 2),
        "Forfait controle": round(forfait, 2),
        f"Halfuurkosten controle ({halfuren_controle}x)": round(halfuur_kost, 2),
        f"Bijkomende certificaten ({max(0,aantal_certificaten-1)}x)": round(bijkomende_certs, 2),
        f"Monsterneming ({halfuren_monsterneming} halfuren)": round(monsterneming, 2),
        "TOTAAL": round(totaal, 2),
    }
