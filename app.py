

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
