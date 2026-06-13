# CampusX : Campus Event Manager Platform

A web-based event management platform developed using **FastAPI**, **SQLAlchemy**, **Jinja2 Templates**, and **SQLite**. The system streamlines campus event organization by providing role-based access for Administrators, Volunteers, and Participants.

---

# Overview

Campus Event Manager is designed to simplify the planning, coordination, and execution of campus events. The platform enables administrators to create and manage events, assign tasks to volunteers, publish announcements, and monitor registrations. Participants can browse events and register for them, while volunteers can view and manage assigned tasks.

---

# Features

## User Management

* User Registration
* User Login and Logout
* Secure Password Hashing using bcrypt
* JWT-based Authentication
* Role-Based Access Control (RBAC)

### Supported Roles

* Administrator
* Volunteer
* Participant

---

## Event Management

Administrators can:

* Create Events
* Edit Event Details
* Delete Events
* Manage Event Capacity
* Categorize Events
* Track Event Status

---

## Registration Management

Participants can:

* View Available Events
* Register for Events

Administrators can:

* View All Registrations
* Monitor Participation Metrics

---

## Volunteer Task Management

Administrators can:

* Create Tasks
* Assign Tasks to Volunteers
* Monitor Task Progress

Volunteers can:

* View Assigned Tasks
* Track Task Status

---

## Announcement System

Administrators can:

* Create Announcements
* Publish Event Updates
* Share Event Information

Participants and Volunteers can:

* View Announcements

---

## Dashboard Analytics

### Administrator Dashboard

Displays:

* Total Events
* Total Tasks
* Total Registrations
* Pending Tasks

### Volunteer Dashboard

Displays:

* Assigned Tasks
* Pending Tasks
* Confirmed Tasks
* Registration Overview

### Participant Dashboard

Displays:

* Personal Registration Count

---

# Technology Stack

## Backend

* FastAPI
* Python 3.x

## Database

* SQLite
* SQLAlchemy ORM

## Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

## Authentication

* JWT (JSON Web Tokens)
* Passlib (bcrypt)

---

# System Architecture

```text
+-------------------+
|      Browser      |
+-------------------+
          |
          v
+-------------------+
|     FastAPI       |
|  Application API  |
+-------------------+
          |
          v
+-------------------+
| Authentication    |
| Authorization     |
+-------------------+
          |
          v
+-------------------+
| SQLAlchemy ORM    |
+-------------------+
          |
          v
+-------------------+
| SQLite Database   |
+-------------------+
```

---
## Entity Relationship Diagram

```mermaid
erDiagram

    USERS {
        int id PK
        string name
        string email
        string password
        string role
        datetime created_at
    }

    EVENTS {
        int id PK
        string title
        text description
        string venue
        string date
        string time
        int capacity
        string category
        string status
        int created_by FK
    }

    REGISTRATIONS {
        int id PK
        int user_id FK
        int event_id FK
    }

    TASKS {
        int id PK
        string title
        text description
        string status
        int event_id FK
        int volunteer_id FK
        datetime created_at
    }

    ANNOUNCEMENTS {
        int id PK
        string title
        text content
        int event_id FK
        int created_by FK
        datetime created_at
    }

    USERS ||--o{ REGISTRATIONS : registers
    EVENTS ||--o{ REGISTRATIONS : contains

    USERS ||--o{ TASKS : assigned_to
    EVENTS ||--o{ TASKS : includes

    USERS ||--o{ ANNOUNCEMENTS : creates
    EVENTS ||--o{ ANNOUNCEMENTS : related_to
```
---

# Database Entities

The system consists of the following entities:

### Users

Stores user information and role details.

### Events

Stores event information and scheduling details.

### Registrations

Tracks participant registrations for events.

### Tasks

Manages volunteer assignments.

### Announcements

Stores event and system announcements.

---

# Project Structure

```text
app/
│
├── main.py
├── auth.py
├── database.py
├── models.py
│
├── routers/
│   ├── events.py
│   ├── registrations.py
│   ├── tasks.py
│   └── announcements.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── ...
│
└── static/
    ├── style.css
    └── main.js
```

---

# Installation Guide

## 1. Clone Repository

```bash
git clone <repository-url>
cd campus-event-manager
```

## 2. Create Virtual Environment

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Application

```bash
uvicorn app.main:app --reload
```

---

## 5. Open Application

```text
http://127.0.0.1:8000
```

---

# User Workflow

## Administrator

1. Login
2. Create Events
3. Assign Volunteer Tasks
4. Publish Announcements
5. Monitor Registrations

## Volunteer

1. Login
2. View Assigned Tasks
3. Track Task Status
4. Access Event Information

## Participant

1. Register Account
2. Browse Events
3. Register for Events
4. View Event Updates

---

# Security Features

* Password Hashing with bcrypt
* JWT Authentication
* HTTP-Only Cookies
* Role-Based Authorization
* Protected Dashboard Access

---

# Future Enhancements

* Email Notifications
* Event Attendance Tracking
* QR Code Check-In
* Calendar Integration
* Advanced Reporting Dashboard
* Real-Time Notifications
* PostgreSQL Support
* Cloud Deployment

---

# Learning Outcomes

This project demonstrates:

* FastAPI Application Development
* RESTful Routing
* SQLAlchemy ORM Integration
* Authentication and Authorization
* Database Design
* Template Rendering with Jinja2
* CRUD Operations
* Role-Based Access Control

---

# Author

Developed as a full-stack web application for managing campus events, volunteer coordination, participant registrations, and event communication.

---

# License

This project is intended for educational and academic purposes.
