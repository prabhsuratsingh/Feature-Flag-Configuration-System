import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_db
from app.core.admin_security import require_admin
from app.models.feature import Feature
from app.models.feature_override import FeatureOverride
from app.services.cache_invalidator import invalidate_flag_cache
from app.services.audit import log_audit
from app.services.snapshot import model_to_dict


router = APIRouter(prefix="/admin/features", tags=["admin-features"])

@router.post("")
def create_feature(
    key: str,
    description: str | None = None,
    default_enabled: bool = False,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    feature = Feature(
        id=uuid.uuid4(),
        key=key,
        description=description,
        default_enabled=default_enabled,
    )

    db.add(feature)
    db.commit()
    db.refresh(feature)

    return feature

@router.patch("/{feature_id}")
def update_feature(
    feature_id: uuid.UUID,
    default_enabled: bool,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    feature = db.get(Feature, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    before = model_to_dict(feature)

    feature.default_enabled = default_enabled

    after = model_to_dict(feature)

    log_audit(
        db=db,
        actor=admin["sub"],
        entity_type="feature",
        entity_id=feature.id,
        action="update",
        before=before,
        after=after,
    )

    db.commit()

    for env in ["dev", "staging", "prod"]:
        invalidate_flag_cache(env)

    return feature


@router.put("/{feature_id}/override")
def upsert_override(
    feature_id: uuid.UUID,
    environment: str,
    enabled: bool,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    override = (
        db.query(FeatureOverride)
        .filter(
            FeatureOverride.feature_id == feature_id,
            FeatureOverride.environment == environment,
        )
        .first()
    )

    before = model_to_dict(override) if override else None

    if override:
        override.enabled = enabled
        action = "update"
    else:
        override = FeatureOverride(
            id=uuid.uuid4(),
            feature_id=feature_id,
            environment=environment,
            enabled=enabled,
        )
        db.add(override)
        action = "create"

    db.flush()  # ensures ID exists
    after = model_to_dict(override)

    log_audit(
        db=db,
        actor=admin["sub"],
        entity_type="feature_override",
        entity_id=override.id,
        action=action,
        before=before,
        after=after,
    )

    db.commit()
    invalidate_flag_cache(environment)

    return after


@router.delete("/{feature_id}")
def delete_feature(
    feature_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    feature = db.get(Feature, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    db.delete(feature)
    db.commit()

    for env in ["dev", "staging", "prod"]:
        invalidate_flag_cache(env)

    return {"status": "deleted"}
