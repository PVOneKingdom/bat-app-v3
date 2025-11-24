# BAT App v3 - Repository Analysis

## Executive Summary

**BAT App v3** (Benchmark Assessment Tool) is a FastAPI-based web application designed for conducting structured business assessments with visualization capabilities. The application enables coaches and administrators to manage assessments, generate reports with visual "wheel" representations, and provide actionable recommendations to users.

**Version**: 3.0.8 (in development)
**Migration**: Refactored from WordPress to FastAPI for improved flexibility and developer experience

---

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite3 with Write-Ahead Logging (WAL) mode
- **Authentication**: JWT tokens via `python-jose`
- **Password Security**: bcrypt hashing via `passlib`
- **Template Engine**: Jinja2
- **Date Formatting**: Babel

### Frontend
- **CSS Framework**: Bulma (without dark mode)
- **Dynamic Updates**: HTMX for partial page refreshes
- **Rich Text Editor**: Quill.js (report editing)
- **Drag & Drop**: Sortable.js (question reordering)
- **JavaScript**: Vanilla JS with modular components

### Security & Integration
- **CAPTCHA**: Optional Cloudflare Turnstile on login
- **Email**: Optional SMTP integration for notifications
- **HTTPS**: Configurable middleware for reverse proxy setups

### Dependencies
```
fastapi[standard]
python-jose[cryptography]
passlib
python-multipart
python-dotenv
requests
babel
bcrypt==4.3.0
```

---

## Architecture

### Layered Design Pattern

```
┌─────────────────────────────────────────┐
│  Presentation Layer (web/, api/)        │
│  - Route handlers                        │
│  - Request/Response formatting           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Service Layer (service/)                │
│  - Business logic                        │
│  - Authorization checks                  │
│  - Data transformation                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Data Access Layer (data/)               │
│  - Database queries                      │
│  - CRUD operations                       │
│  - Model conversion                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Database (SQLite)                       │
└─────────────────────────────────────────┘
```

### Directory Structure

```
bat-app-v3/
├── app/
│   ├── api/              # API endpoints (/api/v1/auth)
│   ├── config/           # Environment configuration
│   ├── data/             # Data access layer (DAL)
│   ├── db/               # SQLite database files
│   ├── exception/        # Custom exception handlers
│   ├── model/            # Pydantic data models
│   ├── service/          # Business logic layer
│   ├── static/           # CSS, JS, images, SVG wheels
│   ├── template/         # Jinja2 HTML templates
│   ├── uploads/          # User-uploaded files
│   ├── web/              # Web route handlers
│   ├── main.py           # Application entry point
│   └── .env              # Environment variables
├── requirements.txt
├── compose.yml           # Docker/Podman compose
├── containerfile         # Container build
└── README.md
```

---

## Database Schema

### Core Tables

**users**
- Primary key: `user_id` (UUID)
- Fields: username, email, hash, role, password_reset_token, reset_token_expires
- Unique: username, email

**questions_categories**
- 13 business assessment dimensions
- Fields: category_id, category_name, category_order

**questions**
- 4 questions per category (52 total)
- Fields: question_id, category_id, question, question_description, question_order, option_yes, option_mid, option_no

**assessments**
- Primary key: `assessment_id` (UUID)
- Foreign key: `owner_id` → users
- Fields: assessment_name, owner_id, last_edit, last_editor

**assessments_questions** & **assessments_questions_categories**
- "Frozen" snapshots of questions/categories at assessment creation time
- Prevents retroactive changes to existing assessments

**assessments_answers**
- Primary key: `answer_id` (UUID)
- Foreign keys: assessment_id, question_id
- Fields: answer_option (Yes/Mid/No), answer_description

**assessments_notes**
- Coach notes per category
- Fields: note_id, assessment_id, category_order, note_content (JSON)

**reports**
- Primary key: `report_id` (UUID)
- Foreign key: `assessment_id`
- Fields: report_name, public, key, wheel_filename, summary, recommendation_title_1-3, recommendation_content_1-3
- Stores published reports with SVG visualizations

---

## Authentication & Authorization

### JWT-Based Authentication

**Flow**:
1. User submits credentials → `/login` (POST)
2. Optional Cloudflare Turnstile verification
3. Password verified with bcrypt
4. JWT token generated (30-min expiry, configurable)
5. Token stored in HTTP-only, secure cookie
6. Client-side JWT manager auto-renews before expiry

**Token Payload**:
```json
{
  "user_id": "<uuid>",
  "exp": <timestamp>
}
```

**Key Files**:
- `app/service/authentication.py` - Core auth logic
- `app/api/auth.py` - Token validation endpoint
- `app/static/js/jwt-manager.js` - Client-side token refresh

