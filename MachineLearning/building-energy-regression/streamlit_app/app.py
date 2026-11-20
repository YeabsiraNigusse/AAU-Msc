"""Estimate building loads with the fitted Ridge pipeline."""

import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from pydantic import ValidationError

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from src.design import BuildingDesign
from src.features import FEATURES


@st.cache_resource
def load_model():
    return joblib.load(APP_DIR / "ridge_model.joblib")


st.set_page_config(page_title="Building Energy Estimator", page_icon="🏠")
st.title("Building Energy Estimator")
st.write("Enter a building design to estimate its heating and cooling loads.")

with st.form("building_design"):
    geometry, glazing = st.columns(2)
    with geometry:
        st.subheader("Geometry")
        relative_compactness = st.number_input(
            "Relative compactness", min_value=0.01, max_value=1.0, value=0.82, step=0.01
        )
        surface_area = st.number_input("Surface area (m²)", min_value=0.01, value=612.50)
        wall_area = st.number_input("Wall area (m²)", min_value=0.01, value=318.50)
        roof_area = st.number_input("Roof area (m²)", min_value=0.01, value=147.00)
        overall_height = st.number_input("Overall height (m)", min_value=0.01, value=7.00)

    with glazing:
        st.subheader("Orientation and glazing")
        orientation = st.selectbox("Orientation code", (2, 3, 4, 5))
        glazing_percent = st.number_input(
            "Glazing area (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0
        )
        glazing_distribution = st.selectbox(
            "Glazing distribution code", (0, 1, 2, 3, 4, 5),
            help="Use 0 for no glazing. If glazing area is above 0%, choose a code from 1 to 5.",
        )

    submitted = st.form_submit_button("Estimate loads", type="primary")

if submitted:
    try:
        design = BuildingDesign(
            relative_compactness=relative_compactness,
            surface_area=surface_area,
            wall_area=wall_area,
            roof_area=roof_area,
            overall_height=overall_height,
            orientation=orientation,
            glazing_area=glazing_percent / 100,
            glazing_area_distribution=glazing_distribution,
        )
    except ValidationError as error:
        for issue in error.errors():
            st.error(issue["msg"].removeprefix("Value error, "))
        st.stop()

    values = design.model_dump()
    bundle = load_model()
    outside_range = [
        field.replace("_", " ")
        for field, (low, high) in bundle["training_bounds"].items()
        if not low <= values[field] <= high
    ]
    if outside_range:
        st.warning("Outside the model's training ranges: " + ", ".join(outside_range) + ".")

    frame = pd.DataFrame([values], columns=FEATURES)
    heating, cooling = bundle["pipeline"].predict(frame)[0]
    heating_column, cooling_column = st.columns(2)
    heating_column.metric("Estimated heating load", f"{heating:.2f}")
    cooling_column.metric("Estimated cooling load", f"{cooling:.2f}")

with st.expander("Model performance"):
    st.write(
        "Tuned Ridge Regression. On 128 test cases from two unseen building geometries, "
        "RMSE was 1.61 for heating and 2.81 for cooling, in the dataset's load units."
    )
