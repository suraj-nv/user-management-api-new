from typing import Annotated, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from uuid import UUID
NameStr = Annotated[str, Field(min_length=2, max_length=50)]
UsernameStr = Annotated[str, Field(min_length=3, max_length=20)]
PasswordStr = Annotated[str, Field(min_length=6)]
EmailType = Annotated[EmailStr, Field(description="Valid email required")]


class UserCreate(BaseModel):
    first_name: NameStr
    last_name: NameStr
    username: UsernameStr
    email: EmailType
    password: PasswordStr   # ✅ FIXED

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v):
        allowed_domains = ["gmail.com", "company.com"]
        domain = v.split("@")[-1]

        if domain not in allowed_domains:
            raise ValueError("Email domain not allowed")

        return v


class UserResponse(BaseModel):
    id: UUID
    username: UsernameStr
    email: EmailType
    role: str

    class Config:
        from_attributes = True

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_name: Optional[str] = None
class UserDelete(BaseModel):
    username: str

class UserLogin(BaseModel):
    username: str
    password: str