import streamlit as st


def cagr(first, last, n):
    if first <= 0 or n <= 0:
        return None
    return (last / first) ** (1.0 / n) - 1


def render(ctx):
    st.header("5. Key insights and next steps")
    yearly = ctx["yearly"]
    region_tbl = ctx["region_tbl"]
    long_f = ctx["long"]

    points = []
    if len(yearly) >= 2:
        f, l = yearly.iloc[0], yearly.iloc[-1]
        points.append(
            "Renewables went from %.1f %% to %.1f %% of production between %d and %d, "
            "while nuclear went from %.1f %% to %.1f %%." % (f["renew_share"], l["renew_share"], f["year"], l["year"], f["nuclear_share"], l["nuclear_share"])
        )
        n = int(l["year"] - f["year"])
        ys = long_f.groupby(["year", "source"])["gwh"].sum().unstack()
        growth = {}
        for s in ys.columns:
            g = cagr(ys.loc[f["year"], s], ys.loc[l["year"], s], n)
            if g is not None:
                growth[s] = g
        if growth:
            s = max(growth, key=growth.get)
            points.append("The fastest growing source is %s, about %+.0f %% per year on average." % (s.lower(), 100 * growth[s]))

    if len(region_tbl) >= 2:
        hi = region_tbl.sort_values("renew_share", ascending=False).iloc[0]
        lo = region_tbl.sort_values("renew_share").iloc[0]
        points.append(
            "%s has the highest renewable share (%.1f %%) and %s the lowest (%.1f %%), "
            "so one national number hides big gaps." % (hi["region"], hi["renew_share"], lo["region"], lo["renew_share"])
        )

    if points:
        st.success("\n".join("- " + p for p in points))
    else:
        st.info("Select at least two years and two regions to get automatic insights.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Implications")
        st.markdown(
            "- A region with a high renewable share is not always the one that produces the most, "
            "so shares and volumes must be read together.\n"
            "- Sources that depend on the season (solar, hydro) need storage or flexible sources next to them.\n"
            "- Regional plans should look at their own starting mix instead of copying a national target."
        )
    with c2:
        st.subheader("Next steps")
        st.markdown(
            "- Add consumption data to see which regions import electricity.\n"
            "- Add installed capacity to compare production with what could be produced.\n"
            "- Use real region borders (geojson) for a proper choropleth map.\n"
            "- Add CO2 emissions per source to link the mix with climate impact."
        )

    st.caption("Correlation is not causation: this dashboard describes the mix, it does not explain why it changed.")
