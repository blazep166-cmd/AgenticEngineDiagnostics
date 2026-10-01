from diagnostics import (
    analyze_case_sensor,
    lookup_obd_code
)


class DiagnosticAgent:

    def __init__(
        self,
        goal,
        reference_data,
        case_data,
        obd_data=None,
        obd_code=None
    ):

        self.goal = goal
        self.reference_data = reference_data
        self.case_data = case_data
        self.obd_data = obd_data
        self.obd_code = obd_code

        self.state = {
            "goal": goal,
            "actions_taken": [],
            "observations": [],
            "status": "investigating",
            "current_action": None,
            "abnormal_sensors": [],
            "normal_sensors": [],
            "missing_sensors": [],
            "reasoning_log": []
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
                "case_key": "coolant_temperature",
                "column": "Coolant temp",
                "tool_name": "Coolant Temperature Analysis"
            },

            "coolant_pressure": {
                "case_key": "coolant_pressure",
                "column": "Coolant pressure",
                "tool_name": "Coolant Pressure Analysis"
            },

            "oil_pressure": {
                "case_key": "oil_pressure",
                "column": "Lub oil pressure",
                "tool_name": "Lubrication Oil Pressure Analysis"
            },

            "oil_temperature": {
                "case_key": "oil_temperature",
                "column": "lub oil temp",
                "tool_name": "Lubrication Oil Temperature Analysis"
            },

            "fuel_pressure": {
                "case_key": "fuel_pressure",
                "column": "Fuel pressure",
                "tool_name": "Fuel Pressure Analysis"
            }
        }


    # ======================================================
    # CHECK WHETHER DATA EXISTS
    # ======================================================

    def measurement_available(self, action):

        config = self.sensor_configuration()[action]

        value = self.case_data.get(
            config["case_key"]
        )

        return value is not None


    # ======================================================
    # INITIAL ACTION
    # ======================================================

    def choose_initial_action(self):

        if self.goal == "cooling_condition":

            preferred_actions = [
                "coolant_temperature",
                "coolant_pressure",
                "rpm"
            ]

        elif self.goal == "lubrication_condition":

            preferred_actions = [
                "oil_pressure",
                "oil_temperature",
                "rpm"
            ]

        elif self.goal == "fuel_condition":

            preferred_actions = [
                "fuel_pressure",
                "rpm"
            ]

        else:

            preferred_actions = [
                "coolant_temperature",
                "oil_pressure",
                "fuel_pressure",
                "rpm",
                "coolant_pressure",
                "oil_temperature"
            ]


        for action in preferred_actions:

            if (
                self.measurement_available(action)
                and
                action not in self.state["actions_taken"]
            ):

                self.state["reasoning_log"].append(
                    f"Selected {action} as the initial "
                    f"measurement for the diagnostic goal."
                )

                return action


        return self.choose_any_available_sensor()


    # ======================================================
    # EVIDENCE-DRIVEN NEXT ACTION
    # ======================================================

    def choose_next_action(self):

        observations = self.state[
            "observations"
        ]

        actions_taken = self.state[
            "actions_taken"
        ]


        if not observations:

            return self.choose_initial_action()


        last_observation = observations[-1]


        # --------------------------------------------------
        # COOLING SYSTEM REASONING
        # --------------------------------------------------

        if self.goal == "cooling_condition":

            if (
                last_observation.get("sensor")
                == "Coolant temp"
                and
                last_observation.get("status")
                == "Unusually High"
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
                        "high. The agent selected coolant "
                        "pressure as the next measurement "
                        "to determine whether another "
                        "cooling-system abnormality is "
                        "present."
                    )

                    return "coolant_pressure"


            if (
                last_observation.get("sensor")
                == "Coolant pressure"
                and
                last_observation.get("status")
                in [
                    "Unusually Low",
                    "Unusually High"
                ]
            ):

                if (
                    self.measurement_available("rpm")
                    and
                    "rpm" not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal coolant pressure was "
                        "identified. The agent selected "
                        "engine RPM to examine the operating "
                        "condition associated with the "
                        "cooling-system evidence."
                    )

                    return "rpm"


            return self.choose_from_priority(
                [
                    "coolant_temperature",
                    "coolant_pressure",
                    "rpm"
                ]
            )


        # --------------------------------------------------
        # LUBRICATION SYSTEM REASONING
        # --------------------------------------------------

        elif self.goal == "lubrication_condition":

            if (
                last_observation.get("sensor")
                == "Lub oil pressure"
                and
                last_observation.get("status")
                in [
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
                        "Abnormal lubrication oil pressure "
                        "was identified. The agent selected "
                        "oil temperature to gather related "
                        "lubrication-system evidence."
                    )

                    return "oil_temperature"


            if (
                last_observation.get("sensor")
                == "lub oil temp"
                and
                last_observation.get("status")
                in [
                    "Unusually Low",
                    "Unusually High"
                ]
            ):

                if (
                    self.measurement_available("rpm")
                    and
                    "rpm" not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal oil temperature was "
                        "identified. The agent selected "
                        "engine RPM to evaluate the "
                        "associated operating condition."
                    )

                    return "rpm"


            return self.choose_from_priority(
                [
                    "oil_pressure",
                    "oil_temperature",
                    "rpm"
                ]
            )


        # --------------------------------------------------
        # FUEL SYSTEM REASONING
        # --------------------------------------------------

        elif self.goal == "fuel_condition":

            if (
                last_observation.get("sensor")
                == "Fuel pressure"
                and
                last_observation.get("status")
                in [
                    "Unusually Low",
                    "Unusually High"
                ]
            ):

                if (
                    self.measurement_available("rpm")
                    and
                    "rpm" not in actions_taken
                ):

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal fuel pressure was "
                        "identified. The agent selected "
                        "engine RPM as additional operating "
                        "evidence."
                    )

                    return "rpm"


            return self.choose_from_priority(
                [
                    "fuel_pressure",
                    "rpm"
                ]
            )


        # --------------------------------------------------
        # GENERAL ENGINE REASONING
        # --------------------------------------------------

        else:

            # If an abnormal sensor has been found,
            # investigate related evidence first.

            abnormal = self.state[
                "abnormal_sensors"
            ]


            if "coolant_temperature" in abnormal:

                action = self.first_available(
                    [
                        "coolant_pressure",
                        "rpm"
                    ]
                )

                if action:

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal coolant temperature "
                        "shifted the investigation toward "
                        "additional cooling-system evidence."
                    )

                    return action


            if "coolant_pressure" in abnormal:

                action = self.first_available(
                    [
                        "coolant_temperature",
                        "rpm"
                    ]
                )

                if action:

                    return action


            if "oil_pressure" in abnormal:

                action = self.first_available(
                    [
                        "oil_temperature",
                        "rpm"
                    ]
                )

                if action:

                    self.state[
                        "reasoning_log"
                    ].append(
                        "Abnormal oil pressure shifted the "
                        "investigation toward additional "
                        "lubrication-system evidence."
                    )

                    return action


            if "oil_temperature" in abnormal:

                action = self.first_available(
                    [
                        "oil_pressure",
                        "rpm"
                    ]
                )

                if action:

                    return action


            if "fuel_pressure" in abnormal:

                action = self.first_available(
                    [
                        "rpm"
                    ]
                )

                if action:

                    return action


            return self.choose_any_available_sensor()


    # ======================================================
    # PRIORITY HELPERS
    # ======================================================

    def choose_from_priority(self, actions):

        for action in actions:

            if (
                action not in self.state["actions_taken"]
                and
                self.measurement_available(action)
            ):

                return action

        return self.choose_any_available_sensor()


    def first_available(self, actions):

        for action in actions:

            if (
                action not in self.state["actions_taken"]
                and
                self.measurement_available(action)
            ):

                return action

        return None


    def choose_any_available_sensor(self):

        for action in self.sensor_configuration():

            if (
                action not in self.state["actions_taken"]
                and
                self.measurement_available(action)
            ):

                return action

        return "stop"


    # ======================================================
    # EXECUTE SENSOR ACTION
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
    # UPDATE AGENT STATE
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

        self.state[
            "current_action"
        ] = action


        status = observation.get(
            "status"
        )


        if status in [
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
    # IDENTIFY MISSING INFORMATION
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

                config = self.sensor_configuration()[
                    action
                ]

                missing.append(
                    config["column"]
                )


        self.state[
            "missing_sensors"
        ] = missing


    # ======================================================
    # OBD-II EVIDENCE
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
                f"found and added as diagnostic evidence."
            )

        else:

            self.state[
                "reasoning_log"
            ].append(
                f"OBD-II code {result['code']} was not "
                f"found in the available reference data."
            )


    # ======================================================
    # BUILD FINAL ASSESSMENT
    # ======================================================

    def build_assessment(self):

        abnormal_evidence = []
        within_reference = []
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

                abnormal_evidence.append(
                    evidence
                )

            else:

                within_reference.append(
                    evidence
                )


        return {
            "abnormal_evidence":
                abnormal_evidence,

            "within_reference":
                within_reference,

            "obd_evidence":
                obd_evidence,

            "missing_information":
                self.state[
                    "missing_sensors"
                ],

            "reasoning_log":
                self.state[
                    "reasoning_log"
                ]
        }


    # ======================================================
    # MAIN AGENT LOOP
    # ======================================================

    def investigate(self):

        self.identify_missing_information()


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


        # OBD evidence is investigated after the
        # sensor investigation.

        self.investigate_obd()


        self.state[
            "assessment"
        ] = self.build_assessment()


        return self.state
