from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth import hash_password, verify_password, create_access_token, require_role
from database import get_db
from models import User, Book, Order, Role
from schemas import (
    UserCreate, UserOut, Token,
    BookCreate, BookUpdate, BookOut,
    OrderCreate, OrderOut,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
books_router = APIRouter(prefix="/books", tags=["Books"])
orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
