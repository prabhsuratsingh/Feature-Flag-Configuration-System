import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_db
from app.core.admin_security import require_admin
from app.models.configuration import Configuration
from app.services.cache_invalidator import invalidate_config_cache
from app.services.audit import log_audit
from app.services.snapshot import model_to_dict


router = APIRouter(prefix="/admin/configs", tags=["admin-configs"])

@router.put("")
def upsert_config(
    key: str,
    environment: str,
    value: dict | str | int | bool,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    config = (
        db.query(Configuration)
        .filter(
            Configuration.key == key,
            Configuration.environment == environment,
        )
        .first()
    )

    before = model_to_dict(config) if config else None

    if config:
        config.value = value
        action = "update"
    else:
        config = Configuration(
            id=uuid.uuid4(),
            key=key,
            environment=environment,
            value=value,
        )
        db.add(config)
        action = "create"

    db.flush()
    after = model_to_dict(config)

    log_audit(
        db=db,
        actor=admin["sub"],
        entity_type="configuration",
        entity_id=config.id,
        action=action,
        before=before,
        after=after,
    )

    db.commit()
    invalidate_config_cache(environment)

    return after


@router.delete("")
def delete_config(
    key: str,
    environment: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    config = (
        db.query(Configuration)
        .filter(
            Configuration.key == key,
            Configuration.environment == environment,
        )
        .first()
    )

    before = model_to_dict(config)

    if not config:
        return {"status": "not_found"}

    log_audit(
        db=db,
        actor=admin["sub"],
        entity_type="feature",
        entity_id=config.id,
        action="delete",
        before=before,
        after=None,
    )

    db.delete(config)
    db.commit()
    invalidate_config_cache(environment)

    return {"status": "deleted"}
