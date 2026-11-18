# recuperer_volumes.py
# Télécharge les volumes mensuels (EVP) du Port of Los Angeles depuis 2019
# et les enregistre dans data/volumes_pola.csv. À lancer une fois : python recuperer_volumes.py

from datetime import date
import pandas as pd

URL = "https://portoflosangeles.org/Business/statistics/Container-Statistics/Historical-TEU-Statistics-{}"
MOIS = ["january", "february", "march", "april", "may", "june", "july",
        "august", "september", "october", "november", "december"]


def nombre(texte):
    # "429,922.75" -> 429922.75 ; une case vide ("", "nan", "-") -> None
    texte = str(texte).replace(",", "").strip()
    if texte.lower() in ("", "nan", "-"):
        return None
    try:
        return float(texte)
    except ValueError:
        return None


lignes = []
for annee in range(2019, date.today().year + 1):
    # header=None : on ne se fie pas à l'en-tête, on lit les colonnes par position
    tableau = pd.read_html(URL.format(annee), match="January", header=None)[0]
    for _, l in tableau.iterrows():
        mois = str(l[0]).strip().lower()
        if mois not in MOIS:                 # on saute l'en-tête et la ligne Total
            continue
        total = nombre(l[7])                 # colonne 7 = Total TEUs
        if total is None:                    # mois pas encore publié
            continue
        lignes.append({
            "date": f"{annee}-{MOIS.index(mois) + 1:02d}-01",
            "imports": nombre(l[1]),                    # Loaded Imports
            "exports": nombre(l[4]),                    # Loaded Exports
            "vides": nombre(l[2]) + nombre(l[5]),       # Empty Imports + Empty Exports
            "total": total,
        })
    print(annee, "OK")

pola = pd.DataFrame(lignes)
pola.to_csv("data/volumes_pola.csv", index=False)
print(len(pola), "mois enregistrés dans data/volumes_pola.csv")

sources = pd.read_csv("data/sources.csv")
sources.loc[sources["source"].str.contains("Los Angeles"), "date_recuperation"] = date.today().isoformat()
sources.to_csv("data/sources.csv", index=False)
