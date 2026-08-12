from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Tuple
from backend.app.eureka.models import EurekaRegistration, EurekaTeamMember
from backend.app.eureka.schemas import EurekaRegistrationCreate

def generate_registration_id(db: Session) -> str:
    """Generates the next sequential registration ID (e.g. ER001, ER002)."""
    max_id = db.query(func.max(EurekaRegistration.registration_id)).scalar()
    if not max_id:
        return "ER001"
    
    try:
        # Expected format is ERXXX where XXX is a number
        if max_id.startswith("ER") and max_id[2:].isdigit():
            num = int(max_id[2:]) + 1
            return f"ER{num:03d}"
    except (ValueError, IndexError):
        pass
    
    # Fallback/Safety check
    count = db.query(EurekaRegistration).count()
    return f"ER{count + 1:03d}"

def create_registration(db: Session, registration_data: EurekaRegistrationCreate, pitch_deck_path: Optional[str] = None) -> EurekaRegistration:
    """Creates a new registration entry with associated team members in the database."""
    reg_id = generate_registration_id(db)
    
    # Extract team members to create separately
    team_members_data = registration_data.team_members
    
    db_registration = EurekaRegistration(
        registration_id=reg_id,
        startup_name=registration_data.startup_name,
        category=registration_data.category,
        stage=registration_data.stage,
        description=registration_data.description,
        problem_statement=registration_data.problem_statement,
        solution=registration_data.solution,
        is_existing=registration_data.is_existing,
        website=registration_data.website,
        current_stage=registration_data.current_stage,
        team_size=registration_data.team_size,
        revenue=registration_data.revenue,
        registration_details=registration_data.registration_details,
        has_pitch_deck=registration_data.has_pitch_deck,
        pitch_deck_path=pitch_deck_path,
        status="Pending"
    )
    
    db.add(db_registration)
    db.flush()  # Generate db_registration.id
    
    # Create team members
    for member_data in team_members_data:
        db_member = EurekaTeamMember(
            registration_id=db_registration.id,
            name=member_data.name,
            email=member_data.email,
            phone=member_data.phone,
            college=member_data.college,
            department=member_data.department,
            year=member_data.year,
            bank_account=member_data.bank_account,
            is_lead=member_data.is_lead
        )
        db.add(db_member)
        
    db.commit()
    db.refresh(db_registration)
    return db_registration

def get_registrations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> Tuple[List[EurekaRegistration], int]:
    """Retrieves list of registrations and the total matching count based on filters and search."""
    query = db.query(EurekaRegistration)
    
    if status:
        query = query.filter(EurekaRegistration.status == status)
    if category:
        query = query.filter(EurekaRegistration.category == category)
        
    if search:
        # Search startup name, or team member name, or email, or registration_id
        search_filter = or_(
            EurekaRegistration.startup_name.ilike(f"%{search}%"),
            EurekaRegistration.registration_id.ilike(f"%{search}%"),
            EurekaRegistration.team_members.any(EurekaTeamMember.name.ilike(f"%{search}%")),
            EurekaRegistration.team_members.any(EurekaTeamMember.email.ilike(f"%{search}%"))
        )
        query = query.filter(search_filter)
        
    # Get total count before pagination
    total_count = query.distinct().count()
    
    # Order by creation date descending
    results = query.order_by(EurekaRegistration.created_at.desc()).offset(skip).limit(limit).all()
    
    return results, total_count

def get_registration_by_id(db: Session, registration_id: int) -> Optional[EurekaRegistration]:
    """Fetches a specific registration by database PK id."""
    return db.query(EurekaRegistration).filter(EurekaRegistration.id == registration_id).first()

def get_registration_by_code(db: Session, reg_code: str) -> Optional[EurekaRegistration]:
    """Fetches a registration by unique string code (e.g. ER001)."""
    return db.query(EurekaRegistration).filter(EurekaRegistration.registration_id == reg_code).first()

def update_registration_status(db: Session, db_registration: EurekaRegistration, new_status: str) -> EurekaRegistration:
    """Updates status for a registration."""
    db_registration.status = new_status
    db.commit()
    db.refresh(db_registration)
    return db_registration
