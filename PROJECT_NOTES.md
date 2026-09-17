# Project Engineering Notes

## Business Goal

Provide a centralized SaaS-style workspace for customer service and operational issue management.

## Core User Stories

- As an employee, I can create a support ticket for a customer.
- As a manager, I can assign tickets and change their priority.
- As a user, I can search and filter support tickets.
- As an administrator, I can manage customer records.
- As an engineer, I can query operational data through REST APIs.
- As a maintainer, I can run automated tests before releasing changes.

## Non-Functional Goals

- Secure password storage
- Clear separation between routes and data models
- Relational data integrity
- Environment-based configuration
- Testable API behavior
- Production-ready WSGI entry point
- Containerized deployment option
- Cloud deployment path

## Future Engineering Work

- Alembic/Flask-Migrate database migrations
- CSRF protection for production forms
- Token-based API authentication
- Rate limiting
- Structured JSON logging
- SLA and response-time metrics
- Email notifications
- CI/CD deployment pipeline
