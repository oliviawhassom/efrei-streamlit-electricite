import streamlit as st

from utils.config import SOURCE_TITLE, SOURCE_PORTAL, SOURCE_LICENSE


def render():
    st.header("1. Why this matters")
    st.markdown(
        "France says it wants to cut its fossil use and add more renewables, but the electricity "
        "system is not the same everywhere. Some regions are full of nuclear plants, some have dams, "
        "some have a lot of wind, and some produce very little at all. "
        "**So the national average hides a lot of differences, and this app tries to show them.**"
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Context")
        st.markdown(
            "The data comes from RTE, the French grid operator. It gives the electricity produced "
            "each month (in GWh) in every administrative region, split by source: nuclear, thermal "
            "(gas, coal and oil), hydro, wind, solar and bioenergies. "
            "I grouped hydro, wind, solar and bioenergies as **renewable**."
        )
        st.caption("Source: " + SOURCE_TITLE + ", " + SOURCE_PORTAL + ", " + SOURCE_LICENSE)
    with c2:
        st.subheader("Who is this for and what can they learn")
        st.markdown(
            "- Students and citizens who want to understand the energy mix in their own region\n"
            "- Regional decision makers who need to compare their region with the others\n\n"
            "Three questions guide the story:\n"
            "1. Is the share of renewables really going up?\n"
            "2. Which regions are ahead, which ones are behind?\n"
            "3. What would happen if each source kept growing at a given speed?"
        )

    st.info(
        "How to use it: the filters on the left (regions, years, view) change every chart and every number. "
        "Production is not consumption. A region that produces little can still use a lot of electricity "
        "coming from other regions, so low production is not a failure by itself."
    )
