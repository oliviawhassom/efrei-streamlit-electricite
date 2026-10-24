import os
import unicodedata
import pandas as pd
import requests

from utils.config import DATA_URLS, DATA_PATH, DATA_LIGHT_PATH


def download_file(path=DATA_PATH, force=False):
    """Download the csv once and keep a local copy in data/."""
    if os.path.exists(path) and not force:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    last_error = None
    for url in DATA_URLS:
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            return path
        except Exception as e:
            last_error = e
            print("download failed for", url, ":", e)
    raise RuntimeError("could not download the dataset: " + str(last_error))


def keep_column(name):
    # the geo columns are called "Geo-shape region" and "Geo-point region" (with accents), they are huge json strings
    plain = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    return not plain.startswith("geo")


def read_csv_file(path):
    # the first line tells me if the separator is ; or ,
    with open(path, "r", encoding="utf-8-sig") as f:
        header = f.readline()
    sep = ";" if header.count(";") > header.count(",") else ","
    return pd.read_csv(path, sep=sep, encoding="utf-8-sig", usecols=keep_column)


def load_data(path=DATA_PATH):
    try:
        return read_csv_file(download_file(path))
    except Exception as e:
        # no internet on the server: use the light copy that is shipped with the project
        print("using the light copy of the data because:", e)
        return read_csv_file(DATA_LIGHT_PATH)
