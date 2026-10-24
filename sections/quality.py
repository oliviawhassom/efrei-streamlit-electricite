import streamlit as st

from utils.prep import quality_report, missing_by_column


def render(df_raw, tables):
    st.header("4. Data quality and limitations")
    st.markdown("Checks run on the **whole** file, not only on the current filters.")

    rep = quality_report(df_raw, tables)
    n_check = int((rep["Status"] == "Check").sum())
    if n_check == 0:
        st.success("All validation checks passed.")
    else:
        st.warning("%d check(s) need attention, see the Status column." % n_check)
    st.dataframe(rep, hide_index=True, use_container_width=True)

    with st.expander("Missing values per column in the raw file"):
        st.dataframe(missing_by_column(df_raw), hide_index=True, use_container_width=True)

    st.markdown(
        "**What to keep in mind**\n"
        "- Production is not consumption, imports and exports between regions are not in this file.\n"
        "- A few monthly values are negative (probably plants that used more electricity than they produced). "
        "I set them to 0 for the mix, otherwise some shares went above 100 %.\n"
        "- Hydro includes pumped storage plants, which is a bit different from natural river or lake hydro.\n"
        "- Thermal groups gas, coal and oil together, and I could not split them here.\n"
        "- The publisher updates the dataset and can revise past values, so a newer download can differ a little.\n"
        "- The last year is often incomplete. By default I keep full years only, because summer and "
        "winter months do not have the same mix and a partial year would bias the shares.\n"
        "- Bubble positions on the map are approximate region centers, not real borders.\n"
        "- Values are aggregated by region and month, so there is no personal data and no privacy risk."
    )
