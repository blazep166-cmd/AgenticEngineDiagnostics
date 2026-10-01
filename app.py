import streamlit as st

from data_loader import (
    load_engine_data,
    load_obd_data,
    get_sensor_data
)

from diagnostics import lookup_obd_code

from agent import DiagnosticAgent


st.set_page_config(
    page_title="Engine Diagnostic Agent",
    page_icon="🔧",
    layout="wide"
)


# ==========================================================
# LOAD DATA
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


# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("🔧 Engine Diagnostic Agent")

st.write(
    "Single-agent research prototype for investigating "
    "automotive engine conditions using recorded engine "
    "sensor data and OBD-II information."
)

st.divider()


# ==========================================================
# DIAGNOSTIC INPUT
# ==========================================================

st.subheader("Diagnostic Goal")


goal_option = st.selectbox(
    "Select an investigation:",
    [
        "Cooling System Investigation",
        "Lubrication System Investigation",
        "Fuel System Investigation",
        "General Engine Investigation",
        "OBD-II Trouble Code Investigation"
    ]
)


additional_instructions = st.text_area(
    "Additional Instructions (Optional)",
    placeholder=(
        "Example: Investigate a possible overheating "
        "condition."
    )
)


obd_code = ""


if goal_option == "OBD-II Trouble Code Investigation":

    obd_code = st.text_input(
        "OBD-II Trouble Code",
        placeholder="Example: P0001"
    )


st.divider()


# ==========================================================
# START INVESTIGATION
# ==========================================================

start = st.button(
    "Start Investigation",
    type="primary",
    use_container_width=True
)


if start:

    st.header("Investigation")


    # ======================================================
    # OBD-II INVESTIGATION
    # ======================================================

    if goal_option == "OBD-II Trouble Code Investigation":

        if not obd_code:

            st.warning(
                "Enter an OBD-II trouble code."
            )

        else:

            st.subheader("Agent Activity")

            st.write(
                f"**Goal received:** Investigate {obd_code}"
            )

            st.write(
                "**Selected action:** OBD-II Code Lookup"
            )


            result = lookup_obd_code(
                obd_code,
                obd_data
            )


            if result["found"]:

                st.success(
                    f"{obd_code.upper()} found in "
                    "the OBD-II dataset."
                )

                st.subheader("Diagnostic Evidence")

                st.write(
                    f"**Code:** {result['code']}"
                )

                st.write(
                    f"**System:** {result['system']}"
                )

                st.write(
                    f"**Description:** "
                    f"{result['description']}"
                )

            else:

                st.warning(
                    f"{obd_code.upper()} was not found "
                    "in the available OBD-II dataset."
                )


    # ======================================================
    # ENGINE SENSOR INVESTIGATION
    # ======================================================

    else:

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


        st.subheader("Investigation Request")

        st.write(
            f"**Selected Goal:** {goal_option}"
        )


        if additional_instructions:

            st.write(
                f"**Additional Instructions:** "
                f"{additional_instructions}"
            )


        agent = DiagnosticAgent(
            goal=selected_goal,
            engine_data=sensor_data
        )


        # Run agent without relying on terminal output
        while agent.state["status"] == "investigating":

            action = agent.choose_action()


            if action == "stop":

                agent.state["status"] = "complete"

                break


            observation = agent.execute_action(
                action
            )


            agent.update_state(
                action,
                observation
            )


        # ==================================================
        # DISPLAY AGENT ACTIVITY
        # ==================================================

        st.subheader("Agent Activity")


        for number, observation in enumerate(
            agent.state["observations"],
            start=1
        ):

            with st.expander(
                f"Step {number}: "
                f"{observation['tool']}",
                expanded=True
            ):

                st.write(
                    f"**Sensor:** "
                    f"{observation['sensor']}"
                )

                st.write(
                    f"**Records Analyzed:** "
                    f"{observation['records_analyzed']}"
                )


                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Mean",
                        observation["mean"]
                    )

                    st.metric(
                        "Minimum",
                        observation["minimum"]
                    )


                with col2:

                    st.metric(
                        "Median",
                        observation["median"]
                    )

                    st.metric(
                        "Maximum",
                        observation["maximum"]
                    )


                with col3:

                    st.metric(
                        "Standard Deviation",
                        observation[
                            "standard_deviation"
                        ]
                    )


        # ==================================================
        # INVESTIGATION SUMMARY
        # ==================================================

        st.divider()

        st.subheader("Investigation Summary")


        st.success(
            "Investigation completed."
        )


        st.write(
            f"**Diagnostic Goal:** {goal_option}"
        )


        st.write(
            f"**Diagnostic Actions Performed:** "
            f"{len(agent.state['actions_taken'])}"
        )


        st.write(
            "**Actions Selected by Agent:**"
        )


        for action in agent.state["actions_taken"]:

            st.write(
                f"• {action}"
            )


        st.info(
            "This prototype currently reports structured "
            "diagnostic evidence. Diagnostic thresholds and "
            "adaptive evidence-based action selection will "
            "be added as the research system develops."
        )


# ==========================================================
# DATA INFORMATION
# ==========================================================

st.divider()

with st.expander("Available Research Data"):

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Engine Records",
            len(engine_data)
        )


    with col2:

        st.metric(
            "OBD-II Codes",
            len(obd_data)
        )


    st.caption(
        "The Engine Condition binary label is not provided "
        "to the diagnostic agent because its semantic "
        "definition is not established by the available "
        "dataset documentation."
    )
