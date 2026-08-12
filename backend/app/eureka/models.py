from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class EurekaRegistration(Base):
    __tablename__ = "eureka_registrations"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(String, unique=True, index=True, nullable=False)
    
    # Startup Details
    startup_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    
    # Conditional fields
    is_existing = Column(Boolean, default=False)
    website = Column(String, nullable=True)
    current_stage = Column(String, nullable=True)
    team_size = Column(Integer, default=2)
    revenue = Column(String, nullable=True)
    registration_details = Column(Text, nullable=True)
    
    # Uploaded Pitch Deck
    has_pitch_deck = Column(Boolean, default=False)
    pitch_deck_path = Column(String, nullable=True)
    
    # Status & Timing
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team_members = relationship(
        "EurekaTeamMember", 
        back_populates="registration", 
        cascade="all, delete-orphan"
    )


class EurekaTeamMember(Base):
    __tablename__ = "eureka_team_members"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("eureka_registrations.id", ondelete="CASCADE"), nullable=False)
    
    # Personal details
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    college = Column(String, nullable=False)
    department = Column(String, nullable=True)
    year = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    
    is_lead = Column(Boolean, default=False)

    # Relationships
    registration = relationship("EurekaRegistration", back_populates="team_members")
