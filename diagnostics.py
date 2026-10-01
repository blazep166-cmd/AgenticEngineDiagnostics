def compare_to_reference(
    reference_data,
    column,
    actual_value,
    tool_name
):
    values = reference_data[column].dropna()

    mean = values.mean()
    median = values.median()

    percentile = (
        (values <= actual_value).sum()
        / len(values)
    ) * 100

    lower_reference = values.quantile(0.05)
    upper_reference = values.quantile(0.95)

    if actual_value < lower_reference:
        status = "Unusually Low"

    elif actual_value > upper_reference:
        status = "Unusually High"

    else:
        status = "Within Reference Range"

    return {
        "tool": tool_name,
        "sensor": column,
        "actual_value": round(actual_value, 2),
        "status": status,
        "percentile": round(percentile, 1),
        "reference_mean": round(mean, 2),
        "reference_median": round(median, 2),
        "reference_lower": round(lower_reference, 2),
        "reference_upper": round(upper_reference, 2),
        "reference_records": len(values)
    }


def analyze_rpm(reference_data, actual_value):

    return compare_to_reference(
        reference_data,
        "Engine rpm",
        actual_value,
        "RPM Analysis"
    )


def analyze_coolant_temperature(
    reference_data,
    actual_value
):

    return compare_to_reference(
        reference_data,
        "Coolant temp",
        actual_value,
        "Coolant Temperature Analysis"
    )


def analyze_coolant_pressure(
    reference_data,
    actual_value
):

    return compare_to_reference(
        reference_data,
        "Coolant pressure",
        actual_value,
        "Coolant Pressure Analysis"
    )


def analyze_oil_pressure(
    reference_data,
    actual_value
):

    return compare_to_reference(
        reference_data,
        "Lub oil pressure",
        actual_value,
        "Lubrication Oil Pressure Analysis"
    )


def analyze_oil_temperature(
    reference_data,
    actual_value
):

    return compare_to_reference(
        reference_data,
        "lub oil temp",
        actual_value,
        "Lubrication Oil Temperature Analysis"
    )


def analyze_fuel_pressure(
    reference_data,
    actual_value
):

    return compare_to_reference(
        reference_data,
        "Fuel pressure",
        actual_value,
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
