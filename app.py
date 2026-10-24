import streamlit as st

import os

from utils.io import load_data
from utils.prep import make_tables, add_shares
from utils.config import SOURCE_TITLE, SOURCE_PORTAL, SOURCE_LICENSE, BASE_DIR
from sections import intro, overview, deep_dives, quality, conclusions

st.set_page_config(page_title="Who powers the green shift?", layout="wide")

# a bit of css so the numbers are not cut and the page looks less default
st.markdown(
    """
    <style>
    .block-container {padding-top: 2.2rem;}
    div[data-testid="stMetric"] {
        background: #F1F5F2; border-left: 6px solid #009E73;
        padding: 14px 16px; border-radius: 8px;
    }
    div[data-testid="stMetricValue"] div {
        white-space: normal; overflow: visible; text-overflow: clip; font-size: 1.7rem;
    }
    h1 {color: #1F2933;}
    .subtitle {font-size: 1.1rem; color: #52606D; margin-top: -0.6rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading the dataset...")
def get_data():
    df_raw = load_data()
    tables = make_tables(df_raw)
    return df_raw, tables


@st.cache_data(show_spinner=False)
def filter_long(regions, y0, y1, full_only):
    _, tables = get_data()
    d = tables["long"]
    d = d[d["region"].isin(regions) & d["year"].between(y0, y1)]
    if full_only:
        d = d[d["year"].isin(tables["full_years"])]
    return d.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def shares_by(regions, y0, y1, full_only, by):
    return add_shares(filter_long(regions, y0, y1, full_only), list(by))


@st.cache_data(show_spinner=False)
def region_table(regions, y0, y1, full_only):
    d = filter_long(regions, y0, y1, full_only)
    tbl = shares_by(regions, y0, y1, full_only, ("region", "code"))
    per_source = d.pivot_table(index="region", columns="source", values="gwh", aggfunc="sum").reset_index()
    return tbl.merge(per_source, on="region", how="left")


try:
    raw, tables = get_data()
except Exception as e:
    st.error("Could not load the data. Check your internet connection and run `python scripts/download_data.py`.")
    st.exception(e)
    st.stop()

all_regions = sorted(tables["long"]["region"].unique())
all_sources = tables["sources"]

st.title("Who powers the green shift?")
st.markdown('<p class="subtitle">Electricity production by region in France, 2014 to 2025</p>', unsafe_allow_html=True)
st.caption("Source: %s | %s | %s" % (SOURCE_TITLE, SOURCE_PORTAL, SOURCE_LICENSE))

# ---------- sidebar ----------
with st.sidebar:
    photo = os.path.join(BASE_DIR, "assets", "olivia.jpg")
    if os.path.exists(photo):
        st.image(photo, width=110, caption="Olivia Whassom")
    st.caption("EFREI Paris, Data Visualization project 2026, group DE2")
    st.header("Filters")
    regions = st.multiselect("Regions", all_regions, default=all_regions, help="Pick the regions to include everywhere in the app.")
    full_only = st.checkbox(
        "Keep full years only",
        value=True,
        help="The last year is often incomplete. Seasons do not have the same mix, so a partial year can bias the shares.",
    )
    years = sorted(tables["full_years"]) if full_only else sorted(tables["long"]["year"].unique())
    if len(years) > 1:
        y0, y1 = st.slider("Years", int(years[0]), int(years[-1]), (int(years[0]), int(years[-1])))
    else:
        y0 = y1 = int(years[0])
    st.header("Variables")
    share_mode = st.radio("Mix chart shows", ["Production (GWh)", "Share (%)"])
    sources = st.multiselect("Sources in the mix chart", all_sources, default=all_sources)
    metric_label = st.selectbox("Metric for the map", list(deep_dives.METRICS.keys()), help="Changes the color of the map and the ranking.")

if not regions or not sources:
    st.warning("Please select at least one region and one source in the sidebar.")
    st.stop()

regions_t = tuple(regions)
long_f = filter_long(regions_t, y0, y1, full_only)
if long_f.empty:
    st.warning("No data for this selection.")
    st.stop()

# ---------- KPI row ----------
yearly = shares_by(regions_t, y0, y1, full_only, ("year",)).sort_values("year").reset_index(drop=True)
reg_tbl = region_table(regions_t, y0, y1, full_only)
period_share = 100 * long_f.loc[long_f["group"] == "Renewable", "gwh"].sum() / max(long_f["gwh"].sum(), 1)
best = reg_tbl.sort_values("renew_share", ascending=False).iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total production", "%.0f TWh" % (long_f["gwh"].sum() / 1000), help="Sum over the selected regions and years.")
c2.metric("Renewable share", "%.1f %%" % period_share, help="Hydro + wind + solar + bioenergies, divided by total production.")
if len(yearly) >= 2:
    d_pp = yearly.iloc[-1]["renew_share"] - yearly.iloc[0]["renew_share"]
    c3.metric("Change since %d" % yearly.iloc[0]["year"], "%+.1f pts" % d_pp, help="Renewable share of the last year minus the first year, in percentage points.")
else:
    c3.metric("Change over time", "n/a", help="Select at least two years.")
c4.metric("Most renewable region", best["region"], "%.1f %%" % best["renew_share"], delta_color="off")

ctx = {
    "long": long_f,
    "yearly": yearly,
    "region_tbl": reg_tbl,
    "region_year": shares_by(regions_t, y0, y1, full_only, ("region", "year")),
    "region_month": shares_by(regions_t, y0, y1, full_only, ("region", "month")),
}

st.divider()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. The story", "2. Overview", "3. Deep dives", "4. Data quality", "5. Insights"])
with tab1:
    intro.render()
with tab2:
    overview.render(long_f, yearly, share_mode, sources)
with tab3:
    deep_dives.render(ctx, metric_label, sources=sorted(long_f["source"].unique()))
with tab4:
    quality.render(raw, tables)
with tab5:
    conclusions.render(ctx)