### Role-Based Access Control (RBAC)

**Roles**:
1. **admin** - Full system access
2. **coach** - Manage users (except admins), assessments, questions, reports
3. **user** - View/edit own assessments only

**Permission Methods** (User model):
- `can_grant_roles()` - Returns assignable roles
- `can_create_user()` - User creation permission
- `can_delete_user()` - User deletion permission
- `can_modify_user()` - User modification permission
- `can_manage_questions()` - Question management access
- `can_manage_assessments()` - Assessment management access
- `can_manage_reports()` - Report management access

### Security Features
- bcrypt password hashing (configurable cost factor)
- HTTP-only cookies (XSS prevention)
- CSRF protection via SameSite attribute
- Optional HTTPS enforcement
- Time-limited password reset tokens (60 min)
- Prepared statements (SQL injection prevention)

---

## API Routes

### Public Routes (`/`)
- `GET /` - Homepage
- `GET/POST /login` - Authentication
- `GET /logout` - Logout
- `GET/POST /password-reset` - Password reset request
- `GET/POST /set-password` - Set new password with token
- `GET /token-check` - Validate JWT and redirect
- `GET /token-renew` - Refresh JWT token

### Dashboard Routes (`/dashboard/*`)

**Users** (`/dashboard/users`):
- `GET /` - List users
- `GET/POST /add` - Create user
- `GET/PUT /{user_id}` - Update user
- `DELETE /{user_id}` - Delete user

**Questions** (`/dashboard/questions`):
- `GET /` - List categories
- `GET /category/{category_id}` - List questions
- `GET/POST /category/{category_id}/rename` - Rename category
- `POST /category/reorder` - Reorder categories (drag-drop)
- `GET/PUT /edit/{question_id}` - Edit question

**Assessments** (`/dashboard/assessments`):
- `GET /` - List all assessments
- `GET/POST /create` - Create assessment
- `GET /{assessment_id}` - View assessment
- `GET /edit/{assessment_id}` - Edit assessment
- `GET/POST /edit/{assessment_id}/{category_order}/{question_order}` - Answer question
- `GET /review/{assessment_id}` - Review all answers
- `GET /review/{assessment_id}/{category_order}` - Review category
- `DELETE /{assessment_id}` - Delete assessment
- `GET/POST /rename/{assessment_id}` - Rename assessment
- `GET/POST /chown/{assessment_id}` - Change owner

**Reports** (`/dashboard/reports`):
- `GET /` - List all reports
- `GET/POST /create` - Create report
- `GET/POST /edit/{report_id}` - Edit report
- `GET /preview/{report_id}` - Preview report
- `PATCH /publish/{report_id}/{public}` - Toggle public status
- `DELETE /{report_id}` - Delete report
- `GET /notify-user/{report_id}` - Send email notification

### App Routes (`/app/*`) - User Interface
- `/app/assessments/*` - View/edit own assessments
- `/app/reports/*` - View published reports
- `GET/POST /app/profile` - User profile management

### API Endpoints (`/api/v1/auth`)
- `GET /api/v1/auth/` - Health check
- `GET /api/v1/auth/token-check` - Validate and refresh JWT

---

## Key Features

### 1. Assessment Management
- **13 Categories × 4 Questions** = 52-question structured assessment
- **Question Freezing**: Questions/categories frozen at assessment creation (prevents retroactive changes)
- **Three-Option Answers**: Yes/Mid/No responses with optional text descriptions
- **Progress Tracking**: Visual "wheel" shows completion status
- **Category Notes**: Coaches can add notes per category for deeper insights

### 2. The Wheel Visualization
- **SVG-based circular chart** with 13 segments (one per category)
- **Color-coded segments**: Different colors for Yes/Mid/No answers
- **Multiple templates**:
  - `wheel.svg` - Dashboard view
  - `wheel-app.svg` - User app view
  - `wheel-review.svg` - Review mode
  - `wheel-report.svg` - Report snapshot (frozen at creation time)
- **Interactive**: Hover effects show category details

### 3. Report Generation
- **Snapshot Creation**: SVG wheel generated and saved at report creation
- **Rich Text Editing**: Quill.js editor for summary section
- **Three Recommendations**: Structured format with separate titles and content
- **Public/Private Toggle**: Control visibility
- **Unique Access Keys**: Secure URL keys for sharing
- **Email Notifications**: Optional SMTP integration to notify users when reports are ready

### 4. User Management
- **Role Hierarchy**: Admin → Coach → User
- **Self-Service Creation**: Admins/coaches create users
- **Random Password Generation**: Optional auto-generated secure passwords
- **Email Notifications**: Welcome emails with password reset links
- **Profile Editing**: Users can update their own information

