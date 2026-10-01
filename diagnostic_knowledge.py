# ==========================================================
# DIAGNOSTIC KNOWLEDGE BASE
# ==========================================================
#
# This module contains structured diagnostic knowledge used
# by the diagnostic agent.
#
# Important:
# - Symptoms are reported observations.
# - Possible causes are hypotheses, not confirmed failures.
# - Recommended evidence tells the agent what information
#   would help continue an investigation.
# ==========================================================


SYMPTOM_KNOWLEDGE = {

    # ------------------------------------------------------
    # OVERHEATING
    # ------------------------------------------------------

    "overheating": {

        "display_name": "Engine Overheating",

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


    # ------------------------------------------------------
    # WHITE SMOKE / VAPOR
    # ------------------------------------------------------

    "white smoke": {

        "display_name": "White Smoke or Vapor",

        "system": "general",

        "requires_context": True,

        "question":
            "Where is the white smoke or vapor coming from?",

        "options": [
            "Exhaust",
            "Engine bay",
            "Unknown"
        ],

        "possible_causes": [
            "Coolant entering the combustion process",
            "External coolant leak",
            "Coolant contacting hot engine components",
            "Normal condensation under some operating conditions"
        ],

        "recommended_evidence": [
            "Smoke or vapor location",
            "Coolant level",
            "Coolant loss history",
            "Engine temperature",
            "Engine oil condition",
            "OBD-II trouble codes"
        ]
    },


    # ------------------------------------------------------
    # ENGINE SHAKING / VIBRATION
    # ------------------------------------------------------

    "engine shaking": {

        "display_name":
            "Engine Shaking / Abnormal Vibration",

        "system": "general",

        "requires_context": True,

        "question":
            "When is the engine shaking most noticeable?",

        "options": [
            "At idle",
            "During acceleration",
            "At higher engine speed",
            "Throughout operation",
            "Unknown"
        ],

        "related_measurements": [
            "rpm"
        ],

        "possible_causes": [
            "Engine misfire",
            "Unstable combustion",
            "Fuel delivery problem",
            "Air intake or vacuum problem",
            "Mechanical engine imbalance",
            "Engine or transmission mounting problem"
        ],

        "recommended_evidence": [
            "Operating condition when shaking occurs",
            "Engine RPM and RPM stability",
            "Check-engine light status",
            "OBD-II trouble codes",
            "Misfire-related trouble codes",
            "Ignition system condition",
            "Fuel delivery condition",
            "Air intake and vacuum condition",
            "Engine mounting condition"
        ]
    },


    # ------------------------------------------------------
    # ROUGH IDLE
    # ------------------------------------------------------

    "rough idle": {

        "display_name": "Rough or Unstable Idle",

        "system": "general",

        "related_measurements": [
            "rpm"
        ],

        "possible_causes": [
            "Engine misfire",
            "Air intake or vacuum leak",
            "Fuel delivery problem",
            "Ignition system problem",
            "Idle control problem",
            "Mechanical engine condition"
        ],

        "recommended_evidence": [
            "Idle RPM",
            "RPM stability",
            "OBD-II trouble codes",
            "Misfire-related trouble codes",
            "Air intake and vacuum condition",
            "Fuel delivery condition",
            "Ignition system condition"
        ]
    },


    # ------------------------------------------------------
    # POWER LOSS / POOR ACCELERATION
    # ------------------------------------------------------

    "power loss": {

        "display_name":
            "Loss of Power / Poor Acceleration",

        "system": "general",

        "related_measurements": [
            "rpm",
            "fuel_pressure"
        ],

        "possible_causes": [
            "Fuel delivery problem",
            "Air intake restriction",
            "Ignition or combustion problem",
            "Engine mechanical condition",
            "Exhaust restriction"
        ],

        "recommended_evidence": [
            "Fuel pressure",
            "Engine RPM response",
            "OBD-II trouble codes",
            "Air intake condition",
            "Ignition system condition",
            "Engine mechanical condition"
        ]
    },


    # ------------------------------------------------------
    # STALLING
    # ------------------------------------------------------

    "stalling": {

        "display_name": "Engine Stalling",

        "system": "general",

        "related_measurements": [
            "rpm",
            "fuel_pressure"
        ],

        "possible_causes": [
            "Fuel delivery interruption",
            "Air intake or idle-control problem",
            "Ignition or combustion problem",
            "Engine speed control problem"
        ],

        "recommended_evidence": [
            "Condition when the engine stalls",
            "Engine RPM before stalling",
            "Fuel pressure",
            "OBD-II trouble codes",
            "Check-engine light status"
        ]
    },


    # ------------------------------------------------------
    # HARD START / NO START
    # ------------------------------------------------------

    "starting difficulty": {

        "display_name":
            "Starting Difficulty",

        "system": "general",

        "possible_causes": [
            "Fuel delivery problem",
            "Ignition problem",
            "Starting or electrical system problem",
            "Air intake problem",
            "Mechanical engine condition"
        ],

        "recommended_evidence": [
            "Whether the engine cranks",
            "Fuel pressure",
            "Battery and starting-system condition",
            "OBD-II trouble codes",
            "Ignition system condition"
        ]
    },


    # ------------------------------------------------------
    # LOW OIL PRESSURE
    # ------------------------------------------------------

    "low oil pressure": {

        "display_name":
            "Low Lubrication Oil Pressure",

        "system": "lubrication",

        "related_measurements": [
            "oil_pressure",
            "oil_temperature",
            "rpm"
        ],

        "possible_causes": [
            "Low engine oil level",
            "Oil leakage",
            "Oil pump or circulation problem",
            "Oil pressure regulation problem",
            "Excessive internal engine clearance",
            "Oil pressure sensor or measurement problem"
        ],

        "recommended_evidence": [
            "Engine oil level",
            "Oil pressure",
            "Oil temperature",
            "Engine RPM",
            "Oil condition",
            "Visible oil leakage",
            "OBD-II trouble codes"
        ]
    },


    # ------------------------------------------------------
    # BLUE EXHAUST SMOKE
    # ------------------------------------------------------

    "blue smoke": {

        "display_name":
            "Blue Exhaust Smoke",

        "system": "lubrication",

        "possible_causes": [
            "Engine oil entering the combustion process",
            "Valve sealing problem",
            "Piston or cylinder sealing problem",
            "Crankcase ventilation problem"
        ],

        "recommended_evidence": [
            "Engine oil consumption",
            "Engine oil level",
            "Compression test",
            "Cylinder leak-down test",
            "Crankcase ventilation condition",
            "OBD-II trouble codes"
        ]
    },


    # ------------------------------------------------------
    # BLACK EXHAUST SMOKE
    # ------------------------------------------------------

    "black smoke": {

        "display_name":
            "Black Exhaust Smoke",

        "system": "fuel",

        "related_measurements": [
            "fuel_pressure",
            "rpm"
        ],

        "possible_causes": [
            "Excessive fuel delivery",
            "Air intake restriction",
            "Fuel control problem",
            "Combustion problem"
        ],

        "recommended_evidence": [
            "Fuel pressure",
            "Air intake condition",
            "Engine RPM",
            "OBD-II trouble codes",
            "Fuel system condition"
        ]
    }
}


# ==========================================================
# MULTI-SYMPTOM KNOWLEDGE
# ==========================================================

SYMPTOM_COMBINATIONS = {

    (
        "overheating",
        "white smoke",
        "exhaust"
    ): {

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


    (
        "overheating",
        "white smoke",
        "engine bay"
    ): {

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


# ==========================================================
# SYMPTOM PHRASES
# ==========================================================
#
# These allow normal user language to map to structured
# symptoms without requiring generative AI.
# ==========================================================

SYMPTOM_PHRASES = {

    "overheating": [
        "overheat",
        "overheating",
        "running hot",
        "runs hot",
        "getting too hot",
        "engine is hot",
        "temperature is high"
    ],

    "white smoke": [
        "white smoke",
        "white vapor",
        "white steam"
    ],

    "engine shaking": [
        "engine shaking",
        "engine is shaking",
        "engine shakes",
        "car is shaking",
        "car shakes",
        "engine vibration",
        "engine vibrating",
        "engine is vibrating",
        "vibrating"
    ],

    "rough idle": [
        "rough idle",
        "idles rough",
        "rough at idle",
        "unstable idle",
        "idle is rough"
    ],

    "power loss": [
        "loss of power",
        "losing power",
        "no power",
        "low power",
        "poor acceleration",
        "slow acceleration",
        "sluggish",
        "hesitation",
        "hesitates"
    ],

    "stalling": [
        "stalling",
        "engine stalls",
        "engine is stalling",
        "keeps stalling",
        "dies at idle",
        "engine dies"
    ],

    "starting difficulty": [
        "hard to start",
        "hard starting",
        "won't start",
        "will not start",
        "doesn't start",
        "does not start",
        "long crank",
        "cranks for a long time"
    ],

    "low oil pressure": [
        "low oil pressure",
        "oil pressure low",
        "oil pressure warning"
    ],

    "blue smoke": [
        "blue smoke",
        "blue exhaust smoke"
    ],

    "black smoke": [
        "black smoke",
        "black exhaust smoke"
    ]
}


# ==========================================================
# SYMPTOM DETECTION
# ==========================================================

def detect_symptoms(text):

    if not text:
        return []

    text = text.lower().strip()

    detected = []

    for symptom, phrases in SYMPTOM_PHRASES.items():

        for phrase in phrases:

            if phrase in text:

                detected.append(symptom)

                break

    return detected


# ==========================================================
# PRIMARY SYSTEM SELECTION
# ==========================================================

def determine_primary_system(symptoms):

    if "overheating" in symptoms:
        return "cooling_condition"

    if "low oil pressure" in symptoms:
        return "lubrication_condition"

    if "blue smoke" in symptoms:
        return "lubrication_condition"

    if "black smoke" in symptoms:
        return "fuel_condition"

    if "power loss" in symptoms:
        return "general_engine_condition"

    if "engine shaking" in symptoms:
        return "general_engine_condition"

    if "rough idle" in symptoms:
        return "general_engine_condition"

    if "stalling" in symptoms:
        return "general_engine_condition"

    if "starting difficulty" in symptoms:
        return "general_engine_condition"

    return "general_engine_condition"


# ==========================================================
# CONTEXT REQUIREMENTS
# ==========================================================

def get_context_question(symptoms):

    # White smoke location currently receives priority
    # because location significantly changes its meaning.

    if "white smoke" in symptoms:

        knowledge = SYMPTOM_KNOWLEDGE[
            "white smoke"
        ]

        return {
            "symptom": "white smoke",
            "question": knowledge["question"],
            "options": knowledge["options"]
        }


    if "engine shaking" in symptoms:

        knowledge = SYMPTOM_KNOWLEDGE[
            "engine shaking"
        ]

        return {
            "symptom": "engine shaking",
            "question": knowledge["question"],
            "options": knowledge["options"]
        }


    return None


def needs_smoke_location(symptoms):

    # Retained for compatibility with the current app.

    return "white smoke" in symptoms


# ==========================================================
# INDIVIDUAL SYMPTOM KNOWLEDGE
# ==========================================================

def get_symptom_knowledge(symptom):

    return SYMPTOM_KNOWLEDGE.get(
        symptom
    )


def get_detected_knowledge(symptoms):

    results = {}

    for symptom in symptoms:

        knowledge = get_symptom_knowledge(
            symptom
        )

        if knowledge:

            results[symptom] = knowledge

    return results


# ==========================================================
# COMBINED ASSESSMENT
# ==========================================================

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

        location = (
            smoke_location
            .lower()
            .strip()
        )

        key = (
            "overheating",
            "white smoke",
            location
        )

        return SYMPTOM_COMBINATIONS.get(
            key
        )

    return None


# ==========================================================
# EVIDENCE REQUIREMENTS
# ==========================================================

def get_recommended_evidence(symptoms):

    evidence = []

    for symptom in symptoms:

        knowledge = SYMPTOM_KNOWLEDGE.get(
            symptom,
            {}
        )

        for item in knowledge.get(
            "recommended_evidence",
            []
        ):

            if item not in evidence:
                evidence.append(item)

    return evidence


def get_candidate_hypotheses(symptoms):

    hypotheses = []

    for symptom in symptoms:

        knowledge = SYMPTOM_KNOWLEDGE.get(
            symptom,
            {}
        )

        for item in knowledge.get(
            "possible_causes",
            []
        ):

            if item not in hypotheses:
                hypotheses.append(item)

    return hypotheses


# ==========================================================
# DETERMINE WHETHER MORE CONTEXT IS NEEDED
# ==========================================================

def needs_additional_context(
    symptoms,
    context=None
):

    context = context or {}

    missing = []

    for symptom in symptoms:

        knowledge = SYMPTOM_KNOWLEDGE.get(
            symptom,
            {}
        )

        if knowledge.get(
            "requires_context",
            False
        ):

            if symptom not in context:

                missing.append(
                    symptom
                )

    return missing
