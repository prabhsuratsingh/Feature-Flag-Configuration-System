from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FeatureData(Base):
    __tablename__ = "featuredata"