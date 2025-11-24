# BAT App v3

Main improvement is to set it free from Wordpress to allow for more flexibility while developing.

The functions by themselves are pretty much the same as they were but further development should be much much easier.

## Deployment Options

- **[Railway.app Deployment](#railway-deployment)** - One-click cloud deployment (recommended for production)
- **[Local Development](#local-development)** - Run locally with FastAPI
- **[Container Deployment](#container-deployment)** - Docker/Podman compose

---

## Railway Deployment

Deploy BAT App v3 to Railway.app in minutes.

### Prerequisites

- Railway.app account ([sign up here](https://railway.app))
- GitHub account with repository access

### Step 1: Create New Project on Railway

1. Go to [Railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `bat-app-v3` repository
5. Railway will automatically detect the `Procfile` and Python configuration

### Step 2: Configure Environment Variables

In Railway's project settings, add these environment variables:

**Required Variables:**
```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEFAULT_USER=admin
DEFAULT_EMAIL=admin@example.com
DEFAULT_PASSWORD=<your-secure-password>
FORCE_HTTPS_PATHS=True
```

**Optional Variables (for email notifications):**
```bash
SMTP_LOGIN=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_EMAIL=noreply@yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Optional Variables (for Cloudflare Turnstile CAPTCHA):**
```bash
CF_TURNSTILE_SITE_KEY=your-site-key
CF_TURNSTILE_SECRET_KEY=your-secret-key
```

### Step 3: Generate SECRET_KEY

Generate a secure secret key on your local machine:

```bash
openssl rand -hex 32
```

Copy the output and paste it as the `SECRET_KEY` value in Railway.

### Step 4: Deploy

1. Click **"Deploy"** in Railway
2. Railway will:
   - Install dependencies from `requirements.txt`
   - Use the `Procfile` to start the application with uvicorn
   - Automatically run database initialization (create default user and questions)
3. Once deployed, Railway will provide a public URL (e.g., `https://your-app.railway.app`)

### Step 5: Access Your Application

1. Visit your Railway-provided URL
2. Log in with the credentials you set in `DEFAULT_USER` and `DEFAULT_PASSWORD`
3. Change the default password immediately after first login

### Persistent Storage on Railway (CRITICAL)

**⚠️ IMPORTANT:** Railway uses ephemeral storage by default, meaning all data is lost on each deployment. You **MUST** configure volumes for production use.

#### Why Volumes Are Required

Without persistent volumes:
- ❌ Database is recreated on every deployment (all assessments, users, reports lost)
- ❌ Uploaded files disappear after redeployment
- ❌ Default admin user reset on each deployment

#### Required Volumes Configuration

Railway supports persistent volumes that survive deployments. You need **TWO volumes**:

**Volume 1: Database Storage**
- **Mount Path:** `/app/app/db`
- **Purpose:** Stores SQLite database file (`database.db`) and WAL files
- **Recommended Size:** Start with 1GB (SQLite is very space-efficient)
- **Critical:** Without this, all user data, assessments, and reports are lost on redeploy

**Volume 2: Uploads Storage**
- **Mount Path:** `/app/app/uploads`
- **Purpose:** Stores user-uploaded files and generated report visualizations (SVG wheels)
- **Recommended Size:** Start with 2GB (depends on usage)
- **Critical:** Without this, report images and user uploads are lost on redeploy

#### How to Add Volumes in Railway

1. **Open your Railway project** and select your service
2. **Go to Settings tab** → scroll to "Volumes" section
3. **Add Database Volume:**
   - Click **"+ Add Volume"**
   - **Mount Path:** `/app/app/db`
   - **Name:** `bat-app-database` (or your preference)
   - Click **"Add"**
4. **Add Uploads Volume:**
   - Click **"+ Add Volume"** again
   - **Mount Path:** `/app/app/uploads`
   - **Name:** `bat-app-uploads` (or your preference)
   - Click **"Add"**
5. **Redeploy** your application for volumes to take effect

#### Verification

After adding volumes and redeploying:
1. Log in to your application
2. Create a test assessment
3. Trigger a redeploy (push a small change to GitHub)
4. Log in again - your test assessment should still be there ✅

#### Volume Paths Summary

| Data Type | Mount Path | Files Stored | Persistence |
|-----------|------------|--------------|-------------|
| Database | `/app/app/db` | `database.db`, `database.db-wal`, `database.db-shm` | Required |
| Uploads | `/app/app/uploads` | User uploads, report SVGs | Required |

**Note:** The `/app` prefix in mount paths corresponds to the working directory set by Railway. Inside the application code, these directories are referenced as `app/db` and `app/uploads` relative to the project root.

### Updating Your Deployment

Railway automatically redeploys when you push to your connected GitHub branch:

```bash
git add .
git commit -m "Update application"
git push origin main
```

### Troubleshooting Railway Deployment

#### Issue: "RuntimeError: Directory does not exist"
**Symptom:** App crashes on startup with `RuntimeError: Directory '/app/app/uploads' does not exist`

**Solution:** This is fixed in version 3.0.9+. The app now automatically creates required directories. If you're on an older version:
```bash
git pull origin main
# Redeploy on Railway
```

#### Issue: Data lost after redeployment
**Symptom:** All assessments, users, and uploads disappear after pushing new code

**Solution:** You haven't configured persistent volumes. See [Persistent Storage](#persistent-storage-on-railway-critical) section above.

#### Issue: Can't log in after deployment
**Symptom:** Login fails or redirects to login page repeatedly

**Possible causes:**
1. **Wrong credentials:** Check your Railway environment variables for `DEFAULT_USER` and `DEFAULT_PASSWORD`
2. **SECRET_KEY not set:** Verify `SECRET_KEY` is configured in Railway environment variables
3. **HTTPS redirect issue:** If behind a reverse proxy, ensure `FORCE_HTTPS_PATHS=True` is set

#### Issue: Application crashes immediately
**Check Railway logs** for specific errors:
1. Go to your Railway project
2. Click on your service
3. Go to "Deployments" tab
4. Click on the latest deployment
5. Check logs for error messages

Common errors:
- **"Secret Key value is None"** → Set `SECRET_KEY` in environment variables
- **"ModuleNotFoundError"** → Dependency missing, check `requirements.txt`
- **"Address already in use"** → Railway assigns `$PORT` dynamically, ensure Procfile uses it

#### Issue: SMTP emails not sending
**Solution:** Verify all SMTP environment variables are set:
```
SMTP_LOGIN=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_EMAIL=noreply@yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

---

## Local Development

### Setup Instructions

For local setup there are 2 things needed to do + one optional:

1) Set encryption key
2) Add default user and questions
3) Optional: Set SMTP settings for the app

### 1) Set encryption key

We are using 32 character long hex string. Easiest way to generate it is through OpenSSL

```bash
openssl rand -hex 32
```
Then store the value in the .env file

### 2) Set credentials for default user and add questions

These values are also stored in the .env file. So either edit that or copy the example into the `.env`

Make sure you are in the repository root directory. Not in the `app` folder but one above it.

```bash
export PYTHONPATH="$( pwd )"
```

Now run python in interactive mode and add default user.

```bash
python -i app/main.py
```

Now just import add default user and question function and execute.

```python
from app.service.user import add_default_user
from app.service.question import add_default_questions
add_default_user()
add_default_questions()
```
## Run the app

With that out of the way the app can be runned. Navigate to the app folder and run it:

```bash
fastapi run
```


---

## Container Deployment

### Podman Compose / Docker Compose

There is example `compose.yml` in the repository.

Compose file is prepared to use the bat-app:latest version of the container.

### Building the Container

Repository contains the containerfile that instructs podman how to build the container.

For that you can simply run:

```bash
podman build -f containerfile -t bat-app:<version> .
```

### Running with Compose

```bash
# Using Podman
podman-compose up

# Using Docker
docker-compose up
```

Make sure to configure environment variables in the `compose.yml` file before running.


