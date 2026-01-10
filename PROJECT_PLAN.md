# Travel Readiness Sentinel - Project Plan

## 🎯 Project Overview

Transform a Python CLI validation tool into a production-grade microservice with observability and AI capabilities.

**Current Status:** Phase 2 Complete (Dockerized FastAPI)
**Next:** Phase 3 (Observability + Maintainability + AI Foundation)

---

## ✅ Phase 1: FastAPI Implementation (COMPLETE)

**Completed:** January 2026

**What was built:**
- REST API with FastAPI
- 4 endpoints: `/`, `/health`, `/validate`, `/upload`
- Pydantic models for validation
- Excel and YAML file parsing
- Swagger UI documentation at `/docs`
- 55 passing tests

**Key files:**
- `src/api.py` - FastAPI application
- `src/model.py` - Pydantic models
- `src/validation.py` - Business logic
- `src/excel_reader.py` - Excel parsing
- `src/schemas.py` - API schemas

---

## ✅ Phase 2: Docker Containerization (COMPLETE)

**Completed:** January 2026

**What was built:**
- Multi-stage Dockerfile (515MB image, 110MB content)
- Docker Compose for local development
- Non-root user for security
- Health checks
- `.dockerignore` for optimization

**Key files:**
- `Dockerfile` - Multi-stage build
- `docker-compose.yml` - Local dev setup
- `.dockerignore` - Build optimization

**Deployment:**
```bash
docker-compose up -d
# API available at http://localhost:8000
```

---

## 🚧 Phase 3: Observability + Maintainability + AI Foundation (IN PROGRESS)

**Goal:** Production-grade monitoring + clean architecture + prepare for AI

**Time estimate:** 12-15 hours

### Part A: Observability (6-8 hours)

#### A1. Structured Logging ⭐ ESSENTIAL
- JSON-formatted logs with context
- Track request IDs, source types (excel/yaml/ai)
- **Dependencies:** `python-json-logger>=2.0.0`
- **Time:** 3 hours

#### A2. Request/Response Middleware ⭐ ESSENTIAL
- Auto-log every API call
- Track duration, status codes
- **Time:** 1 hour

#### A3. Metrics Endpoint ⭐ IMPORTANT
- Prometheus-compatible metrics
- Track: request count, latency, error rate
- Separate metrics for AI vs manual inputs
- **Dependencies:** `prometheus-client>=0.19.0`
- **Time:** 2-3 hours

#### A4. Enhanced Health Checks
- Detailed component status
- Include metrics in health response
- **Time:** 1 hour

---

### Part B: Maintainability (4-5 hours)

#### B1. Code Organization ⭐ ESSENTIAL

**New structure:**
```
src/
├── api.py                  # FastAPI app
├── config.py              # Settings (AI-ready)
├── middleware.py          # NEW: Logging
├── metrics.py             # NEW: Prometheus
├── logging_config.py      # NEW: Logging setup
│
├── core/                  # NEW: Core logic
│   ├── model.py
│   ├── validation.py
│   └── schemas.py
│
├── ingestion/            # NEW: Input processing (AI-ready!)
│   ├── base.py           # Abstract base class
│   ├── excel.py          # Excel reader (refactored)
│   ├── yaml.py           # YAML reader
│   └── ai.py             # AI stub (Phase 4)
│
└── utils/
    └── helpers.py
```

**Time:** 2-3 hours

#### B2. Abstract Base Classes ⭐ IMPORTANT

Create `IngestionSource` interface:
- Consistent API for all input types
- Easy to add AI without changing existing code
- **Time:** 2 hours

#### B3. Configuration Management
- Centralize settings in `config.py`
- AI settings prepared (disabled by default)
- **Time:** 30 minutes

---

### Part C: AI Foundation (2 hours)

#### C1. Unified Ingestion Pipeline ⭐ ESSENTIAL
- Single validation endpoint for all input types
- AI slots in seamlessly
- **Time:** 1 hour

#### C2. AI Placeholder
- Create stub `AIIngestion` class
- Documents future capability
- **Time:** 30 minutes

#### C3. Documentation
- Update README with planned AI features
- **Time:** 30 minutes

---

### Implementation Order

**Week 1: Observability (6-8 hours)**
1. Structured logging (A1)
2. Request middleware (A2)
3. Metrics endpoint (A3)

**Week 2: Maintainability + AI Prep (6-7 hours)**
4. Code organization (B1)
5. Abstract base classes (B2)
6. Unified pipeline (C1)
7. AI placeholder (C2)

---

### Dependencies to Add

```txt
# Observability
python-json-logger>=2.0.0
prometheus-client>=0.19.0

# AI (Phase 4 - commented out)
# openai>=1.0.0
```

---

## 🔮 Phase 4: AI Ingestion Layer (PLANNED)

**Goal:** Extract itineraries from unstructured text using LLM

**Time estimate:** 10 hours (thanks to Phase 3 foundation!)

**LLM Provider:** Google AI (Gemini) - using your existing Google AI Pro subscription!

### What Phase 3 Enables

With Phase 3 complete, Phase 4 becomes simple:

```python
# src/ingestion/ai.py
import google.generativeai as genai

class AIIngestion(IngestionSource):
    def __init__(self):
        genai.configure(api_key=settings.google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def parse(self, text: str) -> Dict[str, Any]:
        # Just implement this method!
        response = self.model.generate_content(
            EXTRACTION_PROMPT + text,
            generation_config={
                "response_mime_type": "application/json"  # Native JSON mode!
            }
        )
        return json.loads(response.text)
```

**Everything else already works:**
- ✅ Logging (tracks AI separately)
- ✅ Metrics (monitors AI success rate)
- ✅ Validation (same Pydantic models)
- ✅ API (unified endpoint)

