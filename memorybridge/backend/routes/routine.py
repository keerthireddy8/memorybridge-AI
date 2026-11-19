from fastapi import APIRouter
from backend.models import RoutineDeviationResponse
from backend.services.routine_engine import get_baseline_routine, get_today_activity_sequence, analyze_routine_deviation

router = APIRouter(prefix="/api/routine", tags=["routine"])

@router.get("/baseline")
def read_baseline(user_id: str = "user_01"):
    return get_baseline_routine(user_id=user_id)

@router.get("/today")
def read_today_sequence(user_id: str = "user_01"):
    return get_today_activity_sequence(user_id=user_id)

@router.get("/deviation", response_model=RoutineDeviationResponse)
def read_deviation_status(user_id: str = "user_01"):
    return analyze_routine_deviation(user_id=user_id)
