from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, Enum, LargeBinary, JSON, ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class UserDetails(Base):
    __tablename__ = "user_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # Required field
    contact_no = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)  # Required field
    current_job_title = Column(String, nullable=True)
    years_of_exp = Column(Float, nullable=True)
    skills = Column(JSON, nullable=True)
    resume_location = Column(String, nullable=False)  # Required field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    parsed_date = Column(DateTime(timezone=True), nullable=True)  # Will be updated during analysis

    # Relationships
    academics = relationship("Academics", back_populates="user")
    accolades = relationship("Accolades", back_populates="user")
    work_experience = relationship("WorkExperience", back_populates="user")
    sessions = relationship("SessionIdTable", back_populates="user")
    matched_jobs = relationship("MatchedJobs", back_populates="user")

class Accolades(Base):
    __tablename__ = "accolades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    acco_url = Column(String)
    acco_start_year = Column(Integer)
    acco_end_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserDetails", back_populates="accolades")

class Academics(Base):
    __tablename__ = "academics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    school_name = Column(String)
    degree = Column(String)  # New column for degree
    school_year = Column(Integer)
    school_gpa = Column(Float)
    school_type = Column(Enum('under_grad', 'post_grad', 'phd', name='school_type_enum'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserDetails", back_populates="academics")

class SessionIdTable(Base):
    __tablename__ = "session_id_table"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("UserDetails", back_populates="sessions")
    jobs = relationship("JobsOffered", back_populates="session")

class JobsOffered(Base):
    __tablename__ = "jobs_offered"

    jobid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session_id_table.session_id"))
    job_title = Column(String, index=True)
    cmp_name = Column(String, index=True)
    
    # Location details as separate columns
    city = Column(String, index=True)
    state = Column(String, index=True)
    country = Column(String, index=True)
    
    description = Column(Text)
    qualification_required = Column(Text)
    skills_required = Column(ARRAY(String), nullable=False)
    salary_offered = Column(String)
    posted_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    session = relationship("SessionIdTable", back_populates="jobs")
    matches = relationship("MatchedJobs", back_populates="job")

class MatchedJobs(Base):
    __tablename__ = "matched_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs_offered.jobid"))
    match_score = Column(Float)
    matched_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # e.g., "applied", "interviewed", "rejected", "accepted"
    
    # New columns for match criteria
    matched_on = Column(JSON, nullable=False)  # Will store: {"skills": true, "title": true, "qualification": true, etc.}
    match_details = Column(JSON)  # Will store detailed match information like matching skills, etc.
    
    # Relationships
    user = relationship("UserDetails", back_populates="matched_jobs")
    job = relationship("JobsOffered", back_populates="matches")

class WorkExperience(Base):
    __tablename__ = "work_experience"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    company = Column(String)
    position = Column(String)
    joining_year = Column(Integer)
    end_year = Column(Integer, nullable=True)  # Nullable for current positions
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("UserDetails", back_populates="work_experience") 