### 5. Question Management
- **Category System**: 13 predefined business dimensions
- **Question Editing**: Modify questions and answer option labels
- **Drag-and-Drop Reordering**: Reorder categories via Sortable.js
- **Bulk Loading**: JSON-based default question import on first run

### 6. HTMX Integration
- **Partial Page Updates**: Dynamic content without full page reloads
- **Progressive Enhancement**: Works without JavaScript (degrades gracefully)
- **Loading States**: Bulma classes show spinners during requests
- **Custom Error Handling**: Graceful error display

---

## Configuration

### Environment Variables (`.env`)

```bash
# Security (Required)
SECRET_KEY="<64-char-hex>"           # Generate: openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default Admin User (Required)
DEFAULT_USER="admin"
DEFAULT_EMAIL="admin@example.com"
DEFAULT_PASSWORD="password123456"

# Optional: Cloudflare Turnstile CAPTCHA
CF_TURNSTILE_SITE_KEY=""
CF_TURNSTILE_SECRET_KEY=""

# Optional: SMTP Email Notifications
SMTP_LOGIN=""
SMTP_PASSWORD=""
SMTP_EMAIL=""
SMTP_SERVER=""
SMTP_PORT=""

# Optional: HTTPS Enforcement
FORCE_HTTPS_PATHS=True
```

### Setup Process

1. **Generate encryption key**:
   ```bash
   openssl rand -hex 32
   ```

2. **Configure `.env`** with the generated key

3. **Set PYTHONPATH**:
   ```bash
   export PYTHONPATH="$(pwd)"
   ```

4. **Initialize database** (run once):
   ```bash
   python -i app/main.py
   ```
   ```python
   from app.service.user import add_default_user
   from app.service.question import add_default_questions
   add_default_user()
   add_default_questions()
   ```

5. **Run application**:
   ```bash
   cd app
   fastapi run
   ```

### Container Deployment

```bash
# Build
podman build -f containerfile -t bat-app:latest .

# Run
podman-compose up
# or
docker-compose up
```

Volumes mounted for persistence:
- Database files (`app/db/`)
- User uploads (`app/uploads/`)

---

## Notable Design Patterns

### 1. Exception-Driven Flow Control
Custom exceptions manage authentication and navigation:
- `RedirectToLoginException` → Triggers HX-Redirect to login page
- `NonHTMXRequestException` → Converts regular requests to HTMX format
- Service-layer exceptions bubble up with meaningful error messages

### 2. Dependency Injection
FastAPI's `Depends()` resolves current user from JWT:
```python
def get_users(current_user: User = Depends(user_htmx_dep)):
    # current_user automatically extracted from JWT token
    pass
```

### 3. Model-to-Dict Conversion
Consistent pattern in data access layer:
```python
def row_to_model(row: tuple) -> User:
    # Convert SQLite row to Pydantic model

def model_to_dict(user: User) -> dict:
    # Convert Pydantic model to dict for INSERT/UPDATE
```

### 4. Progressive Enhancement
- Application works with JavaScript disabled (falls back to full page loads)
- HTMX enhances with partial updates when JavaScript is available
- Forms use standard HTML with HTMX attributes for progressive enhancement

### 5. Service Layer Authorization
All service methods enforce permissions:
```python
def get_all(current_user: User) -> list[Question]:
    if not current_user.can_manage_questions():
        raise Unauthorized("You cannot manage questions.")
    return data.get_all()
```

---

## Security Considerations

### Strengths
- JWT tokens with short expiry (30 min, configurable)
- bcrypt password hashing with configurable cost factor
- HTTP-only, secure cookies prevent XSS attacks
- Role-based access control enforced at service layer
- Foreign key constraints maintain database integrity
- Prepared statements prevent SQL injection
- Password reset tokens expire in 60 minutes
- Optional CAPTCHA on login (Cloudflare Turnstile)
- HTTPS enforcement via middleware

### Potential Improvements
- SQLite with WAL mode not ideal for high concurrency (consider PostgreSQL for production)
- No rate limiting on most API endpoints (only simulated delay on login)
- No password complexity requirements enforced
- No account lockout after failed login attempts
- Some debug print statements in production code
- Broad exception handlers could mask specific errors

---

## Current Development Status

**Branch**: `feature/3.0.8-adding-quill-to-reports-editor`
**Modified**: `app/template/jinja/dashboard/report-edit.html`

### Recent Development Activity
- Integration of Quill.js rich text editor for report editing
- JWT token handling improvements
- HTMX targeting optimizations (prevent full page reloads)
- Button double-click prevention fixes
- Token security enhancements (moved from query params to HTTP headers)

