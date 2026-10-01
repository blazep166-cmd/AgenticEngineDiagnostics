import streamlit as st

from data_loader import (
    load_engine_data,
    load_obd_data,
    get_sensor_data
)

from agent import DiagnosticAgent


st.set_page_config(
    page_title="Engine Diagnostic Agent",
    page_icon="🔧",
    layout="wide"
)


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


st.title("🔧 Engine Diagnostic Agent")

st.write(
    "Enter available information from the engine. "
    "The diagnostic agent will investigate the case "
    "using the engine dataset and OBD-II dataset as "
    "reference information."
)

st.divider()


# ==========================================================
# DIAGNOSTIC GOAL
# ==========================================================

st.subheader("1. Diagnostic Goal")


goal_option = st.selectbox(
    "What would you like to investigate?",
    [
        "Cooling System Investigation",
        "Lubrication System Investigation",
        "Fuel System Investigation",
        "General Engine Investigation"
    ]
)


symptoms = st.text_area(
    "Describe the problem or symptoms",
    placeholder=(
        "Example: The engine is overheating after "
        "driving for approximately 20 minutes."
    )
)


# ==========================================================
# ENGINE INFORMATION
# ==========================================================

st.divider()

st.subheader("2. Available Engine Information")

st.caption(
    "Enter only the measurements you currently have. "
    "Leave unknown measurements blank."
)


col1, col2 = st.columns(2)


with col1:

    rpm_input = st.text_input(
        "Engine RPM",
        placeholder="Example: 850"
    )

    coolant_temp_input = st.text_input(
        "Coolant Temperature",
        placeholder="Example: 112"
    )

    coolant_pressure_input = st.text_input(
        "Coolant Pressure",
        placeholder="Enter value if available"
    )


with col2:

    oil_pressure_input = st.text_input(
        "Lubrication Oil Pressure",
        placeholder="Enter value if available"
    )

    oil_temp_input = st.text_input(
        "Lubrication Oil Temperature",
        placeholder="Enter value if available"
    )

    fuel_pressure_input = st.text_input(
        "Fuel Pressure",
        placeholder="Enter value if available"
    )


obd_code = st.text_input(
    "OBD-II Trouble Code (Optional)",
    placeholder="Example: P0217"
)


# ==========================================================
# CONVERT INPUT
# ==========================================================

def convert_value(value):

    if value.strip() == "":
        return None

    try:
        return float(value)

    except ValueError:
        return "invalid"


# ==========================================================
# START INVESTIGATION
# ==========================================================

st.divider()


start = st.button(
    "Start Investigation",
    type="primary",
    use_container_width=True
)


