from diagnostics import (
    analyze_rpm,
    analyze_coolant_temperature,
    analyze_coolant_pressure,
    analyze_oil_pressure,
    analyze_oil_temperature,
    analyze_fuel_pressure
)


class DiagnosticAgent:

    def __init__(self, goal, engine_data):

        self.goal = goal
        self.engine_data = engine_data

        self.state = {
            "goal": goal,
            "actions_taken": [],
            "observations": [],
            "status": "investigating",
            "current_action": None
        }


    def choose_action(self):

        actions_taken = self.state["actions_taken"]

        if self.goal == "cooling_condition":

            if "coolant_temperature" not in actions_taken:
                return "coolant_temperature"

            if "coolant_pressure" not in actions_taken:
                return "coolant_pressure"

            if "rpm" not in actions_taken:
                return "rpm"

            return "stop"


        elif self.goal == "lubrication_condition":

            if "oil_pressure" not in actions_taken:
                return "oil_pressure"

            if "oil_temperature" not in actions_taken:
                return "oil_temperature"

            if "rpm" not in actions_taken:
                return "rpm"

            return "stop"


        elif self.goal == "fuel_condition":

            if "fuel_pressure" not in actions_taken:
                return "fuel_pressure"

            if "rpm" not in actions_taken:
                return "rpm"

            return "stop"


        elif self.goal == "general_engine_condition":

            available_actions = [
                "rpm",
                "coolant_temperature",
                "coolant_pressure",
                "oil_pressure",
                "oil_temperature",
                "fuel_pressure"
            ]

            for action in available_actions:

                if action not in actions_taken:
                    return action

            return "stop"


        else:
            return "stop"


    def execute_action(self, action):

        if action == "rpm":

            return analyze_rpm(
                self.engine_data
            )

        elif action == "coolant_temperature":

            return analyze_coolant_temperature(
                self.engine_data
            )

        elif action == "coolant_pressure":

            return analyze_coolant_pressure(
                self.engine_data
            )

        elif action == "oil_pressure":

            return analyze_oil_pressure(
                self.engine_data
            )

        elif action == "oil_temperature":

            return analyze_oil_temperature(
                self.engine_data
            )

        elif action == "fuel_pressure":

            return analyze_fuel_pressure(
                self.engine_data
            )

        return None


    def update_state(self, action, observation):

        self.state["actions_taken"].append(action)

        self.state["observations"].append(
            observation
        )

        self.state["current_action"] = action


    def investigate(self):

        print("\n" + "=" * 60)
        print("DIAGNOSTIC AGENT STARTED")
        print("=" * 60)

        print(
            f"\nDiagnostic Goal: {self.goal}"
        )

        while self.state["status"] == "investigating":

            action = self.choose_action()

            if action == "stop":

                self.state["status"] = "complete"

                break

            print(
                f"\nAgent selected action: {action}"
            )

            observation = self.execute_action(
                action
            )

            self.update_state(
                action,
                observation
            )

            print("\nObservation:")

            for key, value in observation.items():

                print(
                    f"  {key}: {value}"
                )

        print("\n" + "=" * 60)
        print("INVESTIGATION COMPLETE")
        print("=" * 60)

        print(
            f"Actions performed: "
            f"{len(self.state['actions_taken'])}"
        )

        return self.state