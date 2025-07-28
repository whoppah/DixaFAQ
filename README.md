# DixaFAQ

The **DixaFAQ** backend service is built with Django and Django REST Framework. It provides APIs for message ingestion, FAQ management, clustering, embedding, and pipeline orchestration using Celery.

---

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Environment Variables](#environment-variables)
5. [Configuration](#configuration)
6. [Database Migrations & Admin Setup](#database-migrations--admin-setup)
7. [Running Locally](#running-locally)
8. [Docker Setup](#docker-setup)
9. [Celery & Scheduled Tasks](#celery--scheduled-tasks)
10. [Management Commands](#management-commands)
11. [API Endpoints](#api-endpoints)

---

## Features

* RESTful API for:

  * Messages
  * FAQs
  * Cluster runs & results
* Automated pipeline:

  * Download from Dixa & Elevio
  * Preprocess, embed, and match messages
  * Cluster and summarize issues
  * Cache dashboard data
* Celery & Redis for background tasks and scheduling
* PostgreSQL database support via `dj-database-url`
* Admin UI for manual inspection and management

---

## Prerequisites

* Python 3.12
* PostgreSQL (or compatible) database
* Redis for Celery broker & cache
* \[Optional] Docker & Docker Compose

---

## Installation

1. Clone this repository:

   ```bash
   git clone <repository_url> backend
   cd backend
   ```

2. Install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```dotenv
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@host:port/dbname
REDIS_URL=redis://localhost:6379/0

# API Credentials
JINA_API_KEY=
DIXA_API_TOKEN=
ELEVIO_API_KEY=
ELEVIO_JWT=
GROQ_API_KEY=
GOOGLE_CREDENTIALS_JSON=<json-credentials>
GCS_BUCKET_NAME=

# Admin user setup
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=
```

---

## Configuration

All settings are in `config/settings.py`. Adjust:

* `ALLOWED_HOSTS` & `CSRF_TRUSTED_ORIGINS`
* Database settings via `DATABASE_URL`
* Time zone (`Europe/Amsterdam`)
* CORS origins

---

## Database Migrations & Admin Setup

Apply migrations and create superuser:

```bash
python manage.py migrate
python manage.py createadmin  # creates superuser using ADMIN_ env vars
```

---

## Running Locally

Start the development server:

```bash
python manage.py runserver 8080
```

The API will be available at `http://localhost:8080/api/faq/`.

---

## Docker Setup

Build and run the Docker container:

```bash
cd backend
docker build -t dixafaq-backend .
docker run -d \
  --env-file .env \
  -p 8080:8080 \
  dixafaq-backend
```

---

## Celery & Scheduled Tasks

Start Celery worker & beat:

```bash
celery -A faq_api worker --loglevel=info
celery -A faq_api beat --loglevel=info
```

A weekly pipeline job is scheduled (Friday at 14:58 UTC).

---

## Management Commands

* `createadmin`: Create/update admin user
* `download_dixa_elevio`: Download Dixa messages & Elevio FAQs
* `process_and_embed`: Preprocess messages & embed via OpenAI

List all commands:

```bash
python manage.py help
```

---

## API Endpoints

Base URL: `/api/faq/`

| Endpoint                             | Method | Description                            |
| ------------------------------------ | ------ | -------------------------------------- |
| `/messages/`                         | GET    | List & search messages                 |
| `/faqs/`                             | GET    | List & search FAQs                     |
| `/cluster-runs/`                     | GET    | List cluster pipeline runs             |
| `/cluster-results/`                  | GET    | List clustering results                |
| `/cluster-results/export/`           | GET    | Export cluster results as CSV          |
| `/clusters/`                         | GET    | Cached clusters & map                  |
| `/dashboard-clusters-with-messages/` | GET    | Dashboard clusters + sample messages   |
| `/trending-leaderboard/`             | GET    | Trending question keywords leaderboard |
| `/deflection-metrics/`               | GET    | FAQ performance trends                 |
| `/top-process-gaps/`                 | GET    | Top process gap topics                 |
| `/trigger-pipeline/`                 | POST   | Manually trigger pipeline (admin only) |
| `/current-user-info/`                | GET    | Info on authenticated user             |