if start:

    rpm = convert_value(rpm_input)

    coolant_temperature = convert_value(
        coolant_temp_input
    )

    coolant_pressure = convert_value(
        coolant_pressure_input
    )

    oil_pressure = convert_value(
        oil_pressure_input
    )

    oil_temperature = convert_value(
        oil_temp_input
    )

    fuel_pressure = convert_value(
        fuel_pressure_input
    )


    values = [
        rpm,
        coolant_temperature,
        coolant_pressure,
        oil_pressure,
        oil_temperature,
        fuel_pressure
    ]


    if "invalid" in values:

        st.error(
            "One or more engine measurements are not "
            "valid numbers."
        )

        st.stop()


    case_data = {
        "rpm": rpm,
        "coolant_temperature":
            coolant_temperature,
        "coolant_pressure":
            coolant_pressure,
        "oil_pressure":
            oil_pressure,
        "oil_temperature":
            oil_temperature,
        "fuel_pressure":
            fuel_pressure
    }


    goal_mapping = {

        "Cooling System Investigation":
            "cooling_condition",

        "Lubrication System Investigation":
            "lubrication_condition",

        "Fuel System Investigation":
            "fuel_condition",

        "General Engine Investigation":
            "general_engine_condition"
    }


    selected_goal = goal_mapping[
        goal_option
    ]


    agent = DiagnosticAgent(
        goal=selected_goal,
        reference_data=sensor_data,
        case_data=case_data,
        obd_data=obd_data,
        obd_code=(
            obd_code.strip()
            if obd_code.strip()
            else None
        )
    )


    result = agent.investigate()


    # ======================================================
    # CASE INFORMATION
    # ======================================================

    st.header("Diagnostic Investigation")


    st.subheader("Case")

    st.write(
        f"**Diagnostic Goal:** {goal_option}"
    )


    if symptoms.strip():

        st.write(
            f"**Reported Symptoms:** {symptoms}"
        )


    # ======================================================
    # AGENT ACTIVITY
    # ======================================================

    st.subheader("Agent Activity")


    if not result["observations"]:

        st.warning(
            "No engine measurements or OBD-II code "
            "were available for the agent to investigate."
        )


    for number, observation in enumerate(
        result["observations"],
        start=1
    ):

        if observation["tool"] == "OBD-II Code Lookup":

            with st.expander(
                f"Step {number}: OBD-II Code Lookup",
                expanded=True
            ):

                st.write(
                    f"**Code investigated:** "
                    f"{observation['code']}"
                )


                if observation["found"]:

                    st.write(
                        f"**System:** "
                        f"{observation['system']}"
                    )

                    st.write(
                        f"**Description:** "
                        f"{observation['description']}"
                    )

                else:

                    st.warning(
                        "The code was not found in the "
                        "available OBD-II reference data."
                    )

            continue


        with st.expander(
            f"Step {number}: {observation['tool']}",
            expanded=True
        ):

            st.write(
                f"**Actual Engine Reading:** "
                f"{observation['actual_value']}"
            )

            st.write(
                f"**Reference Assessment:** "
                f"{observation['status']}"
            )

            st.write(
                f"**Percentile in Reference Data:** "
                f"{observation['percentile']}%"
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Reference Lower Bound",
                    observation["reference_lower"]
                )


            with col2:

                st.metric(
                    "Reference Median",
                    observation["reference_median"]
                )


            with col3:

                st.metric(
                    "Reference Upper Bound",
                    observation["reference_upper"]
                )


    # ======================================================
    # DIAGNOSTIC ASSESSMENT
    # ======================================================

    assessment = result["assessment"]


    st.divider()

    st.header("Diagnostic Assessment")


    abnormal = assessment[
        "abnormal_evidence"
    ]

    normal = assessment[
        "within_reference"
    ]

    obd_evidence = assessment[
        "obd_evidence"
    ]

    missing = assessment[
        "missing_information"
    ]


    if abnormal:

        st.warning(
            "The agent identified engine measurements "
            "outside the central reference range."
        )


        st.subheader("Abnormal Evidence")


        for evidence in abnormal:

            st.write(
                f"• **{evidence['sensor']}**: "
                f"{evidence['value']} — "
                f"{evidence['status']}"
            )


    else:

        st.success(
            "No entered engine measurements were outside "
            "the central reference range."
        )


    if normal:

        st.subheader(
            "Measurements Within Reference Range"
        )


        for evidence in normal:

            st.write(
                f"• **{evidence['sensor']}**: "
                f"{evidence['value']}"
            )


    if obd_evidence:

        st.subheader("OBD-II Evidence")


        for evidence in obd_evidence:

            st.write(
                f"• **{evidence['code']}** — "
                f"{evidence['description']}"
            )


    # ======================================================
    # MISSING INFORMATION
    # ======================================================

    if missing:

        st.subheader(
            "Additional Information That Could "
            "Support the Investigation"
        )


        for item in missing:

            st.write(
                f"• {item}"
            )


    # ======================================================
    # INTERPRETATION
    # ======================================================

    st.divider()

    st.subheader("Agent Interpretation")


    if abnormal and obd_evidence:

        st.write(
            "The investigation contains both abnormal "
            "sensor evidence and OBD-II evidence. These "
            "findings support further investigation of "
            "the selected engine system."
        )


    elif abnormal:

        st.write(
            "One or more engine measurements are unusual "
            "relative to the available reference dataset. "
            "This identifies an abnormal condition but "
            "does not by itself establish the underlying "
            "mechanical cause."
        )


    elif obd_evidence:

        st.write(
            "The OBD-II code provides diagnostic evidence "
            "relevant to the investigation. Additional "
            "engine measurements may be needed to evaluate "
            "the condition further."
        )


    else:

        st.write(
            "The currently available evidence does not "
            "identify a clear abnormal condition relative "
            "to the reference dataset. Additional engine "
            "information may be required."
        )


    st.info(
        "The reference dataset is used for comparative "
        "analysis and does not represent the specific "
        "vehicle being diagnosed. Results should therefore "
        "be interpreted as diagnostic evidence rather than "
        "a confirmed mechanical failure."
    )


# ==========================================================
# RESEARCH DATA
# ==========================================================

st.divider()


with st.expander("Reference Data Information"):

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Engine Reference Records",
            len(engine_data)
        )


    with col2:

        st.metric(
            "OBD-II Reference Codes",
            len(obd_data)
        )


    st.caption(
        "Engine measurements entered above represent the "
        "specific diagnostic case. The uploaded datasets "
        "are used as reference information by the agent."
    )
