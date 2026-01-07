import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base

class FeatureOverride(Base):
    __tablename__ = "feature_overrides"
    __table_args__ = (
        UniqueConstraint("feature_id", "environment", name="uq_feature_env"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(
        UUID(as_uuid=True),
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )
    environment = Column(String, nullable=False)  # dev / staging / prod
    enabled = Column(Boolean, nullable=False)
