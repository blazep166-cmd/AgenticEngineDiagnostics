from data_loader import (
    load_engine_data,
    load_obd_data,
    get_sensor_data
)

from diagnostics import lookup_obd_code

from agent import DiagnosticAgent


engine_data = load_engine_data(
    "engine_data.csv"
)

obd_data = load_obd_data(
    "Powertrain Codes.csv"
)

sensor_data = get_sensor_data(
    engine_data
)


while True:

    print("\n" + "=" * 60)
    print("AGENTIC ENGINE DIAGNOSTIC PROTOTYPE")
    print("=" * 60)

    print("""
1 - Investigate Cooling Condition
2 - Investigate Lubrication Condition
3 - Investigate Fuel Pressure Condition
4 - General Engine Investigation
5 - OBD-II Trouble Code Lookup
0 - Exit
""")

    choice = input(
        "Select diagnostic goal: "
    )


    if choice == "1":

        agent = DiagnosticAgent(
            goal="cooling_condition",
            engine_data=sensor_data
        )

        agent.investigate()


    elif choice == "2":

        agent = DiagnosticAgent(
            goal="lubrication_condition",
            engine_data=sensor_data
        )

        agent.investigate()


    elif choice == "3":

        agent = DiagnosticAgent(
            goal="fuel_condition",
            engine_data=sensor_data
        )

        agent.investigate()


    elif choice == "4":

        agent = DiagnosticAgent(
            goal="general_engine_condition",
            engine_data=sensor_data
        )

        agent.investigate()


    elif choice == "5":

        code = input(
            "Enter OBD-II code: "
        )

        result = lookup_obd_code(
            code,
            obd_data
        )

        print("\nOBD-II RESULT")

        for key, value in result.items():

            print(
                f"{key}: {value}"
            )


    elif choice == "0":

        print("Program closed.")

        break


    else:

        print("Invalid selection.")