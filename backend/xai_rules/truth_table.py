from typing import Any, Dict, List
import itertools


def _number(data: Dict[str, Any], key: str) -> float:
    """Return a numeric input, or raise ValueError if missing/invalid."""
    value = data.get(key)
    if value is None or isinstance(value, bool):
        raise ValueError(f"Missing or invalid numeric value: {key}")
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Missing or invalid numeric value: {key}")


def _flag(data: Dict[str, Any], key: str) -> bool:
    """Return a Boolean input, or raise ValueError if missing/invalid."""
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"Missing or invalid Boolean value: {key}")
    return value


def _evaluate_one(rule_name: str, data: Dict[str, Any],
    thresholds: Dict[str, Any]) -> bool:
    """Evaluate one named rule. Missing inputs produce UNKNOWN upstream."""

    if rule_name == "R1":
        return (
            _number(data, "N") < _number(thresholds, "N_CRITICAL")
            and _flag(data, "N_REQUIREMENT_CONFIRMED")
        )

    if rule_name == "R2":
        return (
            _number(data, "P") < _number(thresholds, "P_CRITICAL")
            and _flag(data, "P_REQUIREMENT_CONFIRMED")
        )

    if rule_name == "R3":
        return (
            _number(data, "K") < _number(thresholds, "K_CRITICAL")
            and _flag(data, "K_REQUIREMENT_CONFIRMED")
        )

    if rule_name == "R4":
        return (
            _number(data, "water_depletion")
            >= _number(thresholds, "RAW_THRESHOLD")
            and _flag(data, "IRRIGATION_REQUIRED")
        )

    if rule_name == "R5":
        return (
            _number(data, "Moisture")
            >= _number(thresholds, "M_WATERLOGGING")
            and _flag(data, "WATERLOGGING_RISK")
        )

    if rule_name == "R6":
        return (
            _number(data, "Soil_pH")
            < _number(thresholds, "PH_MIN_CROP")
            and _flag(data, "ACIDITY_CONFIRMED")
        )

    if rule_name == "R7":
        return (
            _number(data, "Soil_pH")
            > _number(thresholds, "PH_MAX_CROP")
            and _flag(data, "ALKALINITY_CONFIRMED")
        )

    if rule_name == "R8":
        return (
            _number(data, "Temp") > _number(thresholds, "T_MAX_CROP")
            and _number(data, "Moisture")
            < _number(thresholds, "M_STRESS_CROP")
        )

    if rule_name == "R9":
        temperature = _number(data, "Temp")
        return (
            _number(data, "Humidity")
            > _number(thresholds, "H_DISEASE_THRESHOLD")
            and _number(thresholds, "T_MIN_PATHOGEN")
            <= temperature
            <= _number(thresholds, "T_MAX_PATHOGEN")
        )

    if rule_name == "R10":
        return (
            _flag(data, "DISEASE_CONFIRMED")
            and _flag(data, "REGISTERED_TREATMENT_AVAILABLE")
        )

    raise KeyError(f"Unknown rule: {rule_name}")


RULE_MESSAGES = {
    "R1": "Possible nitrogen shortage: review soil/plant test and crop-stage need.",
    "R2": "Possible phosphorus shortage: review soil test and crop-stage need.",
    "R3": "Possible potassium shortage: review soil test and crop-stage need.",
    "R4": "Irrigation condition met: check field conditions before irrigating.",
    "R5": "Possible waterlogging: inspect drainage and avoid extra irrigation pending checks.",
    "R6": "Soil acidity condition met: confirm pH and obtain a local lime recommendation.",
    "R7": "Soil alkalinity condition met: confirm soil condition and seek local advice.",
    "R8": "Possible combined heat and water stress: inspect crop and water availability.",
    "R9": "Weather-based disease-risk condition met: scout the crop; this is not disease confirmation.",
    "R10": "Disease and treatment-availability flags are confirmed: review registered options, label and IPM guidance.",
}
def test_generate_truth_table_dimensions_and_active_state(self):
        from truth_table import generate_truth_table
        table = generate_truth_table(self.data, self.thresholds)
        # 9 boolean confirmation flags = 2^9 = 512 rows
        self.assertEqual(len(table), 512)
        
        # Verify exactly one row is flagged as the current active state
        active_rows = [r for r in table if r["is_current_state"] is True]
        self.assertEqual(len(active_rows), 1)

