# constants used everywhere (kept in one place so I do not repeat them)

import os

SEED = 42

# paths are built from the location of this file, so the app also works when it is not started from the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# data.gouv.fr resource (csv), dataset "Production regionale mensuelle d'electricite par filiere"
DATA_URLS = [
    "https://www.data.gouv.fr/api/1/datasets/r/27b32325-0f02-4fb2-871c-dc743af1d7db",
    # backup: same dataset straight from the producer (ODRE, opendatasoft export)
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/production-regionale-mensuelle-filiere/exports/csv?delimiter=%3B",
]
DATA_PATH = os.path.join(BASE_DIR, "data", "raw_production_regionale.csv")
# small copy of the same data without the huge geo columns, used if the download fails
DATA_LIGHT_PATH = os.path.join(BASE_DIR, "data", "production_regionale_light.csv")

SOURCE_TITLE = "Production regionale mensuelle d'electricite par filiere"
SOURCE_PORTAL = "data.gouv.fr (Open Data Reseaux Energies, RTE)"
SOURCE_LICENSE = "Licence Ouverte / Open Licence 2.0"

# nice names for the energy sources
SOURCE_LABELS = {
    "nucleaire": "Nuclear",
    "thermique": "Thermal (gas, coal, oil)",
    "hydraulique": "Hydro",
    "eolienne": "Wind",
    "solaire": "Solar",
    "bioenergies": "Bioenergies",
}

RENEWABLE = ["Hydro", "Wind", "Solar", "Bioenergies"]
LOW_CARBON_ONLY = ["Nuclear"]
FOSSIL = ["Thermal (gas, coal, oil)"]

# colorblind friendly palette (Okabe-Ito style)
COLORS = {
    "Nuclear": "#E69F00",
    "Thermal (gas, coal, oil)": "#4D4D4D",
    "Hydro": "#0072B2",
    "Wind": "#009E73",
    "Solar": "#D55E00",
    "Bioenergies": "#CC79A7",
}
GROUP_COLORS = {
    "Renewable": "#009E73",
    "Nuclear": "#E69F00",
    "Thermal (gas, coal, oil)": "#4D4D4D",
}

# approximate region centers (lat, lon), used for the bubble map
REGION_CENTERS = {
    "11": (48.71, 2.50),
    "24": (47.48, 1.68),
    "27": (47.23, 4.80),
    "28": (49.12, 0.15),
    "32": (50.05, 2.78),
    "44": (48.68, 5.98),
    "52": (47.47, -0.82),
    "53": (48.18, -2.83),
    "75": (45.15, 0.20),
    "76": (43.70, 2.15),
    "84": (45.50, 4.90),
    "93": (43.95, 6.05),
    "94": (42.15, 9.10),
}
