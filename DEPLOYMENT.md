# Deployment Guide

## Local PostgreSQL with Docker

Install Docker Desktop, then from the project root:

```bash
docker compose up --build
```

Open `http://localhost:5000`.

## AWS EC2 + PostgreSQL

Recommended production architecture:

```text
Browser
   |
HTTPS / Domain
   |
AWS EC2
   |
Nginx -> Gunicorn -> Flask
   |
AWS RDS for PostgreSQL
```

High-level steps:

1. Create an AWS EC2 instance.
2. Install Python, Nginx and Git.
3. Clone the repository.
4. Create a Python virtual environment.
5. Install `requirements.txt`.
6. Create an AWS RDS PostgreSQL database.
7. Set `DATABASE_URL` and `SECRET_KEY` as environment variables.
8. Start Gunicorn as a system service.
9. Configure Nginx as a reverse proxy.
10. Add HTTPS using an appropriate certificate.
11. Verify `/health`, login, database operations and API endpoints.

Do not commit passwords, API keys, database credentials, or `.env` files to GitHub.
