import traceback
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from database import Base, engine
import models
from routers import auth_router, books_router, orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bookstore API")


@app.exception_handler(Exception)
async def show_error(request: Request, exc: Exception):
    return PlainTextResponse(traceback.format_exc(), status_code=500)


app.include_router(auth_router)
app.include_router(books_router)
app.include_router(orders_router)