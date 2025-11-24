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

### Persistent Storage on Railway

**Important:** Railway uses ephemeral storage by default. For production use:

1. Go to your Railway project settings
2. Add a **Volume** to persist:
   - Database files: Mount at `/bat-app/app/db`
   - Uploaded files: Mount at `/bat-app/app/uploads`

### Updating Your Deployment

Railway automatically redeploys when you push to your connected GitHub branch:

```bash
git add .
git commit -m "Update application"
git push origin main
```

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


