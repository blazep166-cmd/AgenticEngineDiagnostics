from diagnostics import (
    analyze_case_sensor,
    lookup_obd_code
)

from diagnostic_knowledge import (
    detect_symptoms,
    determine_primary_system,
    needs_smoke_location,
    get_combined_assessment
)


class DiagnosticAgent:

    def __init__(
        self,
        goal,
        reference_data,
        case_data,
        obd_data=None,
        obd_code=None,
        symptoms="",
        smoke_location=None
    ):

        self.original_goal = goal
        self.reference_data = reference_data
        self.case_data = case_data
        self.obd_data = obd_data
        self.obd_code = obd_code
        self.symptom_text = symptoms
        self.smoke_location = smoke_location

        self.detected_symptoms = detect_symptoms(
            symptoms
        )

        # Symptoms can determine the diagnostic
        # direction automatically.
        if self.detected_symptoms:

            self.goal = determine_primary_system(
                self.detected_symptoms
            )

        else:

            self.goal = goal

        self.state = {
            "goal": self.goal,
            "original_goal": goal,
            "detected_symptoms":
                self.detected_symptoms,
            "actions_taken": [],
            "observations": [],
            "abnormal_sensors": [],
            "normal_sensors": [],
            "missing_sensors": [],
            "reasoning_log": [],
            "candidate_hypotheses": [],
            "recommended_evidence": [],
            "symptom_interpretation": None,
            "needs_context": False,
            "context_question": None,
            "status": "investigating"
        }


    # ======================================================
    # SENSOR CONFIGURATION
    # ======================================================

    def sensor_configuration(self):

        return {

            "rpm": {
                "case_key": "rpm",
                "column": "Engine rpm",
                "tool_name": "RPM Analysis"
            },

            "coolant_temperature": {
                "case_key":
                    "coolant_temperature",
                "column":
                    "Coolant temp",
                "tool_name":
                    "Coolant Temperature Analysis"
            },

            "coolant_pressure": {
                "case_key":
                    "coolant_pressure",
                "column":
                    "Coolant pressure",
                "tool_name":
                    "Coolant Pressure Analysis"
            },

            "oil_pressure": {
                "case_key":
                    "oil_pressure",
                "column":
                    "Lub oil pressure",
                "tool_name":
                    "Lubrication Oil Pressure Analysis"
            },

            "oil_temperature": {
                "case_key":
                    "oil_temperature",
                "column":
                    "lub oil temp",
                "tool_name":
                    "Lubrication Oil Temperature Analysis"
            },

            "fuel_pressure": {
                "case_key":
                    "fuel_pressure",
                "column":
                    "Fuel pressure",
                "tool_name":
                    "Fuel Pressure Analysis"
            }
        }


    # ======================================================
    # AVAILABLE DATA
    # ======================================================

    def measurement_available(self, action):

        config = self.sensor_configuration()[
            action
        ]

        value = self.case_data.get(
            config["case_key"]
        )

        return value is not None


    # ======================================================
    # SYMPTOM ANALYSIS
    # ======================================================

    def analyze_symptoms(self):

        if not self.detected_symptoms:

            self.state["reasoning_log"].append(
                "No recognized diagnostic symptoms were "
                "identified in the symptom description."
            )

            return


        self.state["reasoning_log"].append(
            "Detected symptoms: "
            + ", ".join(self.detected_symptoms)
        )


        if "overheating" in self.detected_symptoms:

            self.state["reasoning_log"].append(
                "Overheating was detected. The agent "
                "prioritized a cooling-system investigation."
            )


        if needs_smoke_location(
            self.detected_symptoms
        ):

            if not self.smoke_location:

                self.state["needs_context"] = True

                self.state["context_question"] = (
                    "Where is the white smoke coming from?"
                )

                self.state["reasoning_log"].append(
                    "White smoke was reported, but its "
                    "location is unknown. Smoke location "
                    "is needed because exhaust smoke and "
                    "engine-bay vapor support different "
                    "diagnostic directions."
                )

            else:

                self.state["reasoning_log"].append(
                    "White smoke location provided: "
                    f"{self.smoke_location}."
                )


        combined = get_combined_assessment(
            self.detected_symptoms,
            self.smoke_location
        )


        if combined:

            self.state[
                "candidate_hypotheses"
            ] = combined[
                "hypotheses"
            ]

            self.state[
                "recommended_evidence"
            ] = combined[
                "recommended_evidence"
            ]

            self.state[
                "symptom_interpretation"
            ] = combined[
                "interpretation"
            ]

            self.state["reasoning_log"].append(
                "The symptom combination produced "
                "candidate diagnostic hypotheses. "
                "These hypotheses require additional "
                "evidence before a mechanical cause "
                "can be established."
            )


    # ======================================================
    # CHOOSE FIRST ACTION
    # ======================================================

    def choose_initial_action(self):

        if self.goal == "cooling_condition":

            priority = [
                "coolant_temperature",
                "coolant_pressure",
                "rpm"
            ]

        elif self.goal == "lubrication_condition":

            priority = [
                "oil_pressure",
                "oil_temperature",
                "rpm"
            ]

        elif self.goal == "fuel_condition":

            priority = [
                "fuel_pressure",
                "rpm"
            ]

        else:

            priority = [
                "coolant_temperature",
                "oil_pressure",
                "fuel_pressure",
                "coolant_pressure",
                "oil_temperature",
                "rpm"
            ]


        for action in priority:

            if (
                self.measurement_available(action)
                and
                action
                not in self.state["actions_taken"]
            ):

                self.state["reasoning_log"].append(
                    f"Selected {action} as the next "
                    f"available measurement relevant "
                    f"to the diagnostic goal."
                )

                return action


        return "stop"


    # ======================================================
    # CHOOSE NEXT ACTION
    # ======================================================

    def choose_next_action(self):

        if not self.state["observations"]:

            return self.choose_initial_action()


        actions_taken = self.state[
            "actions_taken"
        ]

        last = self.state[
            "observations"
        ][-1]


        # Ignore OBD observation when selecting
        # another sensor action.
        if (
            last.get("tool")
            == "OBD-II Code Lookup"
        ):

            return "stop"


        sensor = last.get("sensor")
        status = last.get("status")


        # --------------------------------------------------
        # COOLING INVESTIGATION
        # --------------------------------------------------

        if self.goal == "cooling_condition":

            if (
                sensor == "Coolant temp"
                and
                status == "Unusually High"
            ):

                if (
                    self.measurement_available(
                        "coolant_pressure"
                    )
                    and
                    "coolant_pressure"
                    not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Coolant temperature was unusually "
                        "high. Coolant pressure was selected "
                        "next to gather related cooling-"
                        "system evidence."
                    )

                    return "coolant_pressure"


            if (
                sensor == "Coolant pressure"
                and
                status in [
                    "Unusually Low",
                    "Unusually High"
                ]
            ):

                if (
                    self.measurement_available("rpm")
                    and
                    "rpm"
                    not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal coolant pressure was "
                        "identified. Engine RPM was selected "
                        "to add operating-condition context."
                    )

                    return "rpm"


            return self.next_available(
                [
                    "coolant_temperature",
                    "coolant_pressure",
                    "rpm"
                ]
            )


        # --------------------------------------------------
        # LUBRICATION INVESTIGATION
        # --------------------------------------------------

        if self.goal == "lubrication_condition":

            if (
                sensor == "Lub oil pressure"
                and
                status in [
                    "Unusually Low",
                    "Unusually High"
                ]
            ):

                if (
                    self.measurement_available(
                        "oil_temperature"
                    )
                    and
                    "oil_temperature"
                    not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal oil pressure was found. "
                        "Oil temperature was selected as "
                        "related lubrication evidence."
                    )

                    return "oil_temperature"


            return self.next_available(
                [
                    "oil_pressure",
                    "oil_temperature",
                    "rpm"
                ]
            )


        # --------------------------------------------------
        # FUEL INVESTIGATION
        # --------------------------------------------------

        if self.goal == "fuel_condition":

            if (
                sensor == "Fuel pressure"
                and
                status in [
                    "Unusually Low",
                    "Unusually High"
                ]
            ):

                if (
                    self.measurement_available("rpm")
                    and
                    "rpm"
                    not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal fuel pressure was found. "
                        "Engine RPM was selected as "
                        "additional operating evidence."
                    )

                    return "rpm"


            return self.next_available(
                [
                    "fuel_pressure",
                    "rpm"
                ]
            )


        # --------------------------------------------------
        # GENERAL INVESTIGATION
        # --------------------------------------------------

        return self.next_available(
            list(
                self.sensor_configuration().keys()
            )
        )


    # ======================================================
    # NEXT AVAILABLE MEASUREMENT
    # ======================================================

    def next_available(self, actions):

        for action in actions:

            if (
                action
                not in self.state["actions_taken"]
                and
                self.measurement_available(action)
            ):

                return action

        return "stop"


    # ======================================================
    # EXECUTE ACTION
    # ======================================================

    def execute_action(self, action):

        config = self.sensor_configuration()[
            action
        ]

        actual_value = self.case_data[
            config["case_key"]
        ]

        return analyze_case_sensor(
            self.reference_data,
            config["column"],
            actual_value,
            config["tool_name"]
        )


    # ======================================================
    # UPDATE STATE
    # ======================================================

    def update_state(
        self,
        action,
        observation
    ):

        self.state[
            "actions_taken"
        ].append(action)

        self.state[
            "observations"
        ].append(observation)


        if observation[
            "status"
        ] in [
            "Unusually Low",
            "Unusually High"
        ]:

            self.state[
                "abnormal_sensors"
            ].append(action)

        else:

            self.state[
                "normal_sensors"
            ].append(action)


    # ======================================================
    # OBD-II INVESTIGATION
    # ======================================================

    def investigate_obd(self):

        if (
            not self.obd_code
            or
            self.obd_data is None
        ):

            return


        result = lookup_obd_code(
            self.obd_code,
            self.obd_data
        )


        self.state[
            "actions_taken"
        ].append(
            "obd_lookup"
        )

        self.state[
            "observations"
        ].append(
            result
        )


        if result["found"]:

            self.state[
                "reasoning_log"
            ].append(
                f"OBD-II code {result['code']} was "
                "found and added to the evidence."
            )

        else:

            self.state[
                "reasoning_log"
            ].append(
                f"OBD-II code {result['code']} was "
                "not found in the reference dataset."
            )


    # ======================================================
    # MISSING INFORMATION
    # ======================================================

    def identify_missing_information(self):

        if self.goal == "cooling_condition":

            important = [
                "coolant_temperature",
                "coolant_pressure",
                "rpm"
            ]

        elif self.goal == "lubrication_condition":

            important = [
                "oil_pressure",
                "oil_temperature",
                "rpm"
            ]

        elif self.goal == "fuel_condition":

            important = [
                "fuel_pressure",
                "rpm"
            ]

        else:

            important = list(
                self.sensor_configuration().keys()
            )


        missing = []


        for action in important:

            if not self.measurement_available(
                action
            ):

                missing.append(
                    self.sensor_configuration()[
                        action
                    ]["column"]
                )


        self.state[
            "missing_sensors"
        ] = missing


    # ======================================================
    # FINAL ASSESSMENT
    # ======================================================

    def build_assessment(self):

        abnormal = []
        normal = []
        obd_evidence = []


        for observation in self.state[
            "observations"
        ]:

            if (
                observation.get("tool")
                == "OBD-II Code Lookup"
            ):

                if observation.get("found"):

                    obd_evidence.append(
                        {
                            "code":
                                observation["code"],
                            "system":
                                observation["system"],
                            "description":
                                observation[
                                    "description"
                                ]
                        }
                    )

                continue


            evidence = {
                "sensor":
                    observation["sensor"],
                "value":
                    observation[
                        "actual_value"
                    ],
                "status":
                    observation["status"],
                "percentile":
                    observation[
                        "percentile"
                    ]
            }


            if observation["status"] in [
                "Unusually Low",
                "Unusually High"
            ]:

                abnormal.append(
                    evidence
                )

            else:

                normal.append(
                    evidence
                )


        return {
            "detected_symptoms":
                self.detected_symptoms,

            "abnormal_evidence":
                abnormal,

            "within_reference":
                normal,

            "obd_evidence":
                obd_evidence,

            "candidate_hypotheses":
                self.state[
                    "candidate_hypotheses"
                ],

            "recommended_evidence":
                self.state[
                    "recommended_evidence"
                ],

            "symptom_interpretation":
                self.state[
                    "symptom_interpretation"
                ],

            "missing_information":
                self.state[
                    "missing_sensors"
                ],

            "needs_context":
                self.state[
                    "needs_context"
                ],

            "context_question":
                self.state[
                    "context_question"
                ],

            "reasoning_log":
                self.state[
                    "reasoning_log"
                ]
        }


    # ======================================================
    # MAIN INVESTIGATION
    # ======================================================

    def investigate(self):

        # First interpret the reported symptoms.
        self.analyze_symptoms()

        # Determine which useful measurements
        # have not been supplied.
        self.identify_missing_information()


        # Investigate available sensor evidence.
        while (
            self.state["status"]
            == "investigating"
        ):

            action = self.choose_next_action()


            if action == "stop":

                self.state[
                    "status"
                ] = "complete"

                break


            observation = self.execute_action(
                action
            )


            self.update_state(
                action,
                observation
            )


        # Add OBD-II evidence if available.
        self.investigate_obd()


        self.state[
            "assessment"
        ] = self.build_assessment()


        return self.state
