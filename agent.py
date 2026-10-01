from diagnostics import (
    analyze_case_sensor,
    lookup_obd_code
)

from diagnostic_knowledge import (
    detect_symptoms,
    determine_primary_system,
    get_combined_assessment,
    get_context_question,
    get_symptom_knowledge,
    get_recommended_evidence,
    get_candidate_hypotheses
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
        context=None,
        smoke_location=None
    ):

        self.original_goal = goal
        self.reference_data = reference_data
        self.case_data = case_data
        self.obd_data = obd_data
        self.obd_code = obd_code
        self.symptom_text = symptoms

        # General diagnostic context replaces symptom-specific
        # constructor parameters. smoke_location is retained only
        # for compatibility with the current Streamlit app.
        self.context = context.copy() if context else {}

        if smoke_location and "white smoke" not in self.context:
            self.context["white smoke"] = smoke_location

        self.detected_symptoms = detect_symptoms(symptoms)

        if self.detected_symptoms:
            self.goal = determine_primary_system(
                self.detected_symptoms
            )
        else:
            self.goal = goal

        self.state = {
            "goal": self.goal,
            "original_goal": goal,
            "detected_symptoms": self.detected_symptoms,
            "context": self.context,
            "actions_taken": [],
            "observations": [],
            "abnormal_sensors": [],
            "normal_sensors": [],
            "missing_sensors": [],
            "missing_context": [],
            "reasoning_log": [],
            "candidate_hypotheses": [],
            "recommended_evidence": [],
            "symptom_interpretation": None,
            "needs_context": False,
            "context_question": None,
            "context_options": [],
            "context_symptom": None,
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
    # AVAILABLE DATA
    # ======================================================

    def measurement_available(self, action):

        config = self.sensor_configuration().get(action)

        if not config:
            return False

        value = self.case_data.get(config["case_key"])

        return value is not None

    # ======================================================
    # KNOWLEDGE HELPERS
    # ======================================================

    def symptom_measurements(self):
        """Return sensor actions relevant to the detected symptoms."""

        measurements = []

        for symptom in self.detected_symptoms:
            knowledge = get_symptom_knowledge(symptom) or {}

            for measurement in knowledge.get(
                "related_measurements",
                []
            ):
                if (
                    measurement in self.sensor_configuration()
                    and measurement not in measurements
                ):
                    measurements.append(measurement)

        return measurements

    def goal_measurements(self):
        """Fallback sensor priorities when symptom knowledge is absent."""

        if self.goal == "cooling_condition":
            return [
                "coolant_temperature",
                "coolant_pressure",
                "rpm"
            ]

        if self.goal == "lubrication_condition":
            return [
                "oil_pressure",
                "oil_temperature",
                "rpm"
            ]

        if self.goal == "fuel_condition":
            return [
                "fuel_pressure",
                "rpm"
            ]

        # General investigation no longer means "check everything."
        # If there is no symptom-specific sensor guidance, RPM is the
        # least invasive general operating measurement currently available.
        return ["rpm"]

    def relevant_measurements(self):
        """Prefer symptom-specific measurements over broad goal defaults."""

        symptom_actions = self.symptom_measurements()

        if symptom_actions:
            return symptom_actions

        return self.goal_measurements()

    # ======================================================
    # SYMPTOM ANALYSIS
    # ======================================================

    def analyze_symptoms(self):

        if not self.detected_symptoms:
            self.state["reasoning_log"].append(
                "No recognized diagnostic symptoms were identified "
                "in the symptom description. The investigation will "
                "remain general and will avoid assigning a specific "
                "mechanical cause."
            )
            return

        self.state["reasoning_log"].append(
            "Detected symptoms: "
            + ", ".join(self.detected_symptoms)
            + "."
        )

        self.state["reasoning_log"].append(
            "The reported symptoms selected the initial diagnostic "
            f"direction: {self.goal}."
        )

        # Start with symptom-level hypotheses and evidence requirements.
        # These are possibilities supplied by the structured knowledge
        # base, not confirmed diagnoses.
        self.state["candidate_hypotheses"] = (
            get_candidate_hypotheses(self.detected_symptoms)
        )

        self.state["recommended_evidence"] = (
            get_recommended_evidence(self.detected_symptoms)
        )

        # Ask for the first missing context item defined by the
        # diagnostic knowledge layer.
        context_request = get_context_question(
            self.detected_symptoms
        )

        if context_request:
            symptom = context_request["symptom"]
            supplied = self.context.get(symptom)

            if not supplied or str(supplied).lower() == "unknown":
                self.state["needs_context"] = True
                self.state["context_symptom"] = symptom
                self.state["context_question"] = (
                    context_request["question"]
                )
                self.state["context_options"] = (
                    context_request["options"]
                )
                self.state["missing_context"].append(symptom)

                self.state["reasoning_log"].append(
                    f"Additional context is needed for {symptom}: "
                    f"{context_request['question']}"
                )
            else:
                self.state["reasoning_log"].append(
                    f"Context provided for {symptom}: {supplied}."
                )

        # Existing multi-symptom assessment is currently defined for
        # overheating + white smoke. Pull white-smoke location from the
        # general context dictionary when it is available.
        smoke_location = self.context.get("white smoke")

        combined = get_combined_assessment(
            self.detected_symptoms,
            smoke_location
        )

        if combined:
            self.state["candidate_hypotheses"] = combined[
                "hypotheses"
            ]
            self.state["recommended_evidence"] = combined[
                "recommended_evidence"
            ]
            self.state["symptom_interpretation"] = combined[
                "interpretation"
            ]

            self.state["reasoning_log"].append(
                "The reported symptom combination supports a more "
                "specific diagnostic interpretation. The resulting "
                "items remain candidate hypotheses until additional "
                "evidence supports or contradicts them."
            )

    # ======================================================
    # CHOOSE FIRST ACTION
    # ======================================================

    def choose_initial_action(self):

        priority = self.relevant_measurements()

        for action in priority:
            if (
                self.measurement_available(action)
                and action not in self.state["actions_taken"]
            ):
                self.state["reasoning_log"].append(
                    f"Selected {action} because it is available and "
                    "is relevant to the reported symptom or current "
                    "diagnostic direction."
                )
                return action

        return "stop"

    # ======================================================
    # CHOOSE NEXT ACTION
    # ======================================================

    def choose_next_action(self):

        if not self.state["observations"]:
            return self.choose_initial_action()

        actions_taken = self.state["actions_taken"]
        last = self.state["observations"][-1]

        if last.get("tool") == "OBD-II Code Lookup":
            return "stop"

        sensor = last.get("sensor")
        status = last.get("status")

        # --------------------------------------------------
        # COOLING INVESTIGATION
        # --------------------------------------------------

        if self.goal == "cooling_condition":

            if (
                sensor == "Coolant temp"
                and status == "Unusually High"
                and self.measurement_available("coolant_pressure")
                and "coolant_pressure" not in actions_taken
            ):
                self.state["reasoning_log"].append(
                    "Coolant temperature was unusually high. "
                    "Coolant pressure was selected next because it "
                    "provides related cooling-system evidence."
                )
                return "coolant_pressure"

            if (
                sensor == "Coolant pressure"
                and status in ["Unusually Low", "Unusually High"]
                and self.measurement_available("rpm")
                and "rpm" not in actions_taken
            ):
                self.state["reasoning_log"].append(
                    "Coolant pressure was outside the reference range. "
                    "Engine RPM was selected to add operating-condition "
                    "context."
                )
                return "rpm"

            return self.next_available(
                self.relevant_measurements()
            )

        # --------------------------------------------------
        # LUBRICATION INVESTIGATION
        # --------------------------------------------------

        if self.goal == "lubrication_condition":

            if (
                sensor == "Lub oil pressure"
                and status in ["Unusually Low", "Unusually High"]
                and self.measurement_available("oil_temperature")
                and "oil_temperature" not in actions_taken
            ):
                self.state["reasoning_log"].append(
                    "Oil pressure was outside the reference range. "
                    "Oil temperature was selected as related "
                    "lubrication-system evidence."
                )
                return "oil_temperature"

            return self.next_available(
                self.relevant_measurements()
            )

        # --------------------------------------------------
        # FUEL INVESTIGATION
        # --------------------------------------------------

        if self.goal == "fuel_condition":

            if (
                sensor == "Fuel pressure"
                and status in ["Unusually Low", "Unusually High"]
                and self.measurement_available("rpm")
                and "rpm" not in actions_taken
            ):
                self.state["reasoning_log"].append(
                    "Fuel pressure was outside the reference range. "
                    "Engine RPM was selected as additional operating "
                    "evidence."
                )
                return "rpm"

            return self.next_available(
                self.relevant_measurements()
            )

        # --------------------------------------------------
        # GENERAL / SYMPTOM-SPECIFIC INVESTIGATION
        # --------------------------------------------------

        # This is the major change from the previous agent. A general
        # investigation no longer cycles through every sensor simply
        # because it exists. It stays inside the measurements identified
        # as relevant by the symptom knowledge layer.
        return self.next_available(
            self.relevant_measurements()
        )

    # ======================================================
    # NEXT AVAILABLE MEASUREMENT
    # ======================================================

    def next_available(self, actions):

        for action in actions:
            if (
                action not in self.state["actions_taken"]
                and self.measurement_available(action)
            ):
                self.state["reasoning_log"].append(
                    f"Selected {action} as the next available "
                    "relevant measurement."
                )
                return action

        return "stop"

    # ======================================================
    # EXECUTE ACTION
    # ======================================================

    def execute_action(self, action):

        config = self.sensor_configuration()[action]
        actual_value = self.case_data[config["case_key"]]

        return analyze_case_sensor(
            self.reference_data,
            config["column"],
            actual_value,
            config["tool_name"]
        )

    # ======================================================
    # UPDATE STATE
    # ======================================================

    def update_state(self, action, observation):

        self.state["actions_taken"].append(action)
        self.state["observations"].append(observation)

        if observation["status"] in [
            "Unusually Low",
            "Unusually High"
        ]:
            self.state["abnormal_sensors"].append(action)

            self.state["reasoning_log"].append(
                f"{observation['sensor']} was classified as "
                f"{observation['status']} relative to the reference "
                "dataset. This is treated as abnormal evidence, not "
                "as proof of a specific mechanical failure."
            )
        else:
            self.state["normal_sensors"].append(action)

            self.state["reasoning_log"].append(
                f"{observation['sensor']} was within the current "
                "reference range. This measurement alone does not "
                "rule out the reported symptom or its possible causes."
            )

    # ======================================================
    # OBD-II INVESTIGATION
    # ======================================================

    def investigate_obd(self):

        if not self.obd_code or self.obd_data is None:
            return

        result = lookup_obd_code(
            self.obd_code,
            self.obd_data
        )

        self.state["actions_taken"].append("obd_lookup")
        self.state["observations"].append(result)

        if result["found"]:
            self.state["reasoning_log"].append(
                f"OBD-II code {result['code']} was found and added "
                "to the diagnostic evidence."
            )
        else:
            self.state["reasoning_log"].append(
                f"OBD-II code {result['code']} was not found in the "
                "available reference dataset."
            )

    # ======================================================
    # MISSING INFORMATION
    # ======================================================

    def identify_missing_information(self):

        important = self.relevant_measurements()
        missing = []

        for action in important:
            if not self.measurement_available(action):
                missing.append(
                    self.sensor_configuration()[action]["column"]
                )

        self.state["missing_sensors"] = missing

        if missing:
            self.state["reasoning_log"].append(
                "Relevant sensor evidence is currently unavailable: "
                + ", ".join(missing)
                + "."
            )

        if self.state["needs_context"]:
            self.state["reasoning_log"].append(
                "The investigation also requires additional symptom "
                "context before the diagnostic direction can be "
                "narrowed further."
            )

    # ======================================================
    # FINAL ASSESSMENT
    # ======================================================

    def build_assessment(self):

        abnormal = []
        normal = []
        obd_evidence = []

        for observation in self.state["observations"]:

            if observation.get("tool") == "OBD-II Code Lookup":
                if observation.get("found"):
                    obd_evidence.append({
                        "code": observation["code"],
                        "system": observation["system"],
                        "description": observation["description"]
                    })
                continue

            evidence = {
                "sensor": observation["sensor"],
                "value": observation["actual_value"],
                "status": observation["status"],
                "percentile": observation["percentile"]
            }

            if observation["status"] in [
                "Unusually Low",
                "Unusually High"
            ]:
                abnormal.append(evidence)
            else:
                normal.append(evidence)

        return {
            "detected_symptoms": self.detected_symptoms,
            "context": self.context,
            "abnormal_evidence": abnormal,
            "within_reference": normal,
            "obd_evidence": obd_evidence,
            "candidate_hypotheses": self.state[
                "candidate_hypotheses"
            ],
            "recommended_evidence": self.state[
                "recommended_evidence"
            ],
            "symptom_interpretation": self.state[
                "symptom_interpretation"
            ],
            "missing_information": self.state[
                "missing_sensors"
            ],
            "missing_context": self.state[
                "missing_context"
            ],
            "needs_context": self.state[
                "needs_context"
            ],
            "context_symptom": self.state[
                "context_symptom"
            ],
            "context_question": self.state[
                "context_question"
            ],
            "context_options": self.state[
                "context_options"
            ],
            "reasoning_log": self.state[
                "reasoning_log"
            ]
        }

    # ======================================================
    # MAIN INVESTIGATION
    # ======================================================

    def investigate(self):

        # 1. Interpret the reported symptoms and determine whether
        #    additional context is required.
        self.analyze_symptoms()

        # 2. Determine which symptom-relevant measurements have not
        #    been supplied with the case.
        self.identify_missing_information()

        # 3. Investigate only the relevant sensor evidence that is
        #    actually available.
        while self.state["status"] == "investigating":

            action = self.choose_next_action()

            if action == "stop":
                self.state["status"] = "complete"
                break

            observation = self.execute_action(action)
            self.update_state(action, observation)

        # 4. Add OBD-II evidence when the user supplied a code.
        self.investigate_obd()

        # 5. Build a structured assessment that keeps observations,
        #    hypotheses, missing evidence, and context separate.
        self.state["assessment"] = self.build_assessment()

        return self.state
