import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Role(str, enum.Enum):
    author = "author"
    reader = "reader"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str]
    role: Mapped[Role] = mapped_column(Enum(Role))

    books: Mapped[list["Book"]] = relationship(back_populates="author")
    orders: Mapped[list["Order"]] = relationship(back_populates="reader")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[float]
    stock: Mapped[int] = mapped_column(default=0)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="books")
    orders: Mapped[list["Order"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    quantity: Mapped[int]
    total_price: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reader: Mapped["User"] = relationship(back_populates="orders")
    book: Mapped["Book"] = relationship(back_populates="orders")