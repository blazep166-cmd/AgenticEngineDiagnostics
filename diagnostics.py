def create_sensor_observation(data, column, tool_name):

    values = data[column].dropna()

    return {
        "tool": tool_name,
        "sensor": column,
        "records_analyzed": len(values),
        "mean": round(values.mean(), 2),
        "median": round(values.median(), 2),
        "minimum": round(values.min(), 2),
        "maximum": round(values.max(), 2),
        "standard_deviation": round(values.std(), 2)
    }


def analyze_rpm(data):

    return create_sensor_observation(
        data,
        "Engine rpm",
        "RPM Analysis"
    )


def analyze_coolant_temperature(data):

    return create_sensor_observation(
        data,
        "Coolant temp",
        "Coolant Temperature Analysis"
    )


def analyze_coolant_pressure(data):

    return create_sensor_observation(
        data,
        "Coolant pressure",
        "Coolant Pressure Analysis"
    )


def analyze_oil_pressure(data):

    return create_sensor_observation(
        data,
        "Lub oil pressure",
        "Lubrication Oil Pressure Analysis"
    )


def analyze_oil_temperature(data):

    return create_sensor_observation(
        data,
        "lub oil temp",
        "Lubrication Oil Temperature Analysis"
    )


def analyze_fuel_pressure(data):

    return create_sensor_observation(
        data,
        "Fuel pressure",
        "Fuel Pressure Analysis"
    )


def lookup_obd_code(code, obd_data):

    code = str(code).upper().strip()

    codes = (
        obd_data["Code"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    result = obd_data[codes == code]

    if result.empty:

        return {
            "tool": "OBD-II Code Lookup",
            "code": code,
            "found": False,
            "system": None,
            "description": None
        }

    record = result.iloc[0]

    return {
        "tool": "OBD-II Code Lookup",
        "code": code,
        "found": True,
        "system": record["Trouble Code System"],
        "description": record["Condition Description"]
    }