from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, JSON, ARRAY, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class JobsOffered(Base):
    __tablename__ = "jobs_offered"
    jobid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session_id_table.session_id"))
    job_title = Column(String, index=True)
    cmp_name = Column(String, index=True)
    city = Column(String, index=True)
    state = Column(String, index=True)
    country = Column(String, index=True)
    description = Column(Text, nullable=True)
    qualification_required = Column(Text, nullable=True)
    skills_required = Column(ARRAY(String), nullable=True)
    salary_offered = Column(String, nullable=True)
    posted_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    session = relationship("SessionIdTable", back_populates="jobs")
    matches = relationship("MatchedJobs", back_populates="job")

class MatchedJobs(Base):
    __tablename__ = "matched_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs_offered.jobid"))
    match_score = Column(Float)
    matched_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    matched_on = Column(JSON, nullable=False)
    match_details = Column(JSON)
    user = relationship("UserDetails", back_populates="matched_jobs")
    job = relationship("JobsOffered", back_populates="matches") 