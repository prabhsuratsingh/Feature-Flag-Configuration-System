from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_db, require_api_key
from app.services.config_evaluator import evaluate_configs

router = APIRouter(prefix="/v1/configs", tags=["configs"])


@router.get("")
def get_configs(
    environment: str = Query(..., example="prod"),
    db: Session = Depends(get_db),
    client=Depends(require_api_key),
):
    """
    Returns all runtime configs for a given environment.
    """
    return evaluate_configs(db=db, environment=environment)
