from pydantic import BaseModel
from typing import List, Dict

# Input Schema: Matches the 7 sensors and farmer choices
class SensorInput(BaseModel):
    N: float
    P: float
    K: float
    Soil_pH: float
    Temp: float
    Humidity: float
    Moisture: float
    Rainfall: float
    planned_actions: List[str]

# Output Sub-Schemas
class TruthTableFlag(BaseModel):
    rule: str
    status: str

class ShapDriver(BaseModel):
    feature: str
    impact: float

# Main Output Schema
class DiagnosisOutput(BaseModel):
    prediction: str
    probabilities: Dict[str, float]
    markdown_metrics: str
    truth_table_flags: List[TruthTableFlag]
    shap_drivers: List[ShapDriver]