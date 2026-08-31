import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import api_settings
from backend.app.services.loan_service import loan_state
from backend.app.routers import (
    health, overview, loans, predictions, anomalies, 
    explanations, scenarios, reviewer, model_health, data_quality
)
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Loan Performance Intelligence Engine API",
    description="REST API layer over the credit-risk, transition-survival, and anomaly engine.",
    version="1.0.0"
)

# CORS Configuration
origins = [origin.strip() for origin in api_settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

if "*" in origins or api_settings.ALLOWED_ORIGINS == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
def startup_event():
    logger.info("Starting FastAPI backend server...")
    try:
        loan_state.initialize()
    except Exception as e:
        logger.error(f"Error during startup loan state initialization: {e}")

# Register Routers
app.include_router(health.router, prefix="/api")
app.include_router(overview.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(anomalies.router, prefix="/api")
app.include_router(explanations.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
app.include_router(reviewer.router, prefix="/api")
app.include_router(model_health.router, prefix="/api")
app.include_router(data_quality.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Loan Performance Intelligence Engine API. Visit /docs for self-documenting OpenAPI endpoints."
    }
