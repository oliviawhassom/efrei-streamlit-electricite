raw_production_regionale.csv (about 20 MB, with the huge geo columns) is not bundled. It is downloaded
automatically the first time the app starts, or with `python scripts/download_data.py`.
Dataset page: https://www.data.gouv.fr/datasets/production-regionale-mensuelle-delectricite-par-filiere

production_regionale_light.csv is the same data (2014-01 to 2025-12, 13 regions) without the two geo columns.
The app uses it if the download fails, so the project also runs without internet.
