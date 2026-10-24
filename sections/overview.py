import streamlit as st

from utils.config import GROUP_COLORS
from utils import viz


def headline(yearly):
    if len(yearly) < 2:
        return "Only one year is selected, so there is no trend to show yet."
    first = yearly.iloc[0]
    last = yearly.iloc[-1]
    diff = last["renew_share"] - first["renew_share"]
    word = "grew" if diff >= 0 else "fell"
    return (
        "In the selected regions, the renewable share of production %s from %.1f %% in %d to %.1f %% in %d (%+.1f points)."
        % (word, first["renew_share"], int(first["year"]), last["renew_share"], int(last["year"]), diff)
    )


def render(long_f, yearly, share_mode, sources):
    st.header("2. Overview: how the mix moves over time")
    st.markdown("**" + headline(yearly) + "**")

    d = long_f[long_f["source"].isin(sources)]
    d = d.groupby(["month", "source"], as_index=False)["gwh"].sum()
    st.plotly_chart(viz.area_chart(d, share=(share_mode == "Share (%)")), use_container_width=True)
    st.caption(
        "Chart description: stacked area chart, x axis is the month, y axis is the production "
        "(GWh per month or % depending on the sidebar). Each color is one source. "
        "Hover to read the value of a source for a given month."
    )

    plot = yearly.melt(
        id_vars=["year"],
        value_vars=["renew_share", "nuclear_share", "thermal_share"],
        var_name="group",
        value_name="share",
    )
    names = {"renew_share": "Renewable", "nuclear_share": "Nuclear", "thermal_share": "Thermal (gas, coal, oil)"}
    plot["group"] = plot["group"].map(names)
    fig = viz.line_chart(
        plot,
        x="year",
        y="share",
        color="group",
        title="Yearly share of production by group",
        xtitle="Year",
        ytitle="Share of production (%)",
        cmap=GROUP_COLORS,
        hline=(50, "50 %"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Chart description: line chart of the yearly share (%) of renewable, nuclear and thermal "
        "production. A dotted line marks 50 %. Hover on a point to read the exact share."
    )
