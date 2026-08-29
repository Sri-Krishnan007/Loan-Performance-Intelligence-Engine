from fastapi import APIRouter
from backend.app.schemas.scenario import ScenarioRequest, ScenarioResponse
from backend.app.services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.post("/run", response_model=ScenarioResponse)
def run_scenario(payload: ScenarioRequest):
    """Runs a macroeconomic stress scenario simulation and aggregates results."""
    res = ScenarioService.run_scenario_simulation(
        scenario=payload.scenario,
        segments=payload.segments
    )
    return ScenarioResponse(
        scenario=res["scenario"],
        portfolio=res["portfolio"],
        segments=res["segments"],
        drivers=res["drivers"]
    )
