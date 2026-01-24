# 🧳 Travel Readiness Sentinel

> **An intelligent API that validates travel itineraries to prevent booking errors**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-53%20Passing-brightgreen.svg)](tests/)

---

## 💡 What Does This Do?

Ever booked a flight that departs **before** your hotel checkout? Or arrived at your destination **after** your hotel check-in time? This API automatically catches these mistakes **before** you book.

**Real-world problem it solves:**
- ✅ Validates flight dates match hotel reservations
- ✅ Ensures your hotel covers your entire trip
- ✅ Checks you have a flight home on your last day
- ✅ Prevents costly booking errors

---

## 🎯 Why I Built This

This project demonstrates my ability to build **production-ready backend systems** with:
- Modern Python web frameworks (FastAPI)
- RESTful API design
- Docker containerization
- Automated testing
- Production observability (logging, metrics)
- Clean code architecture

---

## 📸 See It In Action

### Interactive API Documentation
![API Documentation](.github/images/validation-success.png)
*Swagger UI with automatic validation and request tracing*

### Real-Time Monitoring
![Metrics Dashboard](.github/images/metrics-endpoint.png)
*Prometheus metrics for production monitoring*

---

## 🚀 Quick Start

### Try It Yourself (2 minutes)

```bash
# 1. Clone and start with Docker
git clone https://github.com/harveycyl/travel-readiness-sentinel.git
cd travel-readiness-sentinel
docker-compose up

# 2. Open your browser
open http://localhost:8000/docs

# 3. Try the /validate endpoint with sample data
```

That's it! The interactive docs let you test the API directly in your browser.

---

## 🔗 Notion Integration (Optional)

**Export validation results to Notion pages automatically!**

This feature demonstrates third-party API integration skills by exporting your travel check results to beautifully formatted Notion pages.

### Setup Instructions

1. **Create a Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Click **"+ New integration"**
   - Give it a name (e.g., "Travel Sentinel")
   - Select your workspace
   - Click **"Submit"**
   - Copy the **"Internal Integration Token"** (starts with `secret_`)

2. **Create or Choose a Notion Page**
   - Open Notion and create a new page (or use an existing one)
   - This will be the parent page where all your travel check exports will appear

3. **Share the Page with Your Integration**
   - Open your Notion page
   - Click the **"Share"** button (top right)
   - Click **"Invite"**
   - Find your integration name in the dropdown and select it
   - Click **"Invite"**

4. **Get the Page ID**
   - The page ID is in the URL. For example:
   - URL: `https://www.notion.so/My-Travel-Checks-abc123def456?v=...`
   - Page ID: `abc123def456` (the part after the last dash before `?`)

5. **Configure Your Environment**
   ```bash
   # Copy the example env file if you haven't already
   cp .env.example .env
   
   # Edit .env and add your credentials:
   # NOTION_API_TOKEN=secret_YOUR_TOKEN_HERE
   # NOTION_PAGE_ID=abc123def456
   ```

### Usage

Once configured, use the `/export/notion` endpoint instead of `/validate`:

```bash
curl -X POST "http://localhost:8000/export/notion" \
  -H "Content-Type: application/json" \
  -d @examples/valid_full_example.yaml.json
```

**Response includes:**
- All standard validation results
- `notion_url`: Direct link to your created Notion page
- `notion_page_id`: ID of the page
- `exported_at`: Export timestamp

**What gets exported:**
- ✅/❌ Validation status with emojis
- Trip destination and summary
- Detailed check results in color-coded callouts
- Timestamp for tracking

---

---

## 🔒 Security Best Practices

> [!IMPORTANT]
> **Never commit your `.env` file!**

This project handles API keys and sensitive configuration. Follow these rules:

1. **Secrets Management**:
   - Real secrets go in `.env` (which is gitignored by default)
   - Templates go in `.env.example` (safe to commit)

2. **Git Safety**:
   - The `.gitignore` file is pre-configured to exclude `.env`, `.venv`, and other sensitive files.
   - Always verify what you're committing with `git status`

3. **CI/CD**:
   - Use GitHub Secrets or environment variables in your deployment platform
   - Never hardcode secrets in source code files

---

## 🛠️ Technical Highlights

### **Backend Skills Demonstrated**

