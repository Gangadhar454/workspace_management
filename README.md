# Virtual Workspace Room Booking System

## Overview
This is a Django-based RESTful API for managing workspace room bookings, cancellations, and availability. It supports private rooms, conference rooms, and shared desks with specific allocation rules and concurrency handling.

## Setup Instructions

### Prerequisites
- Docker
- Docker Compose

### Running the Application
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd workspace_management
   ```
2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000/api/v1/`.
4. Access the Django admin interface at `http://localhost:8000/admin/` (create a superuser with `python manage.py createsuperuser`).

### API Endpoints
- **POST /api/v1/bookings/create/**: Book a room.
- **POST /api/v1/cancel/{booking_id}/**: Cancel a booking.
- **GET /api/v1/bookings/**: List all bookings.
- **GET /api/v1/rooms/available/?start_time=YYYY-MM-DDTHH:MM:SSZ**: Check room availability.

### Database Schema
- **Users**: Stores user details (name, age, gender).
- **Teams**: Stores team details with many-to-many user relationships.
- **TeamMembers**: Links users to teams, tracks if a member is a child.
- **Rooms**: Stores room details (type, capacity).
- **Bookings**: Tracks bookings with room, user/team, and time slot.

### Design Decisions
- **Normalization**: Used a normalized schema for clarity and to avoid data duplication. The `TeamMember` model handles the many-to-many relationship with child tracking.
- **Concurrency**: Uses `select_for_update()` to lock rooms during booking to prevent race conditions.
- **Validation**: Enforces business rules (e.g., conference rooms for teams of 3+, no overlapping bookings) in serializers and views.
- **Docker**: Uses a multi-container setup with PostgreSQL and Gunicorn for production-like deployment.

### Testing
Run tests with:
```bash
docker-compose exec web python manage.py test
```

### Bonus Features
- **Tests**: Includes unit tests for core functionality.
