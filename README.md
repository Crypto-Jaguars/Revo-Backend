# Revo Backend

A modern FastAPI backend application with GraphQL support, SQLAlchemy, and PostgreSQL.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **GraphQL** - Query language with Strawberry GraphQL
- **SQLAlchemy** - SQL toolkit and ORM with async support
- **PostgreSQL** - Advanced open source relational database
- **Docker** - Containerization for development and deployment
- **Alembic** - Database migration tool
- **Pytest** - Testing framework with async support

## Features

- 🚀 **High Performance**: FastAPI with async/await support
- 🔍 **GraphQL API**: Flexible query language with Strawberry
- 🗄️ **Database**: PostgreSQL with SQLAlchemy ORM
- 🐳 **Docker Ready**: Full containerization setup
- 🧪 **Testing**: Comprehensive test suite with pytest
- 📝 **Auto Documentation**: Interactive API docs with Swagger/ReDoc
- 🔧 **Developer Tools**: Code formatting, linting, and type checking

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### Quick Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Revo-Backend
   ```

2. **Run the setup script:**

   ```bash
   make setup
   ```

3. **Start the database:**

   ```bash
   make docker-up
   ```

4. **Create and run migrations:**

   ```bash
   make migration name="initial"
   make migrate
   ```

5. **Start the application:**
   ```bash
   make run
   ```

The API will be available at:

- **REST API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
Revo-Backend/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI application setup
│   ├── core/                    # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic settings
│   │   └── database.py         # SQLAlchemy async setup
|   |   └── dependencies.py     # Dependencies for JWT middleware
|   |   └── security.py         # JWT middleware
│   ├── models/                 # SQLAlchemy models (modular by domain)
│   │   ├── __init__.py         # Centralized model imports
│   │   ├── base.py            # Base model class
│   │   ├── users/             # User domain models
│   │   │   ├── __init__.py
│   │   │   └── user.py        # User authentication
│   │   ├── farmers/           # Farmer domain models
│   │   │   ├── __init__.py
│   │   │   ├── farmer.py      # Farmer profiles
│   │   │   └── verification.py # Farm verification system
│   │   ├── products/          # Product domain models
│   │   │   ├── __init__.py
│   │   │   └── product.py     # Agricultural products
│   │   ├── orders/            # Order domain models
│   │   │   ├── __init__.py
│   │   │   └── order.py       # Orders and order items
│   │   └── shared/            # Shared models
│   │       ├── __init__.py
│   │       └── location.py    # Geographic locations
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py           # User DTOs
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py   # User operations
│   ├── graphql/              # GraphQL schema and resolvers
│   │   ├── __init__.py
│   │   ├── schema.py         # Main GraphQL schema
│   │   ├── types/            # GraphQL types
│   │   │   ├── __init__.py
│   │   │   └── user_type.py  # User GraphQL types
│   │   └── resolvers/        # GraphQL resolvers
│   │       ├── __init__.py
│   │       └── user_resolver.py # User operations
│   └── api/                  # REST API endpoints
│       ├── __init__.py
│       └── health.py         # Health check endpoints
├── tests/                    # Test suite
│   ├── __init__.py
│   └── conftest.py          # Test configuration
│   └── test_auth.py         # Auth tests
├── alembic/                 # Database migrations
│   ├── env.py              # Alembic environment
│   ├── script.py.mako      # Migration template
│   └── versions/           # Migration files
├── scripts/                 # Utility scripts
│   ├── setup.sh            # Setup script
│   └── start.sh            # Start script
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
├── docker-compose.yml     # Docker services
├── Dockerfile            # Application container
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Python project configuration
├── alembic.ini          # Alembic configuration
├── Makefile            # Development commands
├── CONTRIBUTING.md     # Contribution guidelines
└── PROJECT_OVERVIEW.md # Project documentation
```

## Available Commands

Use the Makefile for common development tasks:

```bash
make help          # Show all available commands
make setup         # Initial project setup
make run           # Start the application
make test          # Run tests with coverage
make lint          # Run code linting
make format        # Format code with black and isort
make docker-up     # Start services with Docker
make docker-down   # Stop Docker services
make migration     # Create database migration
make migrate       # Apply database migrations
```

## GraphQL Examples

### Query Users

```graphql
query {
  users {
    id
    email
    username
    isActive
    createdAt
  }
}
```

### Create User

```graphql
mutation {
  createUser(
    userInput: {
      email: "user@example.com"
      username: "newuser"
      password: "securepassword"
    }
  ) {
    id
    email
    username
  }
}
```

## Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Key environment variables:

- `ENVIRONMENT` - Application environment (development/production)
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key for authentication
- `ALLOWED_ORIGINS` - CORS allowed origins

## Testing

Run the test suite:

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/test_main.py -v

# Run tests with coverage report
pytest --cov=app --cov-report=html tests/
```

## Development

### Local Development (without Docker)

1. **Setup virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. **Setup database and run migrations:**

   ```bash
   # Start PostgreSQL (adjust for your setup)
   # Then run migrations
   alembic upgrade head
   ```

4. **Start the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Code Quality

The project includes several tools for maintaining code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pytest** - Testing framework

Run all quality checks:

```bash
make lint
make format
make test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