---

## Critical File Reference

### Configuration & Initialization
- `app/config/__init__.py` - Environment variable loading
- `app/data/init.py` - Database initialization and schema
- `app/main.py` - Application entry point, middleware, router registration

### Business Logic (Service Layer)
- `app/service/authentication.py` - JWT creation, validation, password hashing
- `app/service/user.py` - User management, RBAC logic
- `app/service/assessment.py` - Assessment CRUD, question freezing
- `app/service/question.py` - Question/category management
- `app/service/report.py` - Report generation, wheel snapshots
- `app/service/notification.py` - SMTP email notifications

### Data Access Layer
- `app/data/user.py` - User database operations
- `app/data/assessment.py` - Assessment database operations
- `app/data/question.py` - Question database operations
- `app/data/report.py` - Report database operations
- `app/data/note.py` - Assessment notes database operations

### Web Routes (Presentation Layer)
- `app/web/public.py` - Public pages (login, password reset)
- `app/web/dashboard/users.py` - User management interface
- `app/web/dashboard/questions.py` - Question management interface
- `app/web/dashboard/assessments.py` - Assessment management interface
- `app/web/dashboard/reports.py` - Report management interface
- `app/web/app/assessments.py` - User assessment interface
- `app/web/app/reports.py` - User report viewing
- `app/web/app/profile.py` - User profile management
- `app/api/auth.py` - API authentication endpoints

### Frontend Assets
- `app/static/js/jwt-manager.js` - Client-side token refresh
- `app/static/js/quill-controller.js` - Rich text editor initialization
- `app/static/js/assessment-wheel-hover.js` - Wheel interactivity
- `app/static/js/htmx-process-errors.js` - HTMX error handling
- `app/static/css/style.css` - Custom styles
- `app/template/jinja/index.html` - Base template with navigation

---

## Use Cases

### Administrator
1. Create coach/user accounts with appropriate roles
2. Manage all assessments across the organization
3. Oversee question templates and categories
4. Review all generated reports
5. Configure system settings

### Coach
1. Create user accounts for clients
2. Create assessments for users
3. Conduct assessment interviews (fill out questions)
4. Add notes per category for deeper insights
5. Generate reports with recommendations
6. Publish reports and notify users via email
7. Manage questions and categories

### End User
1. View assigned assessments
2. Review assessment results (wheel visualization)
3. Access published reports
4. Update profile information
5. Request password resets

---

## Summary

BAT App v3 is a well-architected, modern Python web application that successfully migrated from WordPress to FastAPI. It provides a robust platform for conducting structured business assessments with:

- **Clean Architecture**: Clear separation of concerns (presentation → service → data layers)
- **Security-First Design**: JWT authentication, bcrypt hashing, RBAC throughout
- **Rich Visualizations**: SVG-based "wheel" charts for assessment progress
- **Progressive Enhancement**: HTMX for modern UX while maintaining accessibility
- **Flexible Deployment**: Runs standalone, containerized, or on Railway.app
- **Extensible Design**: Layered architecture supports future enhancements

The application demonstrates solid engineering practices including dependency injection, exception-driven flow control, and consistent model-to-dict conversion patterns. The codebase is maintainable, testable, and ready for production deployment with proper environment configuration.

---

## Deployment Notes

### Railway.app Deployment

BAT App v3 is optimized for Railway deployment with:

**Files:**
- `Procfile` - Defines start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Automatic directory creation for `app/db` and `app/uploads` on startup

**Required Environment Variables:**
- `SECRET_KEY` (generate with `openssl rand -hex 32`)
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `DEFAULT_USER`, `DEFAULT_EMAIL`, `DEFAULT_PASSWORD`
- `FORCE_HTTPS_PATHS=True` (recommended)
- Optional: SMTP settings, Cloudflare Turnstile keys

**Critical: Persistent Volume**

Railway uses ephemeral storage - a volume is REQUIRED for production.

**Single Volume Design (Free Tier Compatible):**

| Mount Path | Purpose | Size |
|------------|---------|------|
| `/app/app/data` | ALL persistent data (database + uploads) | 2GB+ |

**Internal Structure:**
- `/app/app/data/db/` - SQLite database + WAL files
- `/app/app/data/uploads/` - User uploads, report SVGs

Without a volume, all data is lost on each deployment. The application automatically creates the internal directory structure.

**Deployment Process:**
1. Connect GitHub repository to Railway
2. Configure environment variables
3. Add persistent volume at `/app/app/data`
4. Deploy automatically on git push

See README.md for detailed Railway deployment instructions including troubleshooting guide.
