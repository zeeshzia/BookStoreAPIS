from fastapi import FastAPI
from database import Base, engine
import models
from routers import auth_router, books_router, orders_router

app = FastAPI(title="Bookstore API")

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(orders_router)