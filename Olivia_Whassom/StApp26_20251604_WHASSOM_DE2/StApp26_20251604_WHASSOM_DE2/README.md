# Who powers the green shift? Electricity production by region in France

Individual Student Project, Streamlit data storytelling dashboard (#EFREIDataStories2026)

Author: Olivia WHASSOM, student ID 20251604, group DE2, EFREI Paris

Date: 24/10/2026

App URL: (link to add once the app is deployed on Streamlit Community Cloud)
Demo video: (link to add after recording)

## Idea of the project

France wants more renewable electricity, but the national average hides big differences between
regions. The app follows a simple story: hook, context, overview over time, deep dives (map,
comparison, seasons, what-if), data quality, then insights and next steps.

Questions answered:
1. Is the renewable share of production really increasing?
2. Which regions are ahead and which are behind?
3. What happens to the renewable share if each source keeps growing at a chosen speed?

Target audience: students, citizens and regional decision makers.

## Dataset

- Title: Production regionale mensuelle d'electricite par filiere
- Publisher: RTE, through Open Data Reseaux Energies (ODRE)
- Portal: data.gouv.fr, https://www.data.gouv.fr/datasets/production-regionale-mensuelle-delectricite-par-filiere
- Original source: https://odre.opendatasoft.com/explore/dataset/production-regionale-mensuelle-filiere/
- License: Licence Ouverte / Open Licence 2.0
- Content: monthly production in GWh per region and per source (nuclear, thermal, hydro, wind, solar, bioenergies), from 2014

The raw file is not in the zip because it is big. It is downloaded the first time you run the app
(see `utils/io.py`), and kept in `data/`.

## Two parts, same story

- `app.py`: the interactive Streamlit dashboard (main deliverable).
- `StApp26_analysis_notebook.ipynb`: the step by step analysis (cleaning, validation, features, figures with Question / Observation / Interpretation). Open it with `jupyter notebook` from the project root.

## How to run

```
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_data.py  # optional, the app does it by itself otherwise
streamlit run app.py
```

With make: `make install`, `make data`, `make run`.

## Project structure

```
app.py                  main page, sidebar filters, KPIs, cached helpers
sections/
  intro.py              hook, context, audience
  overview.py           mix over time
  deep_dives.py         map + ranking, small multiples, boxplot, seasons heatmap, what-if
  quality.py            data quality checks and limitations
  conclusions.py        insights computed from the filtered data, implications, next steps
utils/
  config.py             constants, colors, labels, region centers
  io.py                 download and read the csv
  prep.py               cleaning, long format, shares, quality report
  viz.py                chart functions (same style everywhere)
scripts/download_data.py
StApp26_analysis_notebook.ipynb
```

## Data work

- Column names are cleaned (accents, spaces) because they can change a bit between exports.
- Months are converted to dates, region codes are kept as 2 digit text.
- Duplicated (month, region) rows are dropped, missing production values are set to 0 for the sums
  (and counted in the quality section).
- Wide table turned into a long table (month, region, source, GWh) and a `group` column
  (Renewable = hydro + wind + solar + bioenergies, Nuclear, Thermal).
- Features: year, month number, total, share of each group.
- Validation: duplicates, negative values, number of regions, same number of months per region,
  gaps in the calendar, incomplete years.

## Performance

`st.cache_data` is used for loading and for every aggregation (filter, shares, region table).
Huge geo_shape columns are skipped when the csv is read. Aggregations use the filters as cache keys.

## Accessibility

- Color palette is colorblind friendly (Okabe-Ito colors) and colors are never the only information (hover values).
- Every chart has a text description under it and labeled axes with units.
- Same y scale on every small multiple.

## Limits and ethics

- Production is not consumption: imports and exports between regions are not included.
- Hydro includes pumped storage, thermal mixes gas, coal and oil.
- The publisher updates the dataset and can revise past values, so a newer download can differ a little.
- Last year is usually incomplete, so full years only is the default (can be changed in the sidebar).
- Map uses approximate region centers, not borders.
- The what-if is a simple compound growth scenario with my own assumptions, not a forecast.
- The data is aggregated by region and month, so there is no personal data.
- The dashboard shows correlations in the mix, it does not prove causes.

## Tested with

Python 3.12, streamlit 1.33+, pandas 2, plotly 5.x.
