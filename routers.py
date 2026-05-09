from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db
from models import User
from auth import create_access_token
from auth_dependency import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])




@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})

    return {
        "access_token": token,
        "token_type": "bearer"   # 🔥 REQUIRED
    }


# CREATE
@router.post("/create")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user, response, error = crud.create_user(db, user)

        if error:
            raise HTTPException(400, error)

        db.commit()
        db.refresh(db_user)

        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))


# GET ALL (PROTECTED)
@router.get("/all", response_model=list[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        # 🔐 Authorization check
        if current_user.role.name != "admin":
            raise HTTPException(status_code=403, detail="Access denied")

        users = db.query(User).all()

        return [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "role": u.role.name if u.role else None
            }
            for u in users
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/update")
def update_user(
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)   # 🔐 JWT protection
):
    try:
        db_user, response, error = crud.update_user(db, user)

        if error:
            raise HTTPException(status_code=400, detail=error)

        db.commit()
        db.refresh(db_user)

        return response

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/delete")
def delete_user(
    user: schemas.UserDelete,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)   # 🔐 JWT protection
):
    try:
        success, error = crud.delete_user(db, user.username)

        if error:
            raise HTTPException(status_code=400, detail=error)

        if not success:
            raise HTTPException(status_code=404, detail="User not found")

        db.commit()

        return {"message": "User deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))