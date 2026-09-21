from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from models import Role


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    role: Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    price: float
    stock: int
    author_id: int


class OrderCreate(BaseModel):
    book_id: int
    quantity: int = Field(ge=1)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    book_id: int
    quantity: int
    total_price: float
    created_at: datetime