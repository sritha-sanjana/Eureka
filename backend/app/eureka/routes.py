import os
import json
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import create_access_token, verify_password, get_current_admin
from backend.app.eureka.schemas import (
    EurekaRegistrationCreate,
    EurekaRegistrationResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminStatusUpdate
)
from backend.app.eureka import crud
from backend.app.eureka.services.excel import generate_eureka_excel

router = APIRouter()

# ----------------- ADMIN AUTHENTICATION -----------------

@router.post("/admin/login", response_model=AdminLoginResponse)
def admin_login(payload: AdminLoginRequest):
    """Logs in an admin and returns a JWT token."""
    # Compare with configured credentials
    if payload.username != settings.ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    # We compare the password against plain text configured in settings (or hash it if preferred)
    if payload.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    # Create access token
    access_token = create_access_token(data={"sub": payload.username, "role": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}


# ----------------- REGISTRATION FLOW -----------------

@router.post("/register", response_model=EurekaRegistrationResponse)
async def register_startup(
    data: str = Form(...),
    pitch_deck: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Submits a registration form with team members and optional pitch deck file.
    Receives JSON payload string in form field `data` to support mixed multi-part upload.
    """
    # 1. Parse and validate JSON data string
    try:
        data_dict = json.loads(data)
        registration_data = EurekaRegistrationCreate(**data_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid JSON format in registration data"
        )
    except ValidationError as e:
        # Convert Pydantic error details to friendly format
        errors = []
        for err in e.errors():
            loc = " -> ".join(str(x) for x in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    # 2. File handling (pitch deck)
    pitch_deck_path = None
    if pitch_deck:
        # Validate file type
        file_ext = os.path.splitext(pitch_deck.filename)[1].lower()
        if file_ext != ".pdf" and pitch_deck.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Pitch deck must be a PDF file."
            )

        # Validate file size (10 MB Limit) and keep the bytes for saving
        file_bytes = await pitch_deck.read()
        file_size = len(file_bytes)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Pitch deck must not exceed 10MB."
            )
            
        # Ensure uploads folder exists
        uploads_subdir = os.path.join(settings.UPLOAD_DIR, "eureka")
        os.makedirs(uploads_subdir, exist_ok=True)
        
        # Save file with unique filename
        unique_name = f"eureka_{uuid.uuid4().hex}.pdf"
        file_save_path = os.path.join(uploads_subdir, unique_name)
        
        try:
            with open(file_save_path, "wb") as buffer:
                buffer.write(file_bytes)
            pitch_deck_path = f"/uploads/eureka/{unique_name}"
            # Mark that a pitch deck is attached
            registration_data.has_pitch_deck = True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded pitch deck: {str(e)}"
            )

    # 3. Save to database
    try:
        new_registration = crud.create_registration(
            db=db, 
            registration_data=registration_data, 
            pitch_deck_path=pitch_deck_path
        )
        
        # Simulating Email confirmation
        print(f"\n[EMAIL SIMULATOR] Registration confirmation sent to team lead: {new_registration.team_members[0].email}")
        print(f"[EMAIL SIMULATOR] Registration ID: {new_registration.registration_id}\n")
        
        return new_registration
    except Exception as e:
        # Delete uploaded file if database insert failed
        if pitch_deck_path:
            full_path = os.path.join(settings.UPLOAD_DIR, "eureka", os.path.basename(pitch_deck_path))
            if os.path.exists(full_path):
                os.remove(full_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database registration failed: {str(e)}"
        )


# ----------------- ADMIN DASHBOARD ENDPOINTS -----------------

@router.get("/admin/registrations")
def get_admin_registrations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Fetches list of applications for Admin portal. Requires JWT token."""
    registrations, total = crud.get_registrations(
        db=db, 
        skip=skip, 
        limit=limit, 
        status=status, 
        category=category, 
        search=search
    )
    from backend.app.eureka.models import EurekaRegistration
    total_all = db.query(EurekaRegistration).count()
    pending_all = db.query(EurekaRegistration).filter(EurekaRegistration.status == "Pending").count()
    approved_all = db.query(EurekaRegistration).filter(EurekaRegistration.status == "Approved").count()
    rejected_all = db.query(EurekaRegistration).filter(EurekaRegistration.status == "Rejected").count()

    # Serialize registrations explicitly so nested team_members are included
    reg_list = [
        EurekaRegistrationResponse.model_validate(r, from_attributes=True).model_dump(mode="json")
        for r in registrations
    ]

    return {
        "total": total,
        "registrations": reg_list,
        "counts": {
            "total": total_all,
            "pending": pending_all,
            "approved": approved_all,
            "rejected": rejected_all
        },
        "skip": skip,
        "limit": limit
    }

@router.patch("/admin/registrations/{id}/status", response_model=EurekaRegistrationResponse)
def update_registration_status(
    id: int,
    payload: AdminStatusUpdate,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Updates registration status (Pending, Approved, Rejected). Requires JWT token."""
    db_registration = crud.get_registration_by_id(db=db, registration_id=id)
    if not db_registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Registration not found"
        )
    return crud.update_registration_status(db=db, db_registration=db_registration, new_status=payload.status)

@router.get("/admin/export")
def export_registrations(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Generates and returns an Excel sheet containing all matching registrations. Requires JWT token."""
    # Fetch all records without pagination for full export
    registrations, _ = crud.get_registrations(
        db=db, 
        skip=0, 
        limit=100000, 
        status=status, 
        category=category, 
        search=search
    )
    
    excel_stream = generate_eureka_excel(registrations)
    
    headers = {
        'Content-Disposition': 'attachment; filename="Eureka_Registrations.xlsx"',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    return StreamingResponse(excel_stream, headers=headers)
