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


# =====================  AUTH  =====================
@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(
        select(User).where((User.username == data.username) | (User.email == data.email))
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@auth_router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return Token(access_token=create_access_token(user.id))


# =====================  BOOKS  =====================
@books_router.get("/", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.scalars(select(Book)).all()


# "/my" ko "/{book_id}" se pehle rakhna zaroori hai
@books_router.get("/my", response_model=list[BookOut])
def my_books(
    author: User = Depends(require_role(Role.author)), db: Session = Depends(get_db)
):
    return db.scalars(select(Book).where(Book.author_id == author.id)).all()


@books_router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@books_router.post("/", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def add_book(
    data: BookCreate,
    author: User = Depends(require_role(Role.author)),
    db: Session = Depends(get_db),
):
    book = Book(**data.model_dump(), author_id=author.id)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def _get_own_book(book_id: int, author: User, db: Session) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.author_id != author.id:
        raise HTTPException(status_code=403, detail="You can only modify your own books")
    return book


@books_router.put("/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    data: BookUpdate,
    author: User = Depends(require_role(Role.author)),
    db: Session = Depends(get_db),
):
    book = _get_own_book(book_id, author, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    author: User = Depends(require_role(Role.author)),
    db: Session = Depends(get_db),
):
    book = _get_own_book(book_id, author, db)
    db.delete(book)
    db.commit()


# =====================  ORDERS  =====================
@orders_router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def buy_book(
    data: OrderCreate,
    reader: User = Depends(require_role(Role.reader)),
    db: Session = Depends(get_db),
):
    book = db.get(Book, data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.stock < data.quantity:
        raise HTTPException(status_code=400, detail=f"Only {book.stock} copies in stock")

    book.stock -= data.quantity
    order = Order(
        reader_id=reader.id,
        book_id=book.id,
        quantity=data.quantity,
        total_price=book.price * data.quantity,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@orders_router.get("/my", response_model=list[OrderOut])
def my_orders(
    reader: User = Depends(require_role(Role.reader)), db: Session = Depends(get_db)
):
    return db.scalars(select(Order).where(Order.reader_id == reader.id)).all()