from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import SensorInput, DiagnosisOutput
from xai_rules.truth_table import evaluate_rules, generate_truth_table

app = FastAPI(title="Crop Pest Expert System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/diagnose", response_model=DiagnosisOutput)
async def get_diagnosis(sensor_data: SensorInput):
    # Convert incoming Pydantic model to dictionary
    data_dict = sensor_data.model_dump()
    
    # Define dynamic agronomic thresholds (or fetch based on crop type)
    thresholds = {
        "N_CRITICAL": 30, "P_CRITICAL": 20, "K_CRITICAL": 25,
        "RAW_THRESHOLD": 0.50, "M_WATERLOGGING": 80,
        "PH_MIN_CROP": 5.5, "PH_MAX_CROP": 7.0,
        "T_MAX_CROP": 34, "M_STRESS_CROP": 20,
        "H_DISEASE_THRESHOLD": 80,
        "T_MIN_PATHOGEN": 20, "T_MAX_PATHOGEN": 30,
    }
    
    # Evaluate rules dynamically
    rule_results = evaluate_rules(data_dict, thresholds)
    truth_table_matrix = generate_truth_table(data_dict, thresholds)
    
    # Map rule results to output schema format
    formatted_flags = [{"rule": r["rule"], "status": r["status"]} for r in rule_results]

    return {
        "prediction": "Evaluated via XAI Rules Engine",
        "probabilities": {"Healthy Crop": 0.75, "Fungal Blight Risk": 0.25},
        "markdown_metrics": f"### Diagnostic Report\nEvaluated {len(rule_results)} rules successfully against current sensor inputs.",
        "truth_table_flags": formatted_flags,
        "shap_drivers": [{"feature": "Moisture", "impact": 0.45}, {"feature": "N", "impact": -0.21}]
    }