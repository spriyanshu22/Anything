import os
import logging
import sqlite3
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from contextlib import contextmanager
from typing import Optional, List

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "app.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

app = FastAPI(title="Auth + Notes API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Database Setup ==============
def init_db():
    """Initialize SQLite database with tables"""
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
    logger.info("Database initialized")

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ============== Pydantic Models ==============
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain alphanumeric characters and underscores')
        return v
    
    @validator('password')
    def password_strong(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: str

class UserProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class Note(BaseModel):
    id: int
    title: str
    content: Optional[str]
    created_at: str
    updated_at: str

class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# ============== Helper Functions ==============
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    
    if user is None:
        raise credentials_exception
    
    return dict(user)

# ============== Auth Endpoints ==============
@app.post("/api/v1/signup", response_model=dict, status_code=201)
def signup(user: UserRegister):
    """Register a new user"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", 
                          (user.username, user.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username or email already registered")
            
            # Create new user
            hashed_password = hash_password(user.password)
            cursor.execute(
                """INSERT INTO users (username, email, password, full_name) 
                   VALUES (?, ?, ?, ?)""",
                (user.username, user.email, hashed_password, user.full_name)
            )
            conn.commit()
            logger.info(f"User registered: {user.username}")
            
        return {"message": "User registered successfully", "username": user.username}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get JWT token"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", 
                          (form_data.username,))
            user = cursor.fetchone()
        
        if not user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        logger.info(f"User logged in: {user['username']}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== Profile Endpoints ==============
@app.get("/api/v1/me", response_model=UserProfile)
def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        created_at=current_user["created_at"]
    )

@app.put("/api/v1/me", response_model=UserProfile)
def update_profile(profile_data: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    """Update current user profile"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            email = profile_data.email or current_user["email"]
            full_name = profile_data.full_name or current_user["full_name"]
            
            # Check if new email is already taken
            if profile_data.email and profile_data.email != current_user["email"]:
                cursor.execute("SELECT id FROM users WHERE email = ?", (profile_data.email,))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Email already in use")
            
            cursor.execute(
                """UPDATE users SET email = ?, full_name = ? WHERE id = ?""",
                (email, full_name, current_user["id"])
            )
            conn.commit()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],))
            updated_user = cursor.fetchone()
        
        logger.info(f"Profile updated for user: {current_user['username']}")
        return UserProfile(
            id=updated_user["id"],
            username=updated_user["username"],
            email=updated_user["email"],
            full_name=updated_user["full_name"],
            created_at=updated_user["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== Notes CRUD Endpoints ==============
@app.post("/api/v1/notes", response_model=Note, status_code=201)
def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    """Create a new note"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO notes (user_id, title, content) 
                   VALUES (?, ?, ?)""",
                (current_user["id"], note.title, note.content)
            )
            conn.commit()
            note_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            new_note = cursor.fetchone()
        
        logger.info(f"Note created by user: {current_user['username']}")
        return Note(
            id=new_note["id"],
            title=new_note["title"],
            content=new_note["content"],
            created_at=new_note["created_at"],
            updated_at=new_note["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create note error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/notes", response_model=List[Note])
def list_notes(current_user: dict = Depends(get_current_user)):
    """List all notes for current user"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC""",
                (current_user["id"],)
            )
            notes = cursor.fetchall()
        
        return [
            Note(
                id=note["id"],
                title=note["title"],
                content=note["content"],
                created_at=note["created_at"],
                updated_at=note["updated_at"]
            )
            for note in notes
        ]
    except Exception as e:
        logger.error(f"List notes error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/notes/{note_id}", response_model=Note)
def get_note(note_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific note"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM notes WHERE id = ? AND user_id = ?""",
                (note_id, current_user["id"])
            )
            note = cursor.fetchone()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return Note(
            id=note["id"],
            title=note["title"],
            content=note["content"],
            created_at=note["created_at"],
            updated_at=note["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get note error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/v1/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note_data: NoteUpdate, current_user: dict = Depends(get_current_user)):
    """Update a note"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if note belongs to user
            cursor.execute(
                """SELECT * FROM notes WHERE id = ? AND user_id = ?""",
                (note_id, current_user["id"])
            )
            note = cursor.fetchone()
            
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            
            title = note_data.title if note_data.title is not None else note["title"]
            content = note_data.content if note_data.content is not None else note["content"]
            
            cursor.execute(
                """UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (title, content, note_id)
            )
            conn.commit()
            
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            updated_note = cursor.fetchone()
        
        logger.info(f"Note updated by user: {current_user['username']}")
        return Note(
            id=updated_note["id"],
            title=updated_note["title"],
            content=updated_note["content"],
            created_at=updated_note["created_at"],
            updated_at=updated_note["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update note error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/v1/notes/{note_id}", status_code=204)
def delete_note(note_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a note"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT id FROM notes WHERE id = ? AND user_id = ?""",
                (note_id, current_user["id"])
            )
            note = cursor.fetchone()
            
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
        
        logger.info(f"Note deleted by user: {current_user['username']}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete note error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== Health Check ==============
@app.get("/api/v1/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# ============== Startup Event ==============
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Application started")

# Simple CRUD for Notes
@app.get("/api/v1/notes")
def get_notes(): return notes_db

@app.post("/api/v1/notes")
def create_note(note: dict):
    notes_db.append(note)
    return note