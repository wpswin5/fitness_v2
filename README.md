# Fitness API

A modern FastAPI service for fitness tracking with Azure SQL Database backend, deployed via GitHub Actions.

## Features

- ✅ FastAPI REST API with async support
- ✅ Azure SQL Database integration
- ✅ Docker containerization
- ✅ GitHub Actions CI/CD pipeline
- ✅ Infrastructure as Code (Bicep)
- ✅ Database migrations
- ✅ Comprehensive test coverage
- ✅ Security best practices (Managed Identity, RBAC)

## Quick Start

### Local Development

```bash
# Setup
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp ../.env.example .env
# Edit .env with your values

# Run
python -m uvicorn main:app --reload

# Test
pytest tests/ -v
```

API will be available at `http://localhost:8000`

## Project Structure

```
fitness_v2/
├── .github/workflows/       # CI/CD pipelines
├── app/                     # FastAPI application
│   ├── src/
│   │   ├── api/            # Route handlers
│   │   ├── models/         # Data models
│   │   ├── db/             # Database utilities
│   │   └── config.py       # Configuration
│   ├── tests/              # Test suite
│   ├── Dockerfile          # Container image
│   └── requirements.txt     # Python dependencies
├── database/               # Azure SQL Database
│   ├── migrations/         # SQL migration scripts
│   ├── bicep/              # Infrastructure templates
│   └── scripts/            # Deployment scripts
├── docs/                   # Documentation
│   ├── DEPLOYMENT.md       # Deployment guide
│   └── SECRETS_SETUP.md    # Security setup
└── .env.example            # Example environment variables
```

## Documentation

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Comprehensive deployment guide
- **[SECRETS_SETUP.md](docs/SECRETS_SETUP.md)** - GitHub Secrets configuration
- **[database/README.md](database/README.md)** - Database project details

## Deployment

### Prerequisites

1. Azure subscription
2. GitHub repository
3. Configured GitHub Secrets (see [SECRETS_SETUP.md](docs/SECRETS_SETUP.md))

### Automatic (GitHub Actions)

Push to `main` branch:
```bash
git push origin main
```

Pipeline automatically:
1. Runs tests
2. Deploys database infrastructure
3. Runs migrations
4. Builds Docker image
5. Pushes to Azure Container Registry
6. Deploys container to Azure

### Manual

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for manual deployment steps.

## API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Workouts
```bash
GET /api/v1/workouts          # List all workouts
POST /api/v1/workouts         # Create workout
```

## Development

### Running Tests
```bash
cd app
pytest tests/ -v --cov=src
```

### Code Quality
```bash
# Lint
pylint src/

# Type checking
mypy src/
```

## Architecture

- **Framework**: FastAPI (async Python web framework)
- **Database**: Azure SQL Database (managed relational DB)
- **Container**: Docker (multi-stage builds)
- **Orchestration**: Azure Container Instances
- **CI/CD**: GitHub Actions
- **IaC**: Bicep (Azure infrastructure language)

## Security Features

- ✅ Service Principal authentication
- ✅ Azure Managed Identity support
- ✅ Database connection encryption
- ✅ CORS configuration
- ✅ Non-root container user
- ✅ GitHub Secrets for sensitive data
- ✅ Role-based access control (RBAC)

## License

MIT

## Support

For issues and questions, please open a GitHub issue.