def evaluate_rules(sensor_data: Dict[str, Any],
                   thresholds: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Evaluate R1-R10.

    sensor_data:
        Dictionary of sensor readings and Boolean confirmation flags.
    thresholds:
        Numeric thresholds for the selected crop and growth stage.
    """
    results = []

    for rule_name in [f"R{i}" for i in range(1, 11)]:
        try:
            is_true = _evaluate_one(rule_name, sensor_data, thresholds)
            status = "TRUE" if is_true else "FALSE"
            message = RULE_MESSAGES[rule_name] if is_true else "Rule condition not met."
        except (ValueError, KeyError):
            status = "UNKNOWN"
            message = "Required input or threshold is missing/invalid."

        results.append({
            "rule": rule_name,
            "status": status,
            "message": message,
        })

    return results


def generate_truth_table(sensor_data: Dict[str, Any],
                         thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates a full 2^n truth-table array across all independent Boolean 
    confirmation flags, showing all possible state combinations alongside 
    an indicator flag designating the current active state.
    """
    flag_keys = [
        "N_REQUIREMENT_CONFIRMED", "P_REQUIREMENT_CONFIRMED", "K_REQUIREMENT_CONFIRMED",
        "IRRIGATION_REQUIRED", "WATERLOGGING_RISK", "ACIDITY_CONFIRMED",
        "ALKALINITY_CONFIRMED", "DISEASE_CONFIRMED", "REGISTERED_TREATMENT_AVAILABLE"
    ]
    
    current_flags = [bool(sensor_data.get(k, False)) for k in flag_keys]
    truth_table_array = []
    
    # Generate 2^n combinations for the boolean flag space
    for combo in itertools.product([False, True], repeat=len(flag_keys)):
        test_data = dict(sensor_data)
        for k, val in zip(flag_keys, combo):
            test_data[k] = val
            
        evaluation = evaluate_rules(test_data, thresholds)
        is_active_state = (list(combo) == current_flags)
        
        row = {
            "combination": {k: v for k, v in zip(flag_keys, combo)},
            "is_current_state": is_active_state,
        }
        for res in evaluation:
            row[res["rule"]] = res["status"]
            
        truth_table_array.append(row)
        
    return truth_table_array


if __name__ == "__main__":
    example_sensor_data = {
        "N": 20, "P": 15, "K": 18,
        "Soil_pH": 5.0, "Temp": 36,
        "Humidity": 85, "Moisture": 15,
        "water_depletion": 0.60,
        "N_REQUIREMENT_CONFIRMED": True,
        "P_REQUIREMENT_CONFIRMED": True,
        "K_REQUIREMENT_CONFIRMED": True,
        "IRRIGATION_REQUIRED": True,
        "WATERLOGGING_RISK": False,
        "ACIDITY_CONFIRMED": True,
        "ALKALINITY_CONFIRMED": False,
        "DISEASE_CONFIRMED": True,
        "REGISTERED_TREATMENT_AVAILABLE": True,
    }

    example_thresholds = {
        "N_CRITICAL": 30, "P_CRITICAL": 20, "K_CRITICAL": 25,
        "RAW_THRESHOLD": 0.50, "M_WATERLOGGING": 80,
        "PH_MIN_CROP": 5.5, "PH_MAX_CROP": 7.0,
        "T_MAX_CROP": 34, "M_STRESS_CROP": 20,
        "H_DISEASE_THRESHOLD": 80,
        "T_MIN_PATHOGEN": 20, "T_MAX_PATHOGEN": 30,
    }

    print("--- Single Evaluation ---")
    for result in evaluate_rules(example_sensor_data, example_thresholds):
        print(f'{result["rule"]}: {result["status"]} - {result["message"]}')
        
    print(f"\n--- Generated 2^n Truth Table Matrix ---")
    table = generate_truth_table(example_sensor_data, example_thresholds)
    print(f"Total combinatorial states generated: {len(table)}")
    active_row = next(r for r in table if r["is_current_state"])
    print("Active state row found successfully.")