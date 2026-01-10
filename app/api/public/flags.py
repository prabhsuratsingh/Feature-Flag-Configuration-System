from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_db, require_api_key
from app.services.flag_evaluator import evaluate_flags

router = APIRouter(prefix="/v1/flags", tags=["flags"])


@router.get("")
def get_flags(
    environment: str = Query(..., example="prod"),
    db: Session = Depends(get_db),
    client=Depends(require_api_key),
):
    """
    Returns all feature flags for a given environment.
    """
    return evaluate_flags(db=db, environment=environment)
