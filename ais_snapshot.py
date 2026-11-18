# ais_snapshot.py
# Écoute le flux AIS d'aisstream.io pendant quelques secondes autour de San Pedro Bay
# et enregistre la dernière position de chaque navire dans data/ais_snapshot.csv.
#
# La clé n'est JAMAIS écrite dans le code. Avant de lancer :
#   Linux :   export AIS_API_KEY="ta_cle"      puis   python ais_snapshot.py   (écoute 2 minutes)
# Sur Streamlit Cloud, la clé est dans les "Secrets" et app.py appelle capturer().

import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
from websockets.sync.client import connect

# Rectangle autour des ports de Los Angeles et Long Beach (latitude, longitude)
ZONE = [[[33.55, -118.45], [33.80, -118.05]]]

STATUTS = {0: "En route (moteur)", 1: "Au mouillage", 2: "Non manoeuvrant",
           3: "Manoeuvre restreinte", 5: "Amarré", 7: "En pêche", 8: "En route (voile)"}


def type_navire(code):
    # Codes AIS officiels : 70-79 cargo, 80-89 pétrolier, 60-69 passagers...
    if code is None:
        return "Type non reçu"
    if 70 <= code <= 79:
        return "Cargo / porte-conteneurs"
    if 80 <= code <= 89:
        return "Pétrolier"
    if 60 <= code <= 69:
        return "Passagers"
    if code in (31, 32, 52):
        return "Remorqueur"
    return "Autre"


def capturer(cle, duree=45):
    navires = {}   # un navire = une entrée, identifiée par son numéro MMSI
    types = {}
    with connect("wss://stream.aisstream.io/v0/stream", open_timeout=20) as ws:
        ws.send(json.dumps({"APIKey": cle, "BoundingBoxes": ZONE,
                            "FilterMessageTypes": ["PositionReport", "ShipStaticData"]}))
        fin = time.time() + duree
        while time.time() < fin:
            try:
                msg = json.loads(ws.recv(timeout=5))
            except TimeoutError:
                continue
            meta = msg.get("MetaData", {})
            mmsi = meta.get("MMSI")
            if msg.get("MessageType") == "ShipStaticData":
                types[mmsi] = msg["Message"]["ShipStaticData"].get("Type")
            elif msg.get("MessageType") == "PositionReport":
                pos = msg["Message"]["PositionReport"]
                navires[mmsi] = {
                    "mmsi": mmsi,
                    "nom": str(meta.get("ShipName", "")).strip(),
                    "lat": pos["Latitude"],
                    "lon": pos["Longitude"],
                    "vitesse_noeuds": pos.get("Sog"),
                    "statut": STATUTS.get(pos.get("NavigationalStatus"), "Autre / non renseigné"),
                }
    df = pd.DataFrame(navires.values())
    if not df.empty:
        df["type"] = [type_navire(types.get(m)) for m in df["mmsi"]]
    df["capture_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return df


if __name__ == "__main__":
    cle = os.environ.get("AIS_API_KEY")
    if not cle:
        raise SystemExit("Clé absente : faire  export AIS_API_KEY=\"ta_cle\"  avant de lancer le script.")
    df = capturer(cle, duree=120)
    df.to_csv("data/ais_snapshot.csv", index=False)
    print(len(df), "navires enregistrés dans data/ais_snapshot.csv")
