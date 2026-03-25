# 🏛️ Museum Exhibition Management API

A comprehensive REST API for managing museum exhibitions, artifacts, owners, and movements across Russia. Built with FastAPI and SQLAlchemy.

## 🚀 Features

- **👥 Owner Management** - Complete CRUD for artifact owners
- **🖼️ Artifact Management** - Manage museum artifacts with types and profitability
- **🏛️ Exhibition Venues** - Handle multiple exhibition locations across Russia
- **🚚 Movement Tracking** - Track artifact movements between venues
- **📊 Analytics** - Advanced analytics and business intelligence
- **🔍 SQL Query Logging** - Every response includes executed SQL queries for learning

## 🛠️ Tech Stack

- **FastAPI** - Modern, fast web framework for APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Database (easily switchable to PostgreSQL/MySQL)
- **Pydantic** - Data validation and settings management
- **Faker** - Test data generation
- **Uvicorn** - ASGI server

## 📋 API Endpoints

### 👥 Owners
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/owners/` | Get all owners |
| `GET` | `/api/v1/owners/{id}` | Get owner by ID |
| `GET` | `/api/v1/owners/{email}/wings` | Get owner's artifacts by email |

### 🖼️ Artifacts (Wings)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/wings/` | Get all artifacts |
| `GET` | `/api/v1/wings/{id}` | Get artifact by ID |
| `PUT` | `/api/v1/wings/{id}` | Update artifact information |

### 🏛️ Exhibition Venues
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/places/` | Get all exhibition venues |
| `GET` | `/api/v1/places/{id}` | Get venue by ID |

### 🚚 Movements
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/moves/` | Get all movements |
| `POST` | `/api/v1/moves/` | Create new movement |
| `DELETE` | `/api/v1/moves/{id}` | Delete movement |

### 🏷️ Artifact Types
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/types/` | Get all artifact types |
| `GET` | `/api/v1/types/{id}` | Get type by ID |

### 📊 Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/analytics/owner-most-wings` | Owner with most artifacts |
| `GET` | `/api/v1/analytics/most-expensive-wing` | Most expensive artifact movement |
| `GET` | `/api/v1/analytics/most-profitable-wing` | Most profitable artifact |
| `GET` | `/api/v1/analytics/most-profitable-place` | Most profitable venue |
| `GET` | `/api/v1/analytics/most-popular-type` | Most popular artifact type |
| `GET` | `/api/v1/analytics/wing-move-frequency/{id}` | Artifact movement frequency |

## 🗄️ Database Schema

```sql
owners (id, email, first_name, last_name, middle_name, birth_date)
types (id, name)
wings (id, owner_id, type_id, profit, name)
places (id, location, scale)
moves (id, wing_id, place_id, price, dt)
```

## 🚀 Quick Start Guide

### Step 1: Clone and Setup
```bash
git clone <repository-url>
cd museum-api
python -m venv .venv

# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
```
### Step 2: Install requirements
```bash
pip install -r requirements.txt
```

### Step 3: Run application
```bash
python run.py
```

