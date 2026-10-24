import numpy as np
import pandas as pd
import streamlit as st

from utils.config import RENEWABLE, COLORS, REGION_CENTERS
from utils import viz

METRICS = {
    "Renewable share (%)": "renew_share",
    "Nuclear share (%)": "nuclear_share",
    "Thermal share (%)": "thermal_share",
    "Total production (GWh)": "total",
    "Solar (GWh)": "Solar",
    "Wind (GWh)": "Wind",
    "Hydro (GWh)": "Hydro",
}

# growth per year by default, these are only my assumptions to play with
DEFAULT_GROWTH = {
    "Solar": 10.0,
    "Wind": 6.0,
    "Hydro": 0.0,
    "Bioenergies": 2.0,
    "Nuclear": 0.0,
    "Thermal (gas, coal, oil)": -3.0,
}


def tab_map(region_tbl, metric_label):
    col = METRICS[metric_label]
    d = region_tbl.copy()
    d["lat"] = d["code"].map(lambda c: REGION_CENTERS.get(c, (np.nan, np.nan))[0])
    d["lon"] = d["code"].map(lambda c: REGION_CENTERS.get(c, (np.nan, np.nan))[1])
    d = d.dropna(subset=["lat", "lon"])

    best = region_tbl.sort_values(col, ascending=False).iloc[0]
    st.markdown("**%s is first for \"%s\" with %s.**" % (best["region"], metric_label, format(best[col], ",.1f")))

    left, right = st.columns([3, 2])
    with left:
        if len(d) == 0:
            st.warning("No coordinates for the selected regions.")
        else:
            st.plotly_chart(viz.map_chart(d, col, metric_label), use_container_width=True)
            st.caption(
                "Chart description: map of France with one bubble per region. The color shows the "
                "selected metric and the size shows the total production. Hover for details."
            )
    with right:
        n_max = max(2, len(region_tbl))
        n = st.slider("Number of regions in the ranking", 2, n_max, min(5, n_max), help="Top N regions for the selected metric")
        top = region_tbl.sort_values(col, ascending=False).head(n)
        st.plotly_chart(
            viz.bar_chart(top, x=col, y="region", title="Top %d regions" % n, xtitle=metric_label, ytitle="Region", height=380),
            use_container_width=True,
        )
        st.caption("Chart description: horizontal bars, regions sorted from highest to lowest value of the selected metric.")


def tab_compare(region_year, region_month, region_tbl):
    st.markdown("**Same scale for every panel, so the regions can be compared fairly.**")
    st.plotly_chart(viz.small_multiples(region_year), use_container_width=True)
    st.caption(
        "Chart description: one small line chart per region, x axis is the year, y axis is the "
        "renewable share (%) from 0 to 100. Hover for the exact value."
    )
    order = region_tbl.sort_values("renew_share", ascending=False)["region"].tolist()
    st.plotly_chart(viz.box_chart(region_month, order), use_container_width=True)
    st.caption(
        "Chart description: one box plot per region showing the spread of the monthly renewable "
        "share. Regions are sorted by their overall renewable share. A tall box means the share changes a lot during the year."
    )


def tab_season(long_f, sources):
    choice = st.selectbox("Source", sources, index=sources.index("Solar") if "Solar" in sources else 0)
    d = long_f[long_f["source"] == choice].groupby(["year", "month_num"], as_index=False)["gwh"].sum()
    pivot = d.pivot(index="month_num", columns="year", values="gwh")
    peak = d.groupby("month_num")["gwh"].mean().idxmax()
    names = viz.MONTH_NAMES
    st.markdown("**On average, %s production peaks in %s.**" % (choice.lower(), names[int(peak) - 1]))
    st.plotly_chart(viz.heatmap(pivot, choice), use_container_width=True)
    st.caption(
        "Chart description: heatmap, columns are years and rows are months. A darker cell means "
        "more production in GWh. It shows if the source depends on the season."
    )


def tab_whatif(long_f):
    st.markdown(
        "Play with a yearly growth rate for each source and see what happens to the renewable share. "
        "**This is a simple what-if, not a forecast.**"
    )
    last_year = int(long_f["year"].max())
    base = long_f[long_f["year"] == last_year].groupby("source")["gwh"].sum()

    c1, c2 = st.columns(2)
    growth = {}
    with c1:
        for s in ["Solar", "Wind", "Hydro"]:
            if s in base.index:
                growth[s] = st.slider("%s growth per year (%%)" % s, -10.0, 30.0, DEFAULT_GROWTH[s], 0.5)
    with c2:
        for s in ["Bioenergies", "Nuclear", "Thermal (gas, coal, oil)"]:
            if s in base.index:
                growth[s] = st.slider("%s growth per year (%%)" % s, -15.0, 15.0, DEFAULT_GROWTH[s], 0.5)
    target = st.slider("Target year", last_year + 1, last_year + 15, last_year + 9)

    rows = []
    for y in range(last_year, target + 1):
        k = y - last_year
        vals = {s: base[s] * (1 + growth.get(s, 0.0) / 100.0) ** k for s in base.index}
        total = sum(vals.values())
        ren = sum(v for s, v in vals.items() if s in RENEWABLE)
        rows.append({"year": y, "renew_share": 100 * ren / total if total > 0 else np.nan, "total": total})
    proj = pd.DataFrame(rows)

    now = proj.iloc[0]["renew_share"]
    end = proj.iloc[-1]["renew_share"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Renewable share in %d (data)" % last_year, "%.1f %%" % now)
    m2.metric("Renewable share in %d (scenario)" % target, "%.1f %%" % end, "%+.1f points" % (end - now))
    m3.metric("Total production in %d (scenario)" % target, "%.0f TWh" % (proj.iloc[-1]["total"] / 1000))

    proj["scenario"] = "Scenario"
    fig = viz.line_chart(
        proj,
        x="year",
        y="renew_share",
        color="scenario",
        title="Renewable share if growth rates stay constant",
        xtitle="Year",
        ytitle="Renewable share (%)",
        cmap={"Scenario": "#009E73"},
        hline=(50, "50 %"),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Chart description: line chart of the renewable share (%) from the last year of data to the target year.")

    with st.expander("Assumptions and limits of this what-if"):
        st.markdown(
            "- Starting point is the last year in the selection (%d), for the selected regions only.\n"
            "- Each source grows by the same percentage every year (compound growth).\n"
            "- Hydro depends on the weather, one dry or wet year can change the starting point.\n"
            "- No link with consumption, prices, grid limits or political decisions.\n"
            "- Default rates are my own rough guesses to start the discussion, not official targets." % last_year
        )


def render(ctx, metric_label, sources):
    st.header("3. Deep dives")
    t1, t2, t3, t4 = st.tabs(["Map and ranking", "Compare regions", "Seasons", "What if"])
    with t1:
        tab_map(ctx["region_tbl"], metric_label)
    with t2:
        tab_compare(ctx["region_year"], ctx["region_month"], ctx["region_tbl"])
    with t3:
        tab_season(ctx["long"], sources)
    with t4:
        tab_whatif(ctx["long"])
