import streamlit as st

from data_loader import (
    load_engine_data,
    load_obd_data,
    get_sensor_data
)

from agent import DiagnosticAgent

from diagnostic_knowledge import (
    detect_symptoms,
    get_context_question
)


st.set_page_config(
    page_title="Engine Diagnostic Agent",
    page_icon="🔧",
    layout="wide"
)


# ==========================================================
# LOAD REFERENCE DATA
# ==========================================================

@st.cache_data
def load_project_data():

    engine_data = load_engine_data(
        "engine_data.csv"
    )

    obd_data = load_obd_data(
        "Powertrain Codes.csv"
    )

    sensor_data = get_sensor_data(
        engine_data
    )

    return engine_data, obd_data, sensor_data



engine_data, obd_data, sensor_data = load_project_data()


SENSOR_UNITS = {
    "Engine rpm": "rpm",
    "Coolant temp": "°C",
    "Coolant pressure": "bar",
    "Lub oil pressure": "bar",
    "lub oil temp": "°C",
    "Fuel pressure": "bar"
}


def format_sensor_value(sensor, value):
    unit = SENSOR_UNITS.get(sensor, "")
    return f"{value} {unit}".strip()


# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("🔧 Engine Diagnostic Agent")

st.write(
    "Describe the engine problem and provide any available "
    "measurements. The agent will determine a diagnostic "
    "direction, investigate available evidence, and identify "
    "additional information that may be needed."
)

st.divider()


# ==========================================================
# REPORTED PROBLEM
# ==========================================================

st.subheader("1. Describe the Engine Problem")


symptoms = st.text_area(
    "What is happening with the engine?",
    placeholder=(
        "Example: My engine is overheating and "
        "I'm seeing white smoke."
    )
)

