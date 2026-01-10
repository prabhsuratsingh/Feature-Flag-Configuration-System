from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import get_db
from app.core.admin_security import require_admin
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogOut

router = APIRouter(
    prefix="/admin/audit-logs",
    tags=["admin-audit"],
)

@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    entity_type: str | None = Query(None),
    entity_id: str | None = Query(None),
    actor: str | None = Query(None),
    action: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    query = db.query(AuditLog)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)

    if actor:
        query = query.filter(AuditLog.actor == actor)

    if action:
        query = query.filter(AuditLog.action == action)

    logs = (
        query
        .order_by(desc(AuditLog.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return logs
