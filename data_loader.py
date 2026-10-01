import pandas as pd


ENGINE_COLUMNS = [
    "Engine rpm",
    "Lub oil pressure",
    "Fuel pressure",
    "Coolant pressure",
    "lub oil temp",
    "Coolant temp",
    "Engine Condition"
]


OBD_COLUMNS = [
    "Code",
    "Trouble Code System",
    "Condition Description"
]


def load_engine_data(file_path):

    column_names = [
        "Engine rpm",
        "Lub oil pressure",
        "Fuel pressure",
        "Coolant pressure",
        "lub oil temp",
        "Coolant temp",
        "Engine Condition"
    ]

    data = pd.read_csv(
        file_path,
        sep=r"\s+",
        skiprows=1,
        names=column_names
    )

    if data.empty:
        raise ValueError("Engine dataset is empty.")

    return data


def load_obd_data(file_path):

    data = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in OBD_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"OBD-II dataset is missing columns: {missing_columns}"
        )

    if data.empty:
        raise ValueError("OBD-II dataset is empty.")

    return data


def get_sensor_data(engine_data):

    sensor_columns = [
        "Engine rpm",
        "Lub oil pressure",
        "Fuel pressure",
        "Coolant pressure",
        "lub oil temp",
        "Coolant temp"
    ]

    return engine_data[sensor_columns].copy()
