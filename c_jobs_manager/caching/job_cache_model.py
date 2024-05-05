from sqlalchemy import Column, Integer, String, DateTime, JSON, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JobCacheModel(Base):
    __tablename__ = 'job_caches'
    __table_args__ = (
        UniqueConstraint('job_id', 'name', name='_job_id_name_uc'),
        {'extend_existing': True},
    )

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    data = Column(JSON, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
