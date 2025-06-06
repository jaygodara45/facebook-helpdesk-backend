# Facebook Helpdesk API

A FastAPI-based backend service that provides a helpdesk interface for managing Facebook page messages and conversations.

## Features

- User Authentication (Register/Login)
- Facebook Page Integration
- Real-time Message Handling
- Conversation Management
- Secure API Endpoints

## Prerequisites

- Python 3.8+
- PostgreSQL
- Facebook Developer Account with an App
- Node.js and npm (for frontend)

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/jaygodara45/facebook-helpdesk-backend.git
cd facebook-helpdesk-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:

```env
# Project Information
PROJECT_NAME="Facebook Helpdesk API"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# Security
SECRET_KEY="your-super-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# PostgreSQL Database
POSTGRES_SERVER="localhost"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"
POSTGRES_DB="facebook_helpdesk"
POSTGRES_PORT="5432"

# Facebook App Configuration
FACEBOOK_APP_ID="your-facebook-app-id"
FACEBOOK_APP_SECRET="your-facebook-app-secret"
FACEBOOK_VERIFY_TOKEN="your-webhook-verify-token"
```

5. Initialize the database:
```bash
# Make sure PostgreSQL is running and create the database
createdb facebook_helpdesk
```

6. Start the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Environment Variables Explanation

### Project Configuration
- `PROJECT_NAME`: Name of the project displayed in API documentation
- `VERSION`: API version number
- `API_V1_STR`: Base path for API version 1 endpoints

### Security Configuration
- `SECRET_KEY`: Used for JWT token generation and encryption (must be kept secret)
- `ALGORITHM`: The algorithm used for JWT token generation (HS256 is default)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Duration in minutes for which the JWT token remains valid

### Database Configuration
- `POSTGRES_SERVER`: Hostname of the PostgreSQL server
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: Name of the database
- `POSTGRES_PORT`: Port number for PostgreSQL server

### Facebook Integration
- `FACEBOOK_APP_ID`: Your Facebook Application ID from Facebook Developers Console
- `FACEBOOK_APP_SECRET`: Your Facebook Application Secret (keep this secure)
- `FACEBOOK_VERIFY_TOKEN`: Custom token for Facebook Webhook verification

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Development

The project uses FastAPI with the following structure:
- `app/main.py`: Application entry point
- `app/core/`: Core configurations and utilities
- `app/api/`: API routes and endpoints
- `app/models/`: Database models
- `app/schemas/`: Pydantic models for request/response validation
- `app/services/`: Business logic and services