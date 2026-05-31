# Synchronicity - Full Stack Project

A comprehensive news processing and verification system composed of three integrated services: **Backend API**, **Search Service**, and **Frontend Dashboard**. The system handles raw reports, processes them with ML algorithms, performs image verification, and provides admin management capabilities.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
- [Backend Documentation](#backend-documentation)
- [Search Service Documentation](#search-service-documentation)
- [Frontend Documentation](#frontend-documentation)
- [Database](#database)
- [Development](#development)
- [Deployment](#deployment)

## 🎯 Project Overview

Synchronicity is an integrated platform designed to streamline news verification and processing. It consists of three main components working together:

1. **Backend API**: Core service handling report management, processing, and admin operations
2. **Search Service**: Specialized service for query optimization and reverse image search
3. **Frontend Dashboard**: User-friendly interface for members and administrators

### ✨ Key Features

- **Member Management**: Create, authenticate, and manage user members with role-based access
- **Raw Report Submission**: Accept text reports with optional image attachments and geolocation data
- **Intelligent Report Processing**: ML-powered pipeline for analyzing and summarizing reports
- **Image Verification**: Reverse image search capabilities using SerpAPI for media authenticity verification
- **Query Optimization**: Query simplification using advanced LLMs via OpenRouter API
- **Admin Dashboard**: Approve/reject processed reports and manage news templates
- **Responsive Frontend**: Modern React-based interface for both members and admins
- **Background Processing**: Asynchronous task processing for resource-intensive operations
- **Real-time Updates**: WebSocket-ready architecture for live data updates
- **API Security**: CORS support and request validation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TanStack)              │
│              Modern Dashboard & Member Interface              │
└──────────────────────┬──────────────────────┬────────────────┘
                       │                      │
          ┌────────────▼──────────────┐      │
          │    Backend API (Flask)     │◄─────┘
          │  - Report Management       │
          │  - Member Auth             │
          │  - Admin Operations        │
          │  - Database Ops            │
          └────────────┬────────────┬──┘
                       │            │
        ┌──────────────▼──┐    ┌────▼──────────────┐
        │  Search Service  │    │   PostgreSQL DB   │
        │   (Query/Images) │    │  - Members        │
        │   - Simplify     │    │  - Reports        │
        │   - Image Search │    │  - Templates      │
        └──────────────────┘    └───────────────────┘
```

## 📁 Repository Structure

```
Synchronicity/
├── backend/              # Main API Server
│   ├── main.py          # Flask app & configuration
│   ├── requirements.txt  # Python dependencies
│   ├── database/        # DB connection pooling
│   ├── handlers/        # Business logic (ML, processing, search)
│   ├── routes/          # API endpoints
│   └── README.md        # This file
│
├── search/              # Query & Image Search Service
│   ├── main.py          # Flask app
│   ├── requirements.txt  # Python dependencies
│   ├── database/        # Token management
│   ├── search/          # Search modules
│   │   ├── query.py     # Query simplification
│   │   └── image.py     # Image search
│   └── tokens.json      # API tokens storage
│
└── frontend/            # React Dashboard
    ├── src/
    │   ├── routes/      # TanStack Router pages
    │   ├── components/  # React components
    │   ├── store/       # State management
    │   ├── lib/         # Utilities & helpers
    │   ├── server.ts    # SSR server entry
    │   └── start.ts     # App initialization
    ├── package.json     # Node dependencies
    ├── vite.config.ts   # Vite configuration
    └── tsconfig.json    # TypeScript config
```

## � Technologies

### Backend & Search Services
- **Framework**: Flask 2.x
- **Database**: PostgreSQL with psycopg2 & asyncpg
- **ORM/Database Client**: Supabase
- **External APIs**: 
  - OpenRouter API (query simplification)
  - SerpAPI (image search)
- **Async Support**: asyncio, asyncpg
- **CORS**: Flask-CORS
- **Environment Management**: python-dotenv
- **HTTP Requests**: requests

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite
- **Routing**: TanStack Router v1
- **Meta-framework**: TanStack Start
- **State Management**: TanStack React Query
- **UI Components**: Radix UI (primitive components)
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form with Zod/Resolvers
- **Authentication**: Civic Auth SDK
- **TypeScript**: Full type safety
- **Deployment**: Cloudflare Workers/Pages

## 🚀 Getting Started

### Prerequisites

**For Backend & Search Services:**
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- API Keys: OpenRouter, SerpAPI

**For Frontend:**
- Node.js 18+
- npm or yarn
- Environment variables configured

### Quick Start

#### 1. Backend API

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Configure .env file (see configuration section)
python main.py
```

Server runs at `http://0.0.0.0:5000`

#### 2. Search Service

```bash
cd search
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

pip install -r requirements.txt

# Configure .env file
python main.py
```

Service runs at `http://0.0.0.0:5001` (or configured port)

#### 3. Frontend Dashboard

```bash
cd frontend
npm install

# Configure .env file with backend URL
npm run dev
```

Dev server runs at `http://localhost:24660` (or configured port)

## ⚙️ Configuration

### Backend Service (.env)

Create `.env` file in the `backend/` directory:

```env
# Flask Configuration
PORT=5000
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/synchronicity
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Search Service (.env)

Create `.env` file in the `search/` directory:

```env
# Flask Configuration
PORT=5001
DEBUG=True

# Database Configuration (same as backend)
DATABASE_URL=postgresql://username:password@localhost:5432/synchronicity

# API Keys
API_ACCESSCODE=your_api_access_code
```

Also create `search/tokens.json`:
```json
[
  { "token": "your_openrouter_token_1" },
  { "token": "your_openrouter_token_2" }
]
```

### Frontend Configuration

Create `.env` file in the `frontend/` directory:

```env
# Backend API URL
VITE_BACKEND_URL=http://ariella.hidencloud.com:24652

# Authentication
VITE_CIVIC_CLIENT_ID=your_civic_client_id
```

### Environment Variables Reference

| Service | Variable | Default | Description |
|---------|----------|---------|-------------|
| Backend | `PORT` | 5000 | Flask server port |
| Backend | `DEBUG` | True | Debug mode for development |
| Backend | `DATABASE_URL` | - | PostgreSQL connection string |
| Search | `PORT` | 5001 | Flask server port |
| Search | `API_ACCESSCODE` | - | API access code for validation |
| Frontend | `VITE_BACKEND_URL` | - | Backend API base URL |
| Frontend | `VITE_CIVIC_CLIENT_ID` | - | Civic authentication client ID |

## 🏃 Running the Application

### Development Mode

**Terminal 1 - Backend API:**
```bash
cd backend
python main.py
```
Runs at `http://0.0.0.0:5000`

**Terminal 2 - Search Service:**
```bash
cd search
python main.py
```
Runs at `http://0.0.0.0:5001`

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```
Runs at `http://localhost:24660`

### Production Mode

**Backend:**
```bash
cd backend
DEBUG=False python main.py
```

**Search Service:**
```bash
cd search
DEBUG=False python main.py
```

**Frontend:**
```bash
cd frontend
npm run build
npm run preview
```

## 📚 Backend Documentation

### Features

- **Member Management**: Create, authenticate, and manage members with role-based access
- **Raw Report Submission**: Accept text reports with optional images and geolocation
- **Report Processing**: ML-powered pipeline with automatic summarization
- **Admin Operations**: Approve/reject reports and manage templates
- **Background Tasks**: Asynchronous processing of resource-intensive operations
- **Connection Pooling**: Efficient PostgreSQL resource management

### Project Structure

```
backend/
├── main.py              # Flask app, CORS, error handlers
├── routes/              # API endpoints
│   ├── member.py        # Member login/deletion
│   ├── raw.py           # Raw report submission
│   ├── processed.py     # Processed report retrieval
│   ├── admin.py         # Admin approval operations
│   └── template.py      # Template management
├── handlers/            # Business logic
│   ├── process.py       # Processing pipeline & background tasks
│   ├── ml.py            # ML algorithms & similarity checking
│   └── search.py        # Image search integration
├── database/            # Data access layer
│   └── pool.py          # Connection pooling
└── requirements.txt
```

### API Endpoints

**Base URL:** `http://localhost:5000`

#### Health Check
```
GET / → {status: ok}
```

#### Member Operations
```
POST /member/login         # Create/authenticate member
POST /member/delete        # Delete member
```

#### Report Operations
```
POST /raw/report                    # Submit raw report
GET /processed/reports              # Get all processed reports
GET /processed/reports/<id>         # Get specific report
```

#### Admin Operations
```
POST /admin/approve                 # Approve news report
```

#### Template Management
```
GET /template/list                  # Get templates
POST /template/create               # Create new template
```

For detailed API documentation, see [backend/endpoints.md](backend/endpoints.md)

### Database Schema

- **members**: User member information
- **raw_reports**: Raw submitted reports with location and image data
- **processed_reports**: ML-processed reports with summaries
- **approved_news**: Final approved news items

## 📍 Search Service Documentation

### Features

- **Query Simplification**: Simplify complex queries using advanced LLMs
- **Image Search**: Reverse image search for media verification
- **Token Rotation**: Multi-token support with intelligent rotation
- **Token Management**: Cooldown tracking and token lifecycle management

### Project Structure

```
search/
├── main.py              # Flask app & routing
├── search/              # Search modules
│   ├── query.py         # Query simplification using OpenRouter API
│   └── image.py         # Image search using SerpAPI
├── database/            # Token management
│   ├── __init__.py
│   └── token.py         # Token storage & operations
├── requirements.txt
└── tokens.json          # OpenRouter API tokens
```

### API Endpoints

**Base URL:** `http://localhost:5001`

```
GET /                           # API documentation
POST /search/image              # Reverse image search
POST /search/query/simplify     # Simplify query
```

### External APIs Used

- **OpenRouter API**: Multi-model LLM for query simplification
- **SerpAPI**: Google Images search for image verification

### Token Management

The service supports multiple tokens for both OpenRouter and SerpAPI with:
- Automatic token rotation
- Cooldown tracking
- Token lifecycle management
- Fallback mechanisms

## 🎨 Frontend Documentation

### Features

- **Member Dashboard**: Submit reports with images and location
- **Admin Dashboard**: Review and approve processed reports
- **Modern UI**: Responsive design using Radix UI components
- **State Management**: TanStack Query for data fetching
- **Real-time Updates**: WebSocket-ready architecture
- **Authentication**: Civic-based authentication

### Project Structure

```
frontend/src/
├── routes/              # TanStack Router pages
│   ├── dashboard.*      # Member dashboard routes
│   ├── admin.*          # Admin routes
│   └── index.tsx        # Home/landing page
├── components/
│   ├── dash/            # Dashboard components
│   │   ├── AIProcessing.tsx
│   │   ├── ImageUpload.tsx
│   │   ├── Sidebar.tsx
│   │   └── ...
│   ├── site/            # Public site components
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   ├── Hero.tsx
│   │   └── ...
│   └── ui/              # Radix UI components
├── store/               # State management
│   ├── reports.ts
│   └── templates.ts
├── lib/                 # Utilities
│   ├── utils.ts
│   ├── error-capture.ts
│   └── error-page.ts
└── server.ts            # SSR server configuration
```

### Available Scripts

```bash
npm run dev              # Start development server
npm run build            # Build for production
npm run build:dev        # Build with dev mode
npm run preview          # Preview production build
npm run lint             # Run ESLint
npm run format           # Format code with Prettier
```

### Component Library

- **Radix UI**: Base components (buttons, dialogs, cards, etc.)
- **Tailwind CSS**: Utility-first styling
- **Custom Components**: Specialized dashboard components

### State Management

- **TanStack Query**: Server state and data fetching
- **React Hooks**: Local component state
- **Context API**: Shared application state

## 👨‍💻 Development

### Request Flow

```
Client Request
    ↓
Frontend (React)
    ↓
Backend API (Flask)
    ├─ Route Handler
    ├─ Request Validation
    ├─ Business Logic (Handlers)
    ├─ Database Operations
    └─ Response
    ↓
Search Service (when needed)
    ├─ Query Simplification
    ├─ Image Search
    └─ Token Management
    ↓
Client Response
```

### Key Components Interaction

1. **Frontend** → Sends requests to Backend API
2. **Backend** → Routes to appropriate handler and database
3. **Backend** → Calls Search Service for query/image operations
4. **Search Service** → Manages external API calls (OpenRouter, SerpAPI)
5. **Database** → Stores and retrieves all data

### Testing

**Backend Tests:**
```bash
cd backend
python test_admin.py
```

**Manual API Testing:**
```bash
curl http://localhost:5000/
```

### Logging & Debugging

- Werkzeug logs are suppressed (ERROR level) to reduce spam
- Enable application logging by modifying `handlers/process.py`
- Frontend console logs available in browser developer tools
- Check environment variables for API key issues

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Database connection fails | Check DATABASE_URL in .env, ensure PostgreSQL is running |
| API keys rejected | Verify OpenRouter and SerpAPI tokens in tokens.json |
| Frontend can't reach backend | Check VITE_BACKEND_URL and CORS settings |
| Image search fails | Verify SerpAPI tokens and cooldown status |
| Query simplification times out | Check OpenRouter API limits and tokens |

## 🔐 Security Considerations

### Current Implementation

- ✅ CORS support for frontend integration
- ✅ Request validation and sanitization
- ✅ Connection pooling prevents resource exhaustion
- ✅ Environment variables for sensitive data
- ✅ Error handling without exposing stack traces

### Production Recommendations

- ⚠️ Restrict CORS origins (currently `"*"`)
- ⚠️ Implement proper JWT/OAuth authentication
- ⚠️ Use HTTPS for all communications
- ⚠️ Add rate limiting on API endpoints
- ⚠️ Implement API key rotation strategy
- ⚠️ Use environment secrets management (AWS Secrets Manager, HashiCorp Vault)
- ⚠️ Enable database encryption at rest
- ⚠️ Implement request logging and monitoring
- ⚠️ Set up security headers (CSP, X-Frame-Options, etc.)
- ⚠️ Regular security audits and dependency updates

## 📊 Monitoring & Performance

### Key Metrics to Monitor

- **Backend**: Request latency, database query time, error rates
- **Search Service**: API call success rate, token availability
- **Frontend**: Page load time, API response time, user interactions
- **Database**: Connection pool usage, slow queries

### Performance Optimization

- Database query optimization with proper indexing
- Frontend code splitting and lazy loading
- API response caching strategies
- Connection pooling and reuse
- Batch operations where possible

## 🚀 Deployment

### Backend Deployment

**Using Gunicorn:**
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

**Using Docker:**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Search Service Deployment

Similar to backend, can use Gunicorn or Docker

### Frontend Deployment

**Cloudflare Pages:**
```bash
cd frontend
npm run build
# Deploy build/ directory to Cloudflare Pages
```

**Traditional Hosting:**
```bash
npm run build
# Serve dist/ folder with your preferred server
```

### Environment Setup for Deployment

Ensure all `.env` variables are set in your deployment platform:

```
Production Backend (.env):
- PORT=5000
- DEBUG=False
- DATABASE_URL=<production_db>

Production Search (.env):
- PORT=5001
- DEBUG=False
- DATABASE_URL=<production_db>
- API_ACCESSCODE=<secure_code>

Production Frontend:
- VITE_BACKEND_URL=<production_backend_url>
- VITE_CIVIC_CLIENT_ID=<production_client_id>
```

## 🔄 Continuous Integration

Recommended CI/CD pipeline:

1. **Code Push** → GitHub
2. **Tests** → Run test suite
3. **Build** → Build all services
4. **Deploy** → Deploy to staging
5. **Manual Testing** → QA verification
6. **Production Deploy** → Deploy to production

### GitHub Actions Example

```yaml
name: CI/CD
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Backend
        run: cd backend && python test_admin.py
      - name: Test Frontend
        run: cd frontend && npm test
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -am 'Add new feature'`
3. Test thoroughly across all services
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request with detailed description

### Contribution Guidelines

- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation for API changes
- Ensure all services are tested before PR
- Write clear commit messages

## 📚 Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [React Documentation](https://react.dev/)
- [TanStack Router](https://tanstack.com/router/latest)
- [Vite Documentation](https://vitejs.dev/)

### External APIs
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [SerpAPI Documentation](https://serpapi.com/docs)
- [Civic Auth Documentation](https://docs.civic.com/)
- [Supabase Documentation](https://supabase.com/docs)

### Development Tools
- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL management
- [VS Code](https://code.visualstudio.com/) - Code editor

## 📞 Support

For issues and questions:
1. Check existing issues in repository
2. Review documentation sections above
3. Create a new issue with detailed description
4. Include error logs and steps to reproduce

## 📄 License

This project is part of the Synchronicity project. All rights reserved.

---

## 📋 Quick Reference

### Port Summary
| Service | Port | URL |
|---------|------|-----|
| Backend API | 5000 | http://localhost:5000 |
| Search Service | 5001 | http://localhost:5001 |
| Frontend | 24660 | http://localhost:24660 |
| PostgreSQL | 5432 | localhost:5432 |

### Key Files
| File | Purpose |
|------|---------|
| `backend/main.py` | Backend entry point |
| `search/main.py` | Search service entry point |
| `frontend/src/start.ts` | Frontend entry point |
| `backend/requirements.txt` | Backend dependencies |
| `search/requirements.txt` | Search dependencies |
| `frontend/package.json` | Frontend dependencies |

### Common Commands
```bash
# Backend
cd backend && python main.py          # Start backend
python test_admin.py                  # Run tests

# Search
cd search && python main.py            # Start search service

# Frontend
cd frontend && npm run dev             # Start dev server
npm run build                          # Build for production
npm run lint                           # Check code
```

---

**Last Updated**: May 31, 2026
**Project Version**: 1.0.0
**Status**: Active Development
