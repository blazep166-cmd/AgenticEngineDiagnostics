def analyze_case_sensor(
    data,
    column,
    actual_value,
    tool_name
):

    values = data[column].dropna()

    # Reference statistics
    mean = values.mean()
    median = values.median()
    minimum = values.min()
    maximum = values.max()
    standard_deviation = values.std()

    # Use the central 90% of the reference
    # dataset as the comparative reference range.
    lower_bound = values.quantile(0.05)
    upper_bound = values.quantile(0.95)

    # Determine where the actual case value
    # falls within the reference dataset.
    percentile = (
        (values <= actual_value).mean()
        * 100
    )

    # Classify the case measurement.
    if actual_value < lower_bound:

        status = "Unusually Low"

    elif actual_value > upper_bound:

        status = "Unusually High"

    else:

        status = "Within Reference Range"


    return {
        "tool": tool_name,
        "sensor": column,
        "actual_value": round(
            actual_value,
            2
        ),
        "status": status,
        "percentile": round(
            percentile,
            1
        ),
        "records_analyzed": len(values),
        "reference_mean": round(
            mean,
            2
        ),
        "reference_median": round(
            median,
            2
        ),
        "reference_minimum": round(
            minimum,
            2
        ),
        "reference_maximum": round(
            maximum,
            2
        ),
        "reference_lower": round(
            lower_bound,
            2
        ),
        "reference_upper": round(
            upper_bound,
            2
        ),
        "standard_deviation": round(
            standard_deviation,
            2
        )
    }


def lookup_obd_code(
    code,
    obd_data
):

    code = str(
        code
    ).upper().strip()


    codes = (
        obd_data["Code"]
        .astype(str)
        .str.upper()
        .str.strip()
    )


    result = obd_data[
        codes == code
    ]


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
        "system":
            record[
                "Trouble Code System"
            ],
        "description":
            record[
                "Condition Description"
            ]
    }
