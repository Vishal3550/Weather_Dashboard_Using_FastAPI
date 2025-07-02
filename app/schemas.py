from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr
    city: str | None = None
    country: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LocationUpdate(BaseModel):
    city: str
    country: str
