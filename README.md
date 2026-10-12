# Bookstore API

A FastAPI backend for a bookstore. Authors can add, update and delete their own books. Readers can browse books and buy them. Authentication is handled with JWT, and passwords are hashed with bcrypt.

## Tech stack
- FastAPI
- SQLAlchemy ORM
- SQLite
- JWT authentication (PyJWT)
- bcrypt for password hashing

## Features
- User registration and login with two roles: author and reader
- Authors can create, update and delete their own books
- Readers can browse all books and place orders
- Stock is checked and reduced when an order is placed
- Role-based access control (an author cannot buy books, a reader cannot add books)

## Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /auth/register | Register a new user | No |
| POST | /auth/login | Login and get a JWT token | No |
| GET | /books/ | List all books | No |
| GET | /books/my | List the logged-in author's books | Author |
| GET | /books/{id} | Get a single book | No |
| POST | /books/ | Add a new book | Author |
| PUT | /books/{id} | Update own book | Author |
| DELETE | /books/{id} | Delete own book | Author |
| POST | /orders/ | Buy a book | Reader |
| GET | /orders/my | List the logged-in reader's orders | Reader |

## Running locally

1. Clone the repo and create a virtual environment.
2. Install dependencies: pip install -r requirements.txt
3. Copy .env.example to .env and fill in your own SECRET_KEY.
4. Start the server: uvicorn main:app --reload
5. Open http://127.0.0.1:8000/docs