**Why Google AI (Gemini)?**
- ✅ You have Google AI Pro subscription (no extra cost!)
- ✅ 2M token context window (handles long emails)
- ✅ Native JSON mode (perfect for structured extraction)
- ✅ Multimodal (can handle images if needed)

### Phase 4 Tasks

1. **Google AI Integration** (3 hours)
   - Install `google-generativeai` SDK
   - Configure Gemini 1.5 Pro
   - Prompt engineering for JSON extraction
   - Response parsing

2. **Safety Rails** (2 hours)
   - Validate LLM output with Pydantic
   - Handle hallucinations
   - Confidence scoring
   - Fallback to OpenAI (optional)

3. **AI Monitoring** (2 hours)
   - Track extraction success rate
   - Monitor token usage
   - Log LLM interactions
   - Compare Google AI vs manual accuracy

4. **Testing** (2 hours)
   - Test with various text formats (emails, PDFs, chat)
   - Edge cases (incomplete info, ambiguous dates)
   - Error handling

5. **Documentation** (1 hour)
   - API examples
   - Prompt templates
   - Configuration guide

### Dependencies

```txt
# Google AI (Primary - using your subscription!)
google-generativeai>=0.3.0

# OpenAI (Optional fallback)
# openai>=1.0.0
```

### Configuration

```python
# .env
AI_ENABLED=true
AI_PROVIDER=google  # or "openai"
GOOGLE_AI_API_KEY=your_api_key_here
GOOGLE_AI_MODEL=gemini-1.5-pro
```

---

## � Phase 5: Gmail Integration via MCP (PLANNED)

**Goal:** Connect to Gmail using Model Context Protocol for email-based itinerary extraction

**Time estimate:** 8-10 hours

### What is MCP?

**Model Context Protocol** - A standardized way for AI applications to connect to external data sources (Gmail, Drive, Slack, etc.) without managing APIs directly.

### Architecture

```
TRS API → MCP Client → Gmail MCP Server → Gmail API → User's Emails
```

### Implementation Overview

1. **MCP Setup** (2h)
   - Install MCP client library
   - Configure Gmail MCP server
   - OAuth authentication flow

2. **Email Fetching** (2h)
   - Query travel-related emails via MCP
   - Filter by keywords (flight, hotel, booking, itinerary)
   - Return email list to user

3. **User Selection** (2h)
   - API endpoint to list emails
   - User selects relevant emails
   - Preview email content

4. **Email → AI Extraction** (2h)
   - Retrieve email body via MCP
   - Pass to Phase 4 AI extraction
   - Validate and return results

5. **Testing & Documentation** (2h)

### Key Benefits of MCP

- ✅ **Standardized** - Works with any MCP-compatible service
- ✅ **Maintained** - Community-maintained servers
- ✅ **Secure** - OAuth handled properly
- ✅ **Extensible** - Easy to add Outlook, iCloud later
- ✅ **Less code** - Focus on business logic, not API integration

### New Dependencies

```txt
mcp>=1.0.0                    # Model Context Protocol client
google-auth>=2.0.0            # OAuth for Gmail
```

### New Endpoints

```
GET  /auth/gmail              # OAuth flow
GET  /emails                  # List travel emails
POST /extract-from-email      # Extract from selected email
```

---

## �📊 Overall Progress

| Phase | Status | Time Spent | Deliverables |
|-------|--------|------------|--------------|
| Phase 1: FastAPI | ✅ Complete | ~20 hours | REST API, 4 endpoints, tests |
| Phase 2: Docker | ✅ Complete | ~10 hours | Containerized app, compose |
| Phase 3: Observability | 🚧 In Progress | 0/15 hours | Logging, metrics, clean code |
| Phase 4: AI Ingestion | 📋 Planned | 0/10 hours | LLM extraction |
| Phase 5: Gmail MCP | 📋 Planned | 0/10 hours | Email integration via MCP |

**Total estimated:** ~65 hours
**Completed:** ~30 hours (46%)
**Remaining:** ~35 hours (54%)

---

## 🎯 Success Criteria

### Phase 3 Complete When:
1. ✅ All requests logged in JSON format
2. ✅ `/metrics` endpoint shows request count, latency, errors
3. ✅ Code organized with `core/` and `ingestion/` modules
4. ✅ Abstract base class for all input types
5. ✅ AI placeholder created and documented

### Phase 4 Complete When:
1. ✅ Can extract itinerary from plain text
2. ✅ LLM output validated by Pydantic
3. ✅ AI metrics tracked separately
4. ✅ Handles errors gracefully
5. ✅ Documented with examples

### Phase 5 Complete When:
1. ✅ MCP client connected to Gmail
2. ✅ Can fetch and filter travel emails
3. ✅ User can select emails via API
4. ✅ Selected emails extracted via Phase 4 AI
5. ✅ OAuth flow working securely

---

## 💬 Open Questions

**For Phase 3:**
1. Prometheus metrics or simple JSON?
2. Logs to stdout (Docker best practice) or files?
3. Any code quality tools? (black, ruff, mypy?)

**For Phase 4:**
1. ✅ **LLM decided:** Google AI (Gemini 1.5 Pro) - using your subscription!
2. What text sources to prioritize? (email, chat, documents, PDFs?)
3. Should we add OpenAI as fallback option?

---

## 📝 Notes

- Phase 3 makes Phase 4 much easier (10h instead of 20h+)
- Clean architecture allows easy extension
- All phases maintain backward compatibility
- Docker setup unchanged throughout

**Last updated:** January 10, 2026
**Current branch:** `phase-3-observability`
