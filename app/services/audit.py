import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_audit(
    *,
    db: Session,
    actor: str,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    before: dict | None,
    after: dict | None,
):
    audit = AuditLog(
        id=uuid.uuid4(),
        actor=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before=before,
        after=after,
    )
    db.add(audit)
