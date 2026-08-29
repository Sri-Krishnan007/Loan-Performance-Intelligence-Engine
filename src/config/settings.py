import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data/synthetic"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Dataset Paths
STATIC_ATTRIBUTES_PATH = DATA_DIR / "loan_static_attributes.csv"
TRAIN_PERFORMANCE_PATH = DATA_DIR / "loan_monthly_performance_train.csv"
TEST_PERFORMANCE_PATH = DATA_DIR / "loan_monthly_performance_test.csv"
SERVICER_UPDATES_PATH = DATA_DIR / "servicer_updates.csv"
MACRO_SCENARIOS_PATH = DATA_DIR / "macro_scenarios.csv"
VALIDATION_RULES_PATH = DATA_DIR / "validation_rules.json"
SUBMISSION_TEMPLATE_PATH = DATA_DIR / "submission_template.csv"

# Output Paths
PROFILING_OUTPUT_DIR = OUTPUT_DIR / "profiling"
MODEL_OUTPUT_DIR = OUTPUT_DIR / "models"
ANOMALY_OUTPUT_DIR = OUTPUT_DIR / "anomaly"
EXPLAIN_OUTPUT_DIR = OUTPUT_DIR / "explainability"
SCENARIO_OUTPUT_DIR = OUTPUT_DIR / "scenarios"
LLM_OUTPUT_DIR = OUTPUT_DIR / "llm"

# Ensure Output Directories Exist
for directory in [
    PROFILING_OUTPUT_DIR,
    MODEL_OUTPUT_DIR,
    ANOMALY_OUTPUT_DIR,
    EXPLAIN_OUTPUT_DIR,
    SCENARIO_OUTPUT_DIR,
    LLM_OUTPUT_DIR,
    MODEL_DIR / "trained",
    MODEL_DIR / "metrics",
    MODEL_DIR / "metadata",
    REPORTS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)

# Quality Scoring Config Defaults (Overridden by validation_rules.json if loaded)
SCORING_CONFIG = {
    "record_score_initial": 100,
    "error_penalty": 20,
    "warning_penalty": 5,
    "info_penalty": 0,
    "minimum_score": 0
}

# Load .env file manually if it exists
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if "=" in line_str and not line_str.startswith("#"):
                k, v = line_str.split("=", 1)
                os.environ[k.strip()] = v.strip()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_DEFAULT_MODEL = "qwen/qwen3.8-27b"
