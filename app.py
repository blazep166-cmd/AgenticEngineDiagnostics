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
# VISUAL DESIGN
# ==========================================================

st.markdown(
    """
    <style>
    /* Overall page */
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(47, 111, 163, 0.08), transparent 28rem),
            #f6f8fb;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Typography */
    h1 {
        letter-spacing: -0.035em;
        font-weight: 800 !important;
        margin-bottom: 0.25rem !important;
    }

    h2 {
        margin-top: 1.5rem !important;
        padding-bottom: 0.55rem;
        border-bottom: 1px solid rgba(49, 51, 63, 0.14);
        letter-spacing: -0.02em;
    }

    h3 {
        letter-spacing: -0.015em;
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 10px !important;
        border-color: rgba(49, 51, 63, 0.18) !important;
        box-shadow: none !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: rgba(47, 111, 163, 0.75) !important;
        box-shadow: 0 0 0 1px rgba(47, 111, 163, 0.25) !important;
    }

    /* Expanders become dashboard panels */
    details {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(49, 51, 63, 0.12) !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 22px rgba(15, 23, 42, 0.045);
        overflow: hidden;
    }

    /* Primary action */
    div.stButton > button[kind="primary"] {
        min-height: 3.2rem;
        border-radius: 12px;
        font-size: 1.03rem;
        font-weight: 750;
        letter-spacing: 0.01em;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
    }

    /* Status messages */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border-width: 1px;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(49, 51, 63, 0.10);
        border-radius: 12px;
        padding: 0.85rem 1rem;
    }

    /* Radio choices */
    div[role="radiogroup"] {
        gap: 0.55rem;
    }

    /* Reduce excessive default whitespace */
    hr {
        margin-top: 1.4rem !important;
        margin-bottom: 1.4rem !important;
    }

    /* Custom dashboard components */
    .prototype-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.8rem 1rem;
        margin: 0.8rem 0 1.5rem 0;
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(49, 51, 63, 0.10);
        border-radius: 12px;
    }

    .prototype-label {
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.72;
    }

    .prototype-status {
        font-size: 0.82rem;
        font-weight: 700;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        background: rgba(47, 111, 163, 0.10);
        border: 1px solid rgba(47, 111, 163, 0.20);
    }

    .section-kicker {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.58;
        margin-bottom: -0.45rem;
    }

    .flow-card {
        padding: 0.9rem 1rem;
        margin: 0.4rem 0 1rem 0;
        background: rgba(255,255,255,0.84);
        border: 1px solid rgba(49, 51, 63, 0.11);
        border-radius: 12px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.035);
        font-weight: 650;
        line-height: 1.75;
    }

    .evidence-note {
        padding: 0.8rem 1rem;
        border-left: 4px solid rgba(47, 111, 163, 0.75);
        background: rgba(47, 111, 163, 0.055);
        border-radius: 0 10px 10px 0;
        margin-bottom: 1rem;
    }

    @media (max-width: 800px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .prototype-bar {
            align-items: flex-start;
            flex-direction: column;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
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


detected_preview = detect_symptoms(
    symptoms
)


# ==========================================================
# DYNAMIC SYMPTOM CONTEXT
# ==========================================================

context = {}

if detected_preview:

    st.success(
        "Symptom identified: "
        + ", ".join(
            symptom.title()
            for symptom in detected_preview
        )
    )

    context_questions_found = False

    for symptom in detected_preview:

        question_data = get_context_question(
            symptom
        )

        if question_data:

            if not context_questions_found:

                st.subheader(
                    "Additional Diagnostic Context"
                )

                st.caption(
                    "The agent identified a symptom that "
                    "requires additional information before "
                    "the investigation can be narrowed."
                )

                context_questions_found = True

            answer = st.radio(
                question_data["question"],
                question_data["options"],
                key=f"context_{symptom}",
                horizontal=True
            )

            if answer != "Unknown":

                context[symptom] = answer


# ==========================================================
# ENGINE INFORMATION
# ==========================================================

st.divider()

st.subheader("2. Available Engine Information")

st.caption(
    "Enter only measurements you actually have. "
    "Unknown measurements can be left blank."
)


st.markdown(
    """
    <div class="evidence-note">
        <strong>Use the evidence you have.</strong><br>
        You do not need to fill in every measurement. The agent can identify
        additional evidence that may help narrow the investigation.
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


with col1:

    rpm_input = st.text_input(
        "Engine RPM (rpm)",
        placeholder="Example: 900"
    )

    coolant_temp_input = st.text_input(
        "Coolant Temperature (°C)",
        placeholder="Example: 120"
    )

    coolant_pressure_input = st.text_input(
        "Coolant Pressure (bar)",
        placeholder="Example: 1.0"
    )


with col2:

    oil_pressure_input = st.text_input(
        "Lubrication Oil Pressure (bar)",
        placeholder="Enter value if available"
    )

    oil_temp_input = st.text_input(
        "Lubrication Oil Temperature (°C)",
        placeholder="Enter value if available"
    )

    fuel_pressure_input = st.text_input(
        "Fuel Pressure (bar)",
        placeholder="Enter value if available"
    )


st.caption(
    "Working units: engine speed in rpm, temperatures in °C, and pressures "
    "in bar. Temperature and pressure units are inferred from the source "
    "dataset values because explicit unit metadata was not provided."
)

obd_code = st.text_input(
    "OBD-II Trouble Code",
    placeholder="Example: P0217"
)


# ==========================================================
# INPUT CONVERSION
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
    "Start Diagnostic Investigation",
    type="primary",
    use_container_width=True
)


if start:

    # ------------------------------------------------------
    # CONVERT ENGINE MEASUREMENTS
    # ------------------------------------------------------

    rpm = convert_value(
        rpm_input
    )

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


    entered_values = [
        rpm,
        coolant_temperature,
        coolant_pressure,
        oil_pressure,
        oil_temperature,
        fuel_pressure
    ]


    if "invalid" in entered_values:

        st.error(
            "One or more engine measurements are not "
            "valid numbers."
        )

        st.stop()


    # ------------------------------------------------------
    # BUILD CASE
    # ------------------------------------------------------

    case_data = {

        "rpm":
            rpm,

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


    # ------------------------------------------------------
    # CREATE AGENT
    # ------------------------------------------------------

    agent = DiagnosticAgent(

        goal="general_engine_condition",

        reference_data=sensor_data,

        case_data=case_data,

        obd_data=obd_data,

        obd_code=(
            obd_code.strip()
            if obd_code.strip()
            else None
        ),

        symptoms=symptoms,

        context=context
    )


    result = agent.investigate()

    assessment = result[
        "assessment"
    ]


    # ======================================================
    # INVESTIGATION OVERVIEW
    # ======================================================

    st.header(
        "Diagnostic Investigation"
    )


    if symptoms.strip():

        st.write(
            f"**Reported Problem:** {symptoms}"
        )


    detected = assessment[
        "detected_symptoms"
    ]


    if detected:

        st.subheader(
            "Symptoms Identified by Agent"
        )

        for symptom in detected:

            st.write(
                f"• {symptom.title()}"
            )

    else:

        st.warning(
            "The current prototype did not recognize "
            "a supported symptom from the description."
        )


    # ======================================================
    # DIAGNOSTIC DIRECTION
    # ======================================================

    st.subheader(
        "Diagnostic Direction"
    )


    if result["goal"] == "cooling_condition":

        st.write(
            "**Cooling system investigation selected**"
        )

    elif result["goal"] == "lubrication_condition":

        st.write(
            "**Lubrication system investigation selected**"
        )

    elif result["goal"] == "fuel_condition":

        st.write(
            "**Fuel system investigation selected**"
        )

    else:

        st.write(
            "**General engine investigation selected**"
        )


    # ======================================================
    # AGENT ACTIVITY
    # ======================================================

    st.divider()

    st.subheader(
        "Agent Investigation"
    )


    if not result["observations"]:

        st.warning(
            "No engine measurements or OBD-II evidence "
            "were available for analysis."
        )


    step_number = 1


    for observation in result[
        "observations"
    ]:

        # --------------------------------------------------
        # OBD-II RESULT
        # --------------------------------------------------

        if (
            observation.get("tool")
            == "OBD-II Code Lookup"
        ):

            with st.expander(
                f"Step {step_number}: "
                f"OBD-II Code Lookup",
                expanded=True
            ):

                st.write(
                    f"**Code:** "
                    f"{observation['code']}"
                )


                if observation[
                    "found"
                ]:

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
                        "The entered code was not found "
                        "in the available OBD-II dataset."
                    )


            step_number += 1

            continue


        # --------------------------------------------------
        # SENSOR RESULT
        # --------------------------------------------------

        with st.expander(
            f"Step {step_number}: "
            f"{observation['tool']}",
            expanded=True
        ):

            st.write(
                f"**Measurement:** "
                f"{observation['actual_value']}"
            )

            st.write(
                f"**Assessment:** "
                f"{observation['status']}"
            )

            st.write(
                f"**Reference Percentile:** "
                f"{observation['percentile']}%"
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Lower Reference",
                    observation[
                        "reference_lower"
                    ]
                )


            with col2:

                st.metric(
                    "Reference Median",
                    observation[
                        "reference_median"
                    ]
                )


            with col3:

                st.metric(
                    "Upper Reference",
                    observation[
                        "reference_upper"
                    ]
                )


        step_number += 1


    # ======================================================
    # AGENT DECISION TRACE
    # ======================================================

    st.divider()

    st.subheader(
        "Agent Decision Trace"
    )

    st.caption(
        "This section shows the agent's recorded actions "
        "and evidence-based decisions during the "
        "investigation."
    )


    reasoning_log = assessment[
        "reasoning_log"
    ]


    if reasoning_log:

        for number, reasoning in enumerate(
            reasoning_log,
            start=1
        ):

            st.write(
                f"**{number}.** {reasoning}"
            )

    else:

        st.write(
            "No diagnostic decisions were recorded."
        )


    # ======================================================
    # SENSOR EVIDENCE
    # ======================================================

    st.divider()

    st.header(
        "Diagnostic Assessment"
    )


    abnormal = assessment[
        "abnormal_evidence"
    ]

    normal = assessment[
        "within_reference"
    ]


    if abnormal:

        st.subheader(
            "Abnormal Sensor Evidence"
        )


        for evidence in abnormal:

            st.warning(
                f"{evidence['sensor']}: "
                f"{evidence['value']} — "
                f"{evidence['status']}"
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


    # ======================================================
    # OBD EVIDENCE
    # ======================================================

    obd_evidence = assessment[
        "obd_evidence"
    ]


    if obd_evidence:

        st.subheader(
            "OBD-II Evidence"
        )


        for evidence in obd_evidence:

            st.write(
                f"**{evidence['code']}** — "
                f"{evidence['description']}"
            )


    # ======================================================
    # SYMPTOM INTERPRETATION
    # ======================================================

    symptom_interpretation = assessment[
        "symptom_interpretation"
    ]


    if symptom_interpretation:

        st.subheader(
            "Symptom Interpretation"
        )

        st.write(
            symptom_interpretation
        )


    # ======================================================
    # CANDIDATE HYPOTHESES
    # ======================================================

    hypotheses = assessment[
        "candidate_hypotheses"
    ]


    if hypotheses:

        st.subheader(
            "Candidate Diagnostic Hypotheses"
        )

        st.caption(
            "These are diagnostic possibilities suggested "
            "by the symptom knowledge layer. They are not "
            "confirmed mechanical failures."
        )


        for hypothesis in hypotheses:

            st.write(
                f"• {hypothesis}"
            )


    # ======================================================
    # NEXT EVIDENCE
    # ======================================================

    recommended = assessment[
        "recommended_evidence"
    ]


    missing = assessment[
        "missing_information"
    ]


    if recommended or missing:

        st.subheader(
            "Recommended Next Evidence"
        )


        displayed = set()


        for item in recommended:

            if item not in displayed:

                st.write(
                    f"• {item}"
                )

                displayed.add(item)


        for item in missing:

            if item not in displayed:

                st.write(
                    f"• {item}"
                )

                displayed.add(item)


    # ======================================================
    # RESEARCH LIMITATION
    # ======================================================

    st.info(
        "Sensor assessments compare the entered case with "
        "the engine reference dataset. OBD-II descriptions "
        "come from the OBD-II reference dataset. Candidate "
        "diagnostic hypotheses come from the separate "
        "diagnostic knowledge layer and should not be "
        "interpreted as confirmed failures."
    )


# ==========================================================
# REFERENCE DATA INFORMATION
# ==========================================================

st.divider()


with st.expander(
    "Reference Data Information"
):

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
