# Spatial Data Platform

## Overview

This is a backend spatial data platform designed to store, update, and retrieve spatial data including points and polygons. The project supports geographical data management with PostGIS integration.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- PostgreSQL 12+
- PostGIS extension
- pip (Python package manager)
- Homebrew (for macOS users)

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/svspavankumarspatial_data_platform.gitcd 

cd spatial_data_platform
```

### 2. Environment Setup

#### Install System Dependencies (macOS)
```bash
brew install postgis
brew install postgresql
```

#### Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Database Configuration

#### Create PostgreSQL Database
```bash
createdb spatial_data_platform
```

#### Enable PostGIS Extension
```sql
CREATE EXTENSION postgis;
```

### 4. Database Tables

Run the following SQL queries to create necessary tables:

```sql
CREATE TABLE points (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    description TEXT
);

CREATE TABLE polygons (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    shape GEOGRAPHY(POLYGON, 4326),
    population_density FLOAT
);
```

### 5. Environment Configuration

Create a `.env` file in the project root with the following variables:

```
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spatial_data
```

### 6. Running the Application

```bash
uvicorn main:app --reload
```

## API Endpoints

### Points Endpoints
- `POST /points`: Create a new point
- `GET /points`: Retrieve all points
- `GET /points/{id}`: Retrieve a specific point
- `PUT /points/{id}`: Update a point
- `DELETE /points/{id}`: Delete a point

### Polygon Endpoints
- `POST /polygons`: Create a new polygon
- `GET /polygons`: Retrieve all polygons
- `GET /polygons/{id}`: Retrieve a specific polygon
- `PUT /polygons/{id}`: Update a polygon
- `DELETE /polygons/{id}`: Delete a polygon
