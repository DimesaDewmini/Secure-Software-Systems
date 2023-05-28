from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Dict
import secrets
import sqlite3
from . import predict as prd
from fastapi.middleware.cors import CORSMiddleware

# Set allowed origins, methods, and headers
allowed_origins = ["*"]
allowed_methods = ["*"]
allowed_headers = ["*"]

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DATABASE = "users.db"

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

# User model
class User(BaseModel):
    username: str
    password: str = None

# API key model
class APIKeyModel(BaseModel):
    api_key: str

# Authentication helper functions
def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result is not None:
        hashed_password = result[0]
        if pwd_context.verify(password, hashed_password):
            return True
    return False

def authenticate_api_key(api_key: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE api_key = ?", (api_key,))
    result = cursor.fetchone()
    if result is not None:
        return True
    return False

# Dependency function for authentication using API key
def get_current_user(api_key: str = Security(APIKeyHeader(name="X-API-Key"))) -> User:
    if not authenticate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE api_key = ?", (api_key,))
    result = cursor.fetchone()
    username = result[0]
    return User(username=username)

# Routes
@app.post("/register")
def register_user(user: User) -> Dict[str, str]:
    hashed_password = pwd_context.hash(user.password)
    api_key = secrets.token_hex(16)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, api_key) VALUES (?, ?, ?)", (user.username, hashed_password, api_key))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully", "api_key": api_key}

@app.post("/login")
def login_user(user: User) -> APIKeyModel:
    if not authenticate_user(user.username, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM users WHERE username = ?", (user.username,))
    result = cursor.fetchone()
    api_key = result[0]
    conn.close()
    return APIKeyModel(api_key=api_key)

@app.post("/predict/")
def predict(input:str, user: User = Depends(get_current_user)):
    return int(prd.predict(input))

# Create the database and table if they don't exisst
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, api_key TEXT)")
conn.close()
