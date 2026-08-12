from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
import re
from datetime import datetime

class EurekaTeamMemberBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str
    college: str = Field(..., min_length=2, max_length=150)
    department: Optional[str] = None
    year: Optional[str] = None
    bank_account: Optional[str] = None
    is_lead: bool = False

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Standardize and validate phone is 10 digits
        digits = re.sub(r"\D", "", v)
        if len(digits) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return digits

class EurekaTeamMemberCreate(EurekaTeamMemberBase):
    pass

class EurekaTeamMemberResponse(EurekaTeamMemberBase):
    id: int
    registration_id: int

    class Config:
        from_attributes = True


class EurekaRegistrationBase(BaseModel):
    startup_name: str = Field(..., min_length=2, max_length=100)
    category: str
    stage: str
    description: str = Field(..., min_length=10)
    problem_statement: str = Field(..., min_length=10)
    solution: str = Field(..., min_length=10)
    
    is_existing: bool = False
    website: Optional[str] = None
    current_stage: Optional[str] = None
    team_size: int = Field(2, ge=2, le=5)
    revenue: Optional[str] = None
    registration_details: Optional[str] = None
    
    has_pitch_deck: bool = False

class EurekaRegistrationCreate(EurekaRegistrationBase):
    team_members: List[EurekaTeamMemberCreate]

    @field_validator("team_members")
    @classmethod
    def check_team_size(cls, members: List[EurekaTeamMemberCreate], info) -> List[EurekaTeamMemberCreate]:
        # Get team_size from input data if present
        # Note: in pydantic v2, we check validation directly
        if len(members) < 2 or len(members) > 5:
            raise ValueError("Team must have between 2 and 5 members")
        
        # Verify exactly one team lead is present
        leads = [m for m in members if m.is_lead]
        if not leads:
            # Set the first member as lead if none specified
            members[0].is_lead = True
        elif len(leads) > 1:
            raise ValueError("A team can only have one Team Lead")
            
        return members

class EurekaRegistrationResponse(EurekaRegistrationBase):
    id: int
    registration_id: str
    status: str
    created_at: datetime
    pitch_deck_path: Optional[str] = None
    team_members: List[EurekaTeamMemberResponse]

    class Config:
        from_attributes = True


# Admin Schemas
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = ["Pending", "Approved", "Rejected"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v
