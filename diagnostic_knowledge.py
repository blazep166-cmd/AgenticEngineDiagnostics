SYMPTOM_KNOWLEDGE = {

    "overheating": {
        "system": "cooling",
        "related_measurements": [
            "coolant_temperature",
            "coolant_pressure",
            "rpm"
        ],
        "possible_causes": [
            "Low coolant level or coolant loss",
            "Cooling system leak",
            "Thermostat malfunction",
            "Cooling fan malfunction",
            "Restricted coolant circulation",
            "Water pump or coolant circulation problem",
            "Combustion gas entering the cooling system"
        ],
        "recommended_evidence": [
            "Coolant level",
            "Coolant temperature",
            "Coolant pressure",
            "Cooling fan operation",
            "Visible coolant leakage",
            "OBD-II trouble codes"
        ]
    },

    "white smoke": {
        "requires_context": True,
        "question": (
            "Where is the white smoke coming from?"
        ),
        "options": [
            "Exhaust",
            "Engine bay",
            "Unknown"
        ]
    }
}


SYMPTOM_COMBINATIONS = {

    ("overheating", "white smoke", "exhaust"): {
        "hypotheses": [
            "Coolant entering the combustion process",
            "Cylinder-head gasket sealing problem",
            "Cylinder-head or engine-block sealing problem"
        ],
        "recommended_evidence": [
            "Coolant level or repeated coolant loss",
            "Cooling-system pressure test",
            "Engine oil condition",
            "Compression test",
            "Cylinder leak-down test",
            "Combustion-gas test of the cooling system",
            "Relevant OBD-II trouble codes"
        ],
        "interpretation": (
            "Overheating combined with persistent white "
            "exhaust smoke can be consistent with coolant "
            "entering the combustion process. The symptoms "
            "alone do not establish the underlying cause."
        )
    },

    ("overheating", "white smoke", "engine bay"): {
        "hypotheses": [
            "External coolant leak contacting hot components",
            "Coolant overflow or venting",
            "Cooling-system hose or connection leak",
            "Radiator or reservoir leakage"
        ],
        "recommended_evidence": [
            "Visible coolant leakage",
            "Coolant level",
            "Cooling-system pressure test",
            "Radiator and hose inspection",
            "Coolant reservoir inspection"
        ],
        "interpretation": (
            "Overheating combined with white vapor or smoke "
            "from the engine bay can be consistent with an "
            "external coolant leak or coolant contacting hot "
            "engine components."
        )
    }
}


def detect_symptoms(text):

    text = text.lower()

    detected = []

    if (
        "overheat" in text
        or "overheating" in text
        or "running hot" in text
    ):
        detected.append("overheating")

    if (
        "white smoke" in text
        or "white vapor" in text
        or "white steam" in text
    ):
        detected.append("white smoke")

    return detected


def determine_primary_system(symptoms):

    if "overheating" in symptoms:
        return "cooling_condition"

    return "general_engine_condition"


def needs_smoke_location(symptoms):

    return (
        "white smoke" in symptoms
    )


def get_combined_assessment(
    symptoms,
    smoke_location=None
):

    if (
        "overheating" in symptoms
        and
        "white smoke" in symptoms
        and
        smoke_location
    ):

        location = smoke_location.lower()

        key = (
            "overheating",
            "white smoke",
            location
        )

        return SYMPTOM_COMBINATIONS.get(
            key
        )

    return None
