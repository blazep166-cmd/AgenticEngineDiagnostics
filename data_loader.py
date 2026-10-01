import pandas as pd


# ==========================================================
# ENGINE DATA
# ==========================================================

ENGINE_COLUMNS = [
    "Engine rpm",
    "Lub oil pressure",
    "Fuel pressure",
    "Coolant pressure",
    "lub oil temp",
    "Coolant temp",
    "Engine Condition"
]


def load_engine_data(file_path):

    data = pd.read_csv(
        file_path,
        sep=r"\s+",
        skiprows=1,
        names=ENGINE_COLUMNS
    )

    if data.empty:
        raise ValueError("Engine dataset is empty.")

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


# ==========================================================
# OBD-II DATA
# ==========================================================

def load_obd_data(file_path):

    records = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        # Skip header
        next(file, None)

        for line in file:

            line = line.strip()

            if not line:
                continue

            # Split into only three pieces:
            # code, system, and full description
            parts = line.split(maxsplit=2)

            if len(parts) < 3:
                continue

            code = parts[0]
            system = parts[1]
            description = parts[2]

            records.append(
                {
                    "Code": code,
                    "Trouble Code System": system,
                    "Condition Description": description
                }
            )

    data = pd.DataFrame(records)

    if data.empty:
        raise ValueError(
            "OBD-II dataset could not be loaded."
        )

    return data
