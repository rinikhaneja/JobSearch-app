from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Enum, JSON, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base
from sqlalchemy.sql import func


def map_degree_type(degree_type):
    if degree_type == "bachelor" or degree_type == "undergraduate" or degree_type == "bsc" or degree_type == "bachelors" or degree_type == "bachelors of science":
        return "under_grad"
    elif degree_type == "master" or degree_type == "graduate" or degree_type == "msc" or degree_type == "masters" or degree_type == "masters of science":
        return "grad"
    elif degree_type == "post_grad" or degree_type == "postgraduate" or degree_type == "postgraduate degree" or degree_type == "postgraduate degree in":
        return "post_grad"
    elif degree_type == "phd" or degree_type == "doctoral" or degree_type == "doctorate":
        return "phd"
    return None

class UserDetails(Base):
    """Represents a user and their details, including resume, contact info, and relationships to academics, accolades, work experience, sessions, and matched jobs."""
    __tablename__ = "user_details"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_no = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    current_job_title = Column(String, nullable=True)
    years_of_exp = Column(Float, nullable=True)
    skills = Column(JSON, nullable=True)
    resume_location = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    parsed_date = Column(DateTime(timezone=True), nullable=True)
    academics = relationship("Academics", back_populates="user")
    accolades = relationship("Accolades", back_populates="user")
    work_experience = relationship("WorkExperience", back_populates="user")
    sessions = relationship("SessionIdTable", back_populates="user")
    matched_jobs = relationship("MatchedJobs", back_populates="user")

class Accolades(Base):
    """Represents an accolade or certification associated with a user."""
    __tablename__ = "accolades"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    acco_url = Column(String)
    acco_start_year = Column(Integer)
    acco_end_year = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("UserDetails", back_populates="accolades")

class Academics(Base):
    """Represents an academic record for a user, including school, degree, and GPA."""
    __tablename__ = "academics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    school_name = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    school_year = Column(Integer, nullable=True)
    school_gpa = Column(Float, nullable=True)
    school_type = Column(Enum('under_grad', 'post_grad', 'phd', 'grad', name='school_type_enum'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("UserDetails", back_populates="academics")

class SessionIdTable(Base):
    """Represents a user session, including session token, validity, and relationship to jobs."""
    __tablename__ = "session_id_table"
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)
    user = relationship("UserDetails", back_populates="sessions")
    jobs = relationship("JobsOffered", back_populates="session")

class WorkExperience(Base):
    __tablename__ = "work_experience"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_details.id"))
    company = Column(String)
    position = Column(String)
    joining_year = Column(Integer)
    end_year = Column(Integer, nullable=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("UserDetails", back_populates="work_experience") 