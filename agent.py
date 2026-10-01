from diagnostics import (
    analyze_rpm,
    analyze_coolant_temperature,
    analyze_coolant_pressure,
    analyze_oil_pressure,
    analyze_oil_temperature,
    analyze_fuel_pressure,
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
            "missing_information": [],
            "status": "investigating",
            "current_action": None
        }


    def value_available(self, sensor):

        value = self.case_data.get(sensor)

        return value is not None


    def choose_action(self):

        actions = self.state["actions_taken"]


        # COOLING SYSTEM

        if self.goal == "cooling_condition":

            if (
                self.value_available("coolant_temperature")
                and "coolant_temperature" not in actions
            ):
                return "coolant_temperature"

            if (
                self.value_available("coolant_pressure")
                and "coolant_pressure" not in actions
            ):
                return "coolant_pressure"

            if (
                self.value_available("rpm")
                and "rpm" not in actions
            ):
                return "rpm"

            if (
                self.obd_code
                and "obd_lookup" not in actions
            ):
                return "obd_lookup"

            return "stop"


        # LUBRICATION SYSTEM

        elif self.goal == "lubrication_condition":

            if (
                self.value_available("oil_pressure")
                and "oil_pressure" not in actions
            ):
                return "oil_pressure"

            if (
                self.value_available("oil_temperature")
                and "oil_temperature" not in actions
            ):
                return "oil_temperature"

            if (
                self.value_available("rpm")
                and "rpm" not in actions
            ):
                return "rpm"

            if (
                self.obd_code
                and "obd_lookup" not in actions
            ):
                return "obd_lookup"

            return "stop"


        # FUEL SYSTEM

        elif self.goal == "fuel_condition":

            if (
                self.value_available("fuel_pressure")
                and "fuel_pressure" not in actions
            ):
                return "fuel_pressure"

            if (
                self.value_available("rpm")
                and "rpm" not in actions
            ):
                return "rpm"

            if (
                self.obd_code
                and "obd_lookup" not in actions
            ):
                return "obd_lookup"

            return "stop"


        # GENERAL ENGINE

        elif self.goal == "general_engine_condition":

            available_actions = [
                ("rpm", "rpm"),
                (
                    "coolant_temperature",
                    "coolant_temperature"
                ),
                (
                    "coolant_pressure",
                    "coolant_pressure"
                ),
                (
                    "oil_pressure",
                    "oil_pressure"
                ),
                (
                    "oil_temperature",
                    "oil_temperature"
                ),
                (
                    "fuel_pressure",
                    "fuel_pressure"
                )
            ]

            for action, sensor in available_actions:

                if (
                    self.value_available(sensor)
                    and action not in actions
                ):
                    return action

            if (
                self.obd_code
                and "obd_lookup" not in actions
            ):
                return "obd_lookup"

            return "stop"


        return "stop"


    def execute_action(self, action):

        if action == "rpm":

            return analyze_rpm(
                self.reference_data,
                self.case_data["rpm"]
            )


        elif action == "coolant_temperature":

            return analyze_coolant_temperature(
                self.reference_data,
                self.case_data[
                    "coolant_temperature"
                ]
            )


        elif action == "coolant_pressure":

            return analyze_coolant_pressure(
                self.reference_data,
                self.case_data[
                    "coolant_pressure"
                ]
            )


        elif action == "oil_pressure":

            return analyze_oil_pressure(
                self.reference_data,
                self.case_data[
                    "oil_pressure"
                ]
            )


        elif action == "oil_temperature":

            return analyze_oil_temperature(
                self.reference_data,
                self.case_data[
                    "oil_temperature"
                ]
            )


        elif action == "fuel_pressure":

            return analyze_fuel_pressure(
                self.reference_data,
                self.case_data[
                    "fuel_pressure"
                ]
            )


        elif action == "obd_lookup":

            if self.obd_data is None:
                return None

            return lookup_obd_code(
                self.obd_code,
                self.obd_data
            )


        return None


    def update_state(
        self,
        action,
        observation
    ):

        self.state["actions_taken"].append(
            action
        )

        if observation is not None:

            self.state["observations"].append(
                observation
            )

        self.state["current_action"] = action


    def identify_missing_information(self):

        required_by_goal = {

            "cooling_condition": {
                "coolant_temperature":
                    "Coolant temperature",
                "coolant_pressure":
                    "Coolant pressure",
                "rpm":
                    "Engine RPM"
            },

            "lubrication_condition": {
                "oil_pressure":
                    "Lubrication oil pressure",
                "oil_temperature":
                    "Lubrication oil temperature",
                "rpm":
                    "Engine RPM"
            },

            "fuel_condition": {
                "fuel_pressure":
                    "Fuel pressure",
                "rpm":
                    "Engine RPM"
            },

            "general_engine_condition": {
                "rpm":
                    "Engine RPM",
                "coolant_temperature":
                    "Coolant temperature",
                "coolant_pressure":
                    "Coolant pressure",
                "oil_pressure":
                    "Lubrication oil pressure",
                "oil_temperature":
                    "Lubrication oil temperature",
                "fuel_pressure":
                    "Fuel pressure"
            }
        }

        expected = required_by_goal.get(
            self.goal,
            {}
        )

        missing = []

        for sensor, label in expected.items():

            if not self.value_available(sensor):
                missing.append(label)

        self.state["missing_information"] = missing


    def build_assessment(self):

        abnormal = []

        normal = []

        obd_evidence = []


        for observation in self.state["observations"]:

            if observation["tool"] == "OBD-II Code Lookup":

                if observation["found"]:

                    obd_evidence.append(
                        {
                            "code":
                                observation["code"],
                            "description":
                                observation["description"]
                        }
                    )

                continue


            status = observation["status"]

            evidence = {
                "sensor":
                    observation["sensor"],
                "value":
                    observation["actual_value"],
                "status":
                    status
            }


            if status in [
                "Unusually Low",
                "Unusually High"
            ]:

                abnormal.append(evidence)

            else:

                normal.append(evidence)


        return {
            "abnormal_evidence": abnormal,
            "within_reference": normal,
            "obd_evidence": obd_evidence,
            "missing_information":
                self.state["missing_information"]
        }


    def investigate(self):

        while self.state["status"] == "investigating":

            action = self.choose_action()


            if action == "stop":

                self.state["status"] = "complete"

                break


            observation = self.execute_action(
                action
            )


            self.update_state(
                action,
                observation
            )


        self.identify_missing_information()

        self.state["assessment"] = (
            self.build_assessment()
        )


        return self.state
