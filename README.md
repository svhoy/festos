# Penalty Management System

A Django-based penalty management system for managing members, penalties, payments, penalty history, and rankings.

The project is currently at **MVP v1** and focuses on the core workflows needed to manage penalties in a simple and transparent way.

## Features

### People

- Create and manage people
- Track membership status:
  - Active
  - Passive
  - Left
- View an individual person's penalty information

### Penalties

- Issue penalties from an active penalty catalog
- View open penalties
- View the current outstanding penalty balance
- Pay individual penalties
- Pay all open penalties at once
- Remove penalties when permitted
- Keep a complete penalty history

Penalty events are tracked separately, including:

- Issued
- Paid
- Removed
- Amount changed

Removed penalties remain visible in the history but are excluded from financial totals and rankings.

### Yearly Overview

The person detail page provides yearly penalty totals.

This makes it possible to see how much penalty volume a person accumulated in each year.

### Rankings

The application provides two rankings:

#### Yearly Ranking

Shows the total amount of penalties issued during a selected year.

Both paid and currently open penalties count toward the ranking.

Removed penalties are ignored.

#### Overall Ranking

Shows the total penalty amount across all years.

Again:

- Paid penalties count
- Open penalties count
- Removed penalties do not count

### HTMX / Live Updates

The person detail page uses HTMX to update penalty-related sections without requiring a full page reload.

After issuing, paying, or removing a penalty, the relevant sections are updated automatically:

- Outstanding penalty balance
- Yearly penalty totals
- Open penalties
- Penalty history

Out-of-band (`hx-swap-oob`) updates are used to keep all sections synchronized.

## Tech Stack

- Python
- Django
- Django ORM
- SQLite/PostgreSQL depending on environment
- HTML / Django Templates
- HTMX
- pytest
- pytest-django

## Project Structure

The project is split into several Django applications:

```text
accounts/
    Authentication, roles and permissions

people/
    People and membership management

penalties/
    Penalty catalog, penalties, payments and history

ranking/
    Yearly and overall rankings

tests/
    Automated test suite
