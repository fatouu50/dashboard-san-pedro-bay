# Tableau de bord — Complexe portuaire de San Pedro Bay

Auteure : Fatouma Soubere Mahamoud — M2 IAMD, IA sectorielle (Université de Djibouti)

Tableau de bord Streamlit qui montre comment se porte le complexe portuaire de San Pedro Bay
(Los Angeles + Long Beach) et comment il se situe face aux autres ports du monde, dont Djibouti.

## Liens

- Tableau de bord en ligne : *(lien Streamlit Cloud à ajouter)*
- Fiche de conception : Google Docs « Fiche de conception – Tableau de bord San Pedro Bay »

## Lancer le tableau de bord

```bash
pip install -r requirements.txt
python recuperer_volumes.py          # télécharge les volumes de Los Angeles (une fois)
export AIS_API_KEY="..."             # clé aisstream.io, jamais écrite dans le code
python ais_snapshot.py               # capture AIS de 2 minutes
streamlit run app.py
```

En ligne (Streamlit Cloud), la clé AIS est placée dans **Settings → Secrets** sous le nom `AIS_API_KEY`.
Le fichier `.streamlit/secrets.toml` est exclu de GitHub par `.gitignore` : **aucune clé n'est visible dans le code.**

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `app.py` | Le tableau de bord : en-tête, 7 tuiles, 4 sections (volumes, comparaison mondiale, direct, recommandations), prévision, anomalies, alertes, bande de traçabilité |
| `recuperer_volumes.py` | Télécharge les volumes mensuels de Los Angeles depuis 2019 et note la date de récupération |
| `ais_snapshot.py` | Capture les positions AIS autour du port (aisstream.io) |
| `assets/` | Images d'illustration : `bandeau.jpg` (fond de page), `logo.jpg` (logo de l'en-tête), `credit.txt` (crédit affiché à l'écran) |
| `data/` | Données sourcées : volumes, CPPI, CNUCED, AIS, et `sources.csv` (adresse + date de chaque source) |

## Sources

Voir `data/sources.csv` (adresse et date de récupération de chaque source), également affiché en bas de l'écran, dans la bande « Traçabilité des données ».

| Source | Contenu | Récupération |
| --- | --- | --- |
| Port of Los Angeles | EVP mensuels : importations, exportations, vides, total, depuis 2019 | Script `recuperer_volumes.py` |
| Port of Long Beach | Mêmes volumes, même période | **Inaccessible** depuis Djibouti (Access Denied, 18/11/2026) ; copie Internet Archive vide (contenu chargé dynamiquement). Le code intègre Long Beach automatiquement si `data/volumes_polb.csv` est rempli. |
| Banque mondiale, CPPI 2023 et 2024 | Rang et score de 7 ports : Los Angeles, Long Beach, Djibouti, Yangshan, Shanghai, Rotterdam, Tanger Med | Copie manuelle dans `data/cppi.csv` |
| CNUCED, UNCTADstat | Escales et temps médian au port, porte-conteneurs, 2022-2023 | Fichiers BULK « Port calls: Calls by commercial market – Annual » et « Port calls: Performance indicators – Annual » (mis à jour le 28/03/2024), filtrés dans `data/cnuced.csv` |
| aisstream.io | Position, type et statut des navires | En direct (au plus une capture toutes les 10 min) |
| Open-Meteo | Vent, rafales (forecast) et vagues (marine) | En direct (au plus un appel toutes les 30 min) |

## Traitements

- **Volumes** : vides = vides importés + vides exportés ; total du complexe = Los Angeles + Long Beach, sur les mois communs.
- **Mise en cache** : les API ne sont pas rappelées à chaque actualisation (`st.cache_data`, 30 min pour la météo, 10 min pour l'AIS) ; les volumes, le CPPI et la CNUCED sont lus dans des fichiers.
- **Mois manquants** : un mois absent de la source est comblé par interpolation et signalé sous le graphique de prévision.
- **Source indisponible** : chaque tuile et chaque vue affiche un message clair au lieu de planter.

## Méthode (fonctions intelligentes)

1. **Prévision avec marge d'incertitude** : lissage exponentiel de Holt-Winters (tendance additive, saisonnalité de 12 mois). L'erreur moyenne (MAE) est mesurée sur les 12 derniers mois, le modèle étant entraîné sur les mois d'avant. La fourchette affichée vaut prévision ± MAE. La MAE est comparée à une référence simple : « même mois de l'année précédente ».
2. **Détection d'anomalies** : un mois est anormal si l'écart entre le réel et le modèle dépasse 2 écarts-types.
3. **Alerte météo** : vigilance si rafales ≥ 40 km/h, alerte si rafales ≥ 60 km/h ou vagues ≥ 2 m dans les 48 h.
4. **Recommandations** : règles simples appliquées aux indicateurs (pic prévu, mois anormal récent, part de vides élevée, météo). Le système recommande une action, le responsable de la planification la valide ou la refuse : niveau 3 d'automatisation sur 5.

## Limites

- Long Beach est absent : le site officiel refuse l'accès depuis Djibouti. Les volumes, la prévision et les anomalies portent sur Los Angeles seul.
- Les chocs (Covid 2020, congestion 2021-2022, droits de douane 2025) ne sont pas prévisibles par le modèle.
- La CNUCED ne publie pas Djibouti seul : seule la région « Afrique de l'Est » est disponible (escales, sans temps au port). La comparaison avec Djibouti passe donc par le CPPI. Dernière année CNUCED disponible : 2023.
- Les seuils météo sont des hypothèses, à valider avec la capitainerie.
- La couverture AIS gratuite est partielle : tous les navires ne sont pas visibles.
- Le CPPI (score par port) et la CNUCED (chiffres par pays) ne mesurent pas la même chose : on les lit côte à côte, sans les combiner.
- Le classement CPPI de Djibouti a été contesté par les autorités djiboutiennes.
- Photos d'illustration du bandeau et du logo (`assets/`) : usage décoratif, auteurs et licences non identifiés (voir `assets/credit.txt`). Elles ne portent aucune donnée.
- Code écrit avec l'aide d'une IA ; chaque bloc est commenté et expliqué.

## Démarche de A à Z (journal de réalisation)

| Étape | Ce qui a été fait | Résultat |
| --- | --- | --- |
| 1. Lecture du sujet et du cours | Conception guidée par la fiche en 8 rubriques du cours (Séquence 6, partie 2) | Fiche de conception + maquette |
| 2. Choix de l'outil | Streamlit (Python) : permet la prévision, l'appel aux API et la mise en ligne gratuite | `app.py` |
| 3. Volumes Los Angeles | Lecture automatique des pages « Historical TEU Statistics » 2019-2026 (`recuperer_volumes.py`) ; colonnes lues par position ; mois non publiés ignorés | 94 mois (janv. 2019 – oct. 2026), vérifiés contre le site (janv. 2019 = 852 449,5 EVP) |
| 4. Volumes Long Beach | polb.com : « Access Denied » depuis Djibouti sur tous les navigateurs ; copie Internet Archive (05/11/2026) vide (contenu chargé en JavaScript) ; signalé à l'enseignante | Absent, documenté ; le code l'intègre si `volumes_polb.csv` est rempli |
| 5. CPPI | Lecture des deux rapports PDF de la Banque mondiale (2023 ; 2020-2024) : rang officiel de chaque édition, score de la série homogène 2020-2024 | 7 ports × 2 éditions dans `cppi.csv` |
| 6. CNUCED | Téléchargement BULK des datasets « Port calls » (UNCTADstat) ; filtre porte-conteneurs, 2022-2023 ; Djibouti absent, région Afrique de l'Est retenue pour les escales | `cnuced.csv` |
| 7. AIS | Compte aisstream.io ; clé stockée hors du code (variable d'environnement en local, Secrets Streamlit en ligne) ; capture limitée à une fois toutes les 10 min | Carte des navires |
| 8. Météo | API Open-Meteo (vent, rafales) et Open-Meteo Marine (vagues), sans clé, appel limité à une fois toutes les 30 min | Tuile 7 et graphiques 72 h |
| 9. Intelligence | Holt-Winters + MAE sur 12 mois (fourchette) ; anomalies à 2 écarts-types ; seuils d'alerte météo ; règles de recommandation | Tuile 3, section Volumes, section Recommandations |
| 10. Robustesse | Chaque source manquante affiche un message clair au lieu de bloquer l'écran | Testé avec sources absentes |
| 11. Interface | Charte violet et rose, icônes au trait, tuiles à 4 éléments (valeur, référence, tendance, fraîcheur), bande de traçabilité des sources | Écran unique, lisible par un non-spécialiste |
| 12. Mise en ligne | Dépôt GitHub (sans clé) puis Streamlit Cloud, clé AIS dans les Secrets | Lien du tableau de bord |
