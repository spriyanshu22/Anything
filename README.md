# Auth + Dashboard Web App

A full-stack web application built with React, FastAPI, and SQLite featuring user authentication, profile management, and a notes CRUD interface.

## 📋 Tech Stack

### Frontend
- **React 19** - Modern UI library
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Database
- **JWT (python-jose)** - Token-based authentication
- **Passlib + Bcrypt** - Password hashing and verification
- **Pydantic** - Data validation

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- Python 3.9+
- npm or yarn

### Backend Setup

1. **Navigate to backend folder:**
   ```bash
   cd Anything/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and update SECRET_KEY
   ```

5. **Run the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend folder:**
   ```bash
   cd Anything/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 📝 Demo Credentials

Use these credentials to test the application:

```
Username: testuser
Email: test@example.com
Password: password123
Full Name: Test User
```

### How to Seed Demo Account:

1. Open the app at `http://localhost:5173`
2. Click "Sign up"
3. Fill in the form with the credentials above
4. Click "Sign Up"
5. Use the credentials to login

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/signup` - Create new account
- `POST /api/v1/login` - Login and get JWT token

### Profile
- `GET /api/v1/me` - Get current user profile
- `PUT /api/v1/me` - Update profile (email, full name)

### Notes (CRUD)
- `POST /api/v1/notes` - Create a note
- `GET /api/v1/notes` - List all notes
- `GET /api/v1/notes/{id}` - Get single note
- `PUT /api/v1/notes/{id}` - Update a note
- `DELETE /api/v1/notes/{id}` - Delete a note

### Health
- `GET /api/v1/health` - Health check

## ✨ Features

### Frontend
✅ User authentication (signup/login)
✅ Protected routes with JWT
✅ Client-side form validation
✅ Responsive design with TailwindCSS
✅ Notes CRUD interface
✅ User profile management
✅ Search/filter notes
✅ Loading states & error handling
✅ Success notifications
✅ Logout functionality

### Backend
✅ User registration with email validation
✅ Secure password hashing (bcrypt)
✅ JWT-based authentication
✅ Protected API endpoints
✅ Input validation with Pydantic
✅ CORS enabled for frontend
✅ SQLite database with proper schema
✅ Structured error responses
✅ Basic logging
✅ Startup database initialization

## 🔐 Security Features

- **Password Hashing**: Bcrypt with passlib
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Server-side validation for all inputs
- **CORS**: Configured for frontend origin
- **Protected Routes**: JWT middleware on protected endpoints
- **Email Validation**: Pydantic EmailStr field validation
- **Error Handling**: No sensitive data in error messages

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Notes Table
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

## 📈 Scalability & Production Notes

### Current Architecture
- Single-file FastAPI backend
- In-memory auth context (frontend)
- SQLite database (suitable for single-server deployments)

### Production Improvements

1. **Database**
   - Migrate to PostgreSQL for better concurrency
   - Add proper indexing on frequently queried fields
   - Implement connection pooling
   - Set up regular backups

2. **Backend**
   - Split `main.py` into modular structure (routers, models, schemas)
   - Add database migrations (Alembic)
   - Implement refresh tokens for better security
   - Add rate limiting (slowapi)
   - Setup proper logging with structured logging
   - Add request/response monitoring
   - Implement caching (Redis) for frequently accessed data

3. **Frontend**
   - Add error boundary components
   - Implement infinite scroll or pagination
   - Cache API responses with React Query
   - Add service workers for offline support
   - Implement optimistic updates for CRUD operations
   - Add TypeScript for type safety

4. **DevOps**
   - Containerize both frontend and backend (Docker)
   - Setup CI/CD pipeline (GitHub Actions)
   - Use environment-specific configurations
   - Implement blue-green deployments
   - Setup monitoring and alerting

5. **Security**
   - Use environment variables for all secrets
   - Implement password reset flow
   - Add 2FA support
   - Regular security audits
   - Implement OWASP best practices
   - Add helmet.js for HTTP headers (Node/Express)

6. **Performance**
   - Implement API pagination
   - Add database query optimization
   - Setup CDN for static assets
   - Enable gzip compression
   - Implement request caching strategies

## 📋 Postman Collection

A Postman collection file (`postman_collection.json`) is included in the project root. Import it to test all API endpoints.

### How to Import:
1. Open Postman
2. Click "Import"
3. Select `postman_collection.json`
4. The collection will be ready to use

Note: Set the `token` variable in Postman after login with the JWT token from the response.

## 🐛 Troubleshooting

### CORS Errors
Ensure both frontend and backend are running on the correct ports (5173 and 8000)

### Database Errors
Delete `Anything/backend/app.db` and restart the backend to reinitialize

### Authentication Issues
Clear browser localStorage if tokens become invalid:
```javascript
localStorage.clear()
```

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Built as part of the Frontend Developer Intern Shortlisting Assignment

---

**Questions or Issues?** Please create an issue in the GitHub repository.
