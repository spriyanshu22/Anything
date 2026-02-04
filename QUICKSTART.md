# Quick Start Guide

This guide will get you up and running in 5 minutes.

## Prerequisites
- Node.js 16+ and npm
- Python 3.9+

## Option 1: Using Docker (Recommended)

### 1. Install Docker Desktop
Download and install from https://www.docker.com/products/docker-desktop

### 2. Build and Run
```bash
cd Anything
docker-compose up
```

The app will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Option 2: Manual Setup

### Backend Setup (Terminal 1)
```bash
cd Anything/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

Backend will run on http://localhost:8000

### Frontend Setup (Terminal 2)
```bash
cd Anything/frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend will run on http://localhost:5173

## Test the Application

1. **Sign Up**
   - Go to http://localhost:5173/signup
   - Create a new account with any username/email
   - Fill in the registration form

2. **Login**
   - Use your credentials to login

3. **Create a Note**
   - Click "+ New Note" on the dashboard
   - Enter title and content
   - Click "Create Note"

4. **Edit/Delete Notes**
   - Click "Edit" to modify a note
   - Click "Delete" to remove a note

5. **Update Profile**
   - Click "Edit Profile" on the profile card
   - Update your email or full name

## Test with Postman

1. Import `postman_collection.json` into Postman
2. Use the "Login" request to get a token
3. Copy the token to the `{{token}}` variable
4. Test other endpoints

## API Documentation

FastAPI provides interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**Database errors?**
```bash
# Delete database and restart
cd backend && rm app.db && python3 -m uvicorn main:app --reload
```

**Clear browser storage:**
Open DevTools (F12) → Application → LocalStorage → Delete all

---

**Next Steps:**
- Read README.md for full documentation
- Check SCALABILITY.md for production strategies
- Review backend/main.py for code structure
