# Penalty Management System

A Django-based penalty management system for managing people, penalties, payments, history, and rankings.

## Features

- Person management
- Membership status management
- Penalty catalog
- Issue penalties
- Pay individual or all open penalties
- Remove penalties
- Penalty history with event tracking
- Yearly penalty summaries
- Yearly and total rankings
- Role-based permissions
- HTMX-based live updates
- Comprehensive automated tests

## Tech Stack

- Python
- Django
- Django ORM
- HTMX
- pytest

## Development

Install the dependencies and run the Django development server:

```bash
python manage.py migrate
python manage.py runserver
```

Run the test suite:
```bash
pytest
```
