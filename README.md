# Cloud Business Support & Service Management Platform

**Version 2.0 — Engineering Prototype**

A professional, cloud-ready business support SaaS prototype built around the technology requirements of a modern R&D web development team.

## Purpose

The platform centralizes customer information and support operations. Employees can manage customers, create and assign support tickets, update priorities and statuses, add internal comments, and view operational dashboard metrics.

## Technology

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- PostgreSQL (production-ready configuration)
- SQLite (zero-setup local demo)
- HTML / CSS
- REST API
- Git / GitHub
- AWS-ready deployment configuration

## Features

- Role-based user accounts
- Secure password hashing
- Customer CRUD
- Customer search
- Support ticket creation and assignment
- Ticket priority and status workflow
- Internal ticket comments
- Dashboard metrics
- Ticket filtering
- REST API for tickets and dashboard statistics
- Activity logging
- Automated tests with pytest
- PostgreSQL-ready configuration
- Responsive interface

## Local Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

### Demo credentials

- Admin: `admin@example.com` / `Admin@123`
- Manager: `manager@example.com` / `Manager@123`
- Employee: `employee@example.com` / `Employee@123`

Change these credentials and `SECRET_KEY` before any real deployment.

## PostgreSQL

Set an environment variable:

```text
DATABASE_URL=postgresql+psycopg://username:password@host:5432/business_support
```

The application automatically uses that database when `DATABASE_URL` is present.

## API Examples

Authenticated requests:

```text
GET  /api/dashboard
GET  /api/tickets
GET  /api/tickets?status=Open
POST /api/tickets
```

Example JSON for ticket creation:

```json
{
  "title": "Unable to access monthly report",
  "description": "Customer cannot download the report.",
  "priority": "High",
  "customer_id": 1
}
```

## Testing

```bash
pytest
```

## Suggested Git Workflow

Use feature branches for development:

```text
main
  ├── feature/authentication
  ├── feature/customer-management
  ├── feature/ticket-api
  ├── feature/dashboard
  └── fix/ticket-validation
```

## AWS Deployment Plan

A production deployment can use:

```text
User
  |
AWS EC2 / Application Server
  |
Gunicorn + Flask
  |
PostgreSQL (Amazon RDS)
```

For a production release, add HTTPS, environment-based secrets, database migrations, monitoring, backups, and a production WSGI server.

## Development Lifecycle Demonstrated

1. Requirements definition
2. Database and screen design
3. Backend implementation
4. API development
5. Frontend implementation
6. Validation and error handling
7. Testing
8. Git-based version control
9. Cloud deployment preparation
10. Maintenance and feature enhancement

## Future Enhancements

- Email notifications
- SLA tracking
- File attachments
- Customer self-service portal
- Advanced analytics
- Audit log UI
- Docker deployment
- CI/CD with GitHub Actions
- AWS RDS + EC2 production deployment
- Role-specific permissions


## Engineering Features Added in Version 2

- Environment-based configuration
- PostgreSQL support through `DATABASE_URL`
- Role-based authorization
- REST API error handling
- `/health` operational endpoint
- Pytest test suite
- Docker and Docker Compose support
- Gunicorn production server configuration
- GitHub Actions CI workflow
- AWS EC2 + RDS deployment guide
- API documentation

## Recommended Development Lifecycle

Use GitHub Issues for requirements and defects, feature branches for changes, pull requests for review, CI for automated tests, and small commits that describe one logical change.