| Skill | Implementation |
|-------|---------------|
| **API Development** | FastAPI with 6 REST endpoints, auto-generated OpenAPI docs |
| **Data Validation** | Pydantic models with custom business logic validators |
| **Testing** | 53 automated tests (100% pass rate), pytest framework |
| **Containerization** | Multi-stage Docker build, docker-compose orchestration |
| **Observability** | Structured JSON logging, Prometheus metrics, request tracing |
| **Third-party Integrations** | Notion API integration for result exports |
| **Code Quality** | Type hints, modular architecture, abstract base classes |

### **Architecture**

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌──────────────────────────┐   │
│  │  Logging Middleware      │   │ ← Request tracing
│  └──────────────────────────┘   │ 
│  ┌──────────────────────────┐   │
│  │  Validation Engine       │   │ ← Business logic
│  └──────────────────────────┘   │
│  ┌──────────────────────────┐   │
│  │  Metrics Collection      │   │ ← Prometheus
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

---

## 📊 Key Features

### For Users
- 🌐 **RESTful API** - Standard HTTP endpoints, works with any client
- 📤 **Multiple Input Formats** - JSON, YAML, or Excel files
- 🔍 **Smart Validation** - Catches logical errors, not just data format issues
- 📚 **Self-Documenting** - Interactive Swagger UI included

### For Operations
- 🐳 **Docker Ready** - One command deployment
- 📈 **Production Monitoring** - Prometheus metrics built-in
- 📝 **Structured Logging** - JSON logs with request IDs for tracing
- ✅ **Health Checks** - Kubernetes/load balancer compatible

---

## 🧪 Testing

Comprehensive test coverage across all layers:

```bash
pytest tests/ -v

# Results: 53 tests, 100% passing
# ✅ Unit tests (models, validation logic)
# ✅ Integration tests (API endpoints)
# ✅ End-to-end tests (full workflows)
```

---

## 📖 API Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `GET /health` | Service health check | Returns operational status |
| `GET /metrics` | Prometheus metrics | Request counts, latency, errors |
| `POST /validate` | Validate JSON itinerary | Returns validation results |
| `POST /upload` | Validate Excel/YAML file | Accepts file upload |
| `POST /export/notion` | Validate & export to Notion | Returns results + Notion page URL |
| `GET /docs` | Interactive documentation | Swagger UI |

---

## 💻 Technology Stack

**Core:**
- Python 3.9+
- FastAPI (async web framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

**Observability:**
- Prometheus (metrics)
- Structured JSON logging
- Request tracing

**Integrations:**
- Notion API (optional export feature)

**Development:**
- pytest (testing)
- Docker & Docker Compose
- Type hints throughout

---

## 🎓 What I Learned

Building this project taught me:

1. **API Design** - How to design intuitive, RESTful endpoints
2. **Data Validation** - Implementing business logic vs schema validation
3. **Production Readiness** - Logging, metrics, health checks, error handling
4. **Testing Strategy** - Unit, integration, and end-to-end test patterns
5. **Containerization** - Multi-stage Docker builds, optimization
6. **Code Organization** - Clean architecture with separation of concerns

---

## 🚢 Deployment

### Local Development
```bash
python -m uvicorn src.api:app --reload
```

### Production (Docker)
```bash
docker build -t trs-api .
docker run -p 8000:8000 \
  -e LOG_FORMAT=json \
  -e ENABLE_METRICS=true \
  trs-api
```

### Cloud Platforms
Works with: AWS ECS, Google Cloud Run, Azure Container Instances, Railway, Render

---

## 📁 Project Structure

```
travel-readiness-sentinel/
├── src/
│   ├── __main__.py          # CLI entry point
│   ├── api.py               # FastAPI application
│   ├── core/                # Business logic
│   │   ├── model.py         # Data models
│   │   ├── validation.py    # Validation rules
│   │   └── schemas.py       # API schemas
│   └── ingestion/           # File parsers
│       ├── excel.py         # Excel reader
│       └── yaml.py          # YAML reader
├── tests/                   # 53 automated tests
├── examples/                # Sample itineraries
├── Dockerfile               # Container definition
└── docker-compose.yml       # Local development
```

---

## 🤝 Contact

**Harvey Lam**
- 💼 GitHub: [@harveycyl](https://github.com/harveycyl)

---

## 📄 License

MIT License - feel free to use this project as a reference or starting point for your own work.

---

<div align="center">

**Built with ❤️ to demonstrate production-grade Python development**

*This project showcases real-world backend engineering skills applicable to any API-driven application*

</div>
