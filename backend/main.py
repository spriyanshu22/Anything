from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

# Config
SECRET_KEY = "super-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock DB
users_db = {}
notes_db = []

class User(BaseModel):
    username: str
    password: str

@app.post("/api/v1/signup")
def signup(user: User):
    if user.username in users_db: raise HTTPException(400, "User exists")
    users_db[user.username] = {"username": user.username, "password": pwd_context.hash(user.password)}
    return {"msg": "User created"}

@app.post("/api/v1/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = jwt.encode({"sub": user["username"]}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/v1/me")
def get_me(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return {"username": payload.get("sub")}

# Simple CRUD for Notes
@app.get("/api/v1/notes")
def get_notes(): return notes_db

@app.post("/api/v1/notes")
def create_note(note: dict):
    notes_db.append(note)
    return note