# Test Application

A sample application for testing Engram's indexing capabilities.

## Features

- User authentication with session tokens
- SQLite database for data persistence
- RESTful API for frontend communication
- Posts management (CRUD operations)

## Architecture

The application follows a layered architecture:

1. **Frontend** (JavaScript) - Handles user interactions
2. **API Layer** - RESTful endpoints
3. **Business Logic** (Python) - Core application logic
4. **Database** (SQLite) - Data persistence

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- SQLite3

### Installation

```bash
pip install -r requirements.txt
npm install
```

### Running

```bash
python app.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/login | User login |
| POST | /auth/logout | User logout |
| GET | /auth/me | Get current user |
| GET | /posts | List all posts |
| POST | /posts | Create a post |
| PUT | /posts/:id | Update a post |
| DELETE | /posts/:id | Delete a post |

## Security

- Passwords are hashed using SHA-256 with salt
- Session tokens expire after 24 hours
- All API endpoints require authentication (except login)
