# Travel Readiness Sentinel - Enterprise Microservice Project Plan

## Overview
Transform the current Python CLI validation tool into a production-grade enterprise microservice with AI capabilities.

**Current State**: CLI tool that validates travel itineraries from Excel/YAML files using Pydantic models and business logic checks.

**Target State**: Containerized FastAPI microservice with observability, AI ingestion capabilities, and enterprise-grade reliability.

---

## Phase 1: Refactor to API (FastAPI)
**Goal**: Transform the standalone CLI script into a stateless REST API

### 1.1 Core Logic Refactoring
- [ ] Create `src/core/` directory structure
- [ ] Move validation logic from `main.py` to `src/core/validators.py`
- [ ] Extract business rules to `src/core/business_rules.py`
- [ ] Move Pydantic models to `src/core/models.py`
- [ ] Create `src/core/parsers.py` for Excel/YAML parsing logic
- [ ] Add `__init__.py` files to make modules importable
- [ ] Update imports and ensure clean separation of concerns

### 1.2 FastAPI Implementation
- [ ] Add FastAPI and uvicorn to `requirements.txt`
- [ ] Create `src/api.py` with FastAPI application instance
- [ ] Implement CORS middleware for web client support
- [ ] Add request/response models for API endpoints

### 1.3 API Endpoints
#### POST /validate
- [ ] Accept JSON body matching Pydantic Itinerary model
- [ ] Run validation logic and return structured JSON report
- [ ] Include validation status, errors, and success messages
- [ ] Add proper HTTP status codes (200 for valid, 422 for invalid)

#### POST /upload
- [ ] Accept multipart/form-data with .xlsx file
- [ ] Parse Excel file using existing logic
- [ ] Convert to internal Pydantic model
- [ ] Return validation report in same format as /validate

#### GET /
- [ ] Root endpoint with API information and version
- [ ] Links to documentation and health check

### 1.4 Documentation & Testing
- [ ] Ensure Swagger UI available at `/docs`
- [ ] Add OpenAPI metadata (title, description, version)
- [ ] Create example request/response bodies
- [ ] Add basic unit tests for API endpoints
- [ ] Test file upload functionality

### 1.5 Configuration
- [ ] Create `src/config.py` for environment-based configuration
- [ ] Add development vs production settings
- [ ] Configure CORS origins, API keys, etc.

**Deliverables**:
- Refactored codebase with clean separation
- Working FastAPI application
- Two functional endpoints
- Swagger documentation
- Basic test coverage

---

## Phase 2: Containerization (Docker)
**Goal**: Make the application deployable anywhere with consistent behavior

### 2.1 Dockerfile Creation
- [ ] Create multi-stage Dockerfile
- [ ] Use `python:3.11-slim` as base image
- [ ] Create non-root user for security
- [ ] Install system dependencies if needed
- [ ] Copy requirements.txt and install Python packages
- [ ] Copy application code
- [ ] Expose port 8000
- [ ] Configure uvicorn as entry point

### 2.2 Docker Optimization
- [ ] Implement multi-stage build to reduce image size
- [ ] Use `.dockerignore` to exclude unnecessary files
- [ ] Cache pip packages for faster builds
- [ ] Set appropriate labels and metadata

### 2.3 Docker Compose Setup
- [ ] Create `docker-compose.yaml` for local development
- [ ] Configure environment variables
- [ ] Set up volume mounting for development
- [ ] Add health checks
- [ ] Configure restart policies

### 2.4 Container Testing
- [ ] Build and test container locally
- [ ] Verify all endpoints work in containerized environment
- [ ] Test file upload functionality in container
- [ ] Validate environment variable handling

### 2.5 Deployment Preparation
- [ ] Create `.env.example` file
- [ ] Document container deployment process
- [ ] Add container security best practices
- [ ] Prepare for cloud deployment (optional)

**Deliverables**:
- Production-ready Dockerfile
- Docker Compose configuration
- Container deployment documentation
- Tested containerized application

---

## Phase 3: Observability (Structured Logging)
**Goal**: Replace print statements with enterprise-grade logging and monitoring

### 3.1 Structured Logging Implementation
- [ ] Add `structlog` to requirements.txt
- [ ] Create `src/logging_config.py`
- [ ] Configure JSON output format
- [ ] Set up different log levels (DEBUG, INFO, WARN, ERROR)
- [ ] Replace all print() statements with structured logs

### 3.2 FastAPI Middleware Integration
- [ ] Create correlation ID middleware
- [ ] Generate unique `request_id` for each incoming request
- [ ] Include `request_id` in all logs for request tracing
- [ ] Add request/response logging middleware
- [ ] Log request method, path, duration, status code

### 3.3 Application Logging
- [ ] Add structured logging to validation logic
- [ ] Log validation start/completion events
- [ ] Log validation failures with detailed context
- [ ] Log file upload events and metadata
- [ ] Add performance timing logs

### 3.4 Health Check Endpoint
- [ ] Implement `GET /health` endpoint
- [ ] Return `{"status": "ok", "timestamp": "...", "version": "..."}` 
- [ ] Add dependency checks (database, external services if any)
- [ ] Configure for Kubernetes readiness/liveness probes

### 3.5 Monitoring Integration Ready
- [ ] Structure logs for easy parsing by monitoring tools
- [ ] Add application metrics logging
- [ ] Include error tracking context
- [ ] Prepare for integration with monitoring platforms

**Deliverables**:
- Fully structured JSON logging
- Request correlation tracking
- Health check endpoint
- Production-ready observability

---

## Phase 4: AI Ingestion Layer
**Goal**: Enable unstructured text ingestion via LLM with deterministic validation safeguards

### 4.1 LLM Integration Setup
- [ ] Add OpenAI SDK or LangChain to requirements.txt
- [ ] Create `src/ai/` directory structure
- [ ] Implement `src/ai/llm_client.py` for LLM interactions
- [ ] Add environment variables for API keys
- [ ] Create prompt templates for itinerary extraction

### 4.2 Text Ingestion Endpoint
#### POST /ingest-text
- [ ] Accept `{"text": "raw email/document content"}`
- [ ] Implement text preprocessing and cleaning
- [ ] Send to LLM for structured extraction
- [ ] Return extracted data + validation results

### 4.3 LLM Prompt Engineering
- [ ] Design prompts to extract itinerary data from text
- [ ] Create examples for few-shot learning
- [ ] Handle various text formats (emails, documents, chat messages)
- [ ] Implement prompt versioning and A/B testing capability

### 4.4 Safety Rails Implementation
- [ ] Create `src/ai/safety.py` for validation pipeline
- [ ] Pass LLM output immediately to existing Pydantic validators
- [ ] Implement confidence scoring for extracted data
- [ ] Add fallback mechanisms for low-confidence extractions
- [ ] Log LLM interactions for monitoring and improvement

### 4.5 Enhanced Validation Pipeline
- [ ] Extend validation to include AI-extracted data quality metrics
- [ ] Add validation for common LLM hallucinations (invalid dates, impossible locations)
- [ ] Implement human-in-the-loop flagging for uncertain cases
- [ ] Create validation report that distinguishes AI vs manual input

### 4.6 AI Monitoring and Observability
- [ ] Log all LLM requests and responses
- [ ] Track extraction success rates
- [ ] Monitor API usage and costs
- [ ] Add alerting for validation failures
- [ ] Implement A/B testing for prompt improvements

**Deliverables**:
- AI-powered text ingestion endpoint
- Robust safety validation pipeline
- LLM interaction monitoring
- Production-ready AI integration

---

## Success Criteria

### Phase 1 Success Metrics
- [ ] All existing CLI functionality available via API
- [ ] Swagger documentation accessible
- [ ] File upload working correctly
- [ ] Response time < 2 seconds for typical validation

### Phase 2 Success Metrics
- [ ] Container builds in < 5 minutes
- [ ] Container image size < 500MB
- [ ] Application starts in < 30 seconds
- [ ] All endpoints functional in container

### Phase 3 Success Metrics
- [ ] All logs in structured JSON format
- [ ] Request correlation working across all operations
- [ ] Health check responds in < 100ms
- [ ] No print() statements in production code

### Phase 4 Success Metrics
- [ ] AI extraction accuracy > 80% for well-formatted text
- [ ] Safety rails catch 100% of invalid dates/data
- [ ] End-to-end response time < 10 seconds
- [ ] Cost per extraction < $0.10

---

## Technical Debt and Considerations

### Security
- [ ] Input validation and sanitization
- [ ] Rate limiting implementation
- [ ] API authentication (Phase 4+)
- [ ] Secrets management for AI API keys

### Performance
- [ ] Async processing for file uploads
- [ ] Caching for repeated validations
- [ ] Connection pooling for external services
- [ ] Resource usage monitoring

### Scalability
- [ ] Stateless design maintained throughout
- [ ] Database integration planning (if needed)
- [ ] Queue system for long-running AI processing
- [ ] Load testing preparation

### Maintenance
- [ ] Automated testing pipeline
- [ ] Dependency update strategy
- [ ] Documentation maintenance
- [ ] Version management strategy

---

## Timeline Estimation

- **Phase 1**: 2-3 weeks (40-60 hours)
- **Phase 2**: 1 week (20 hours)
- **Phase 3**: 1-2 weeks (20-40 hours)
- **Phase 4**: 2-3 weeks (40-60 hours)

**Total**: 6-9 weeks (120-180 hours)

---

## Next Steps
1. Review and approve this plan
2. Set up development environment for Phase 1
3. Create feature branch for Phase 1 development
4. Begin with core logic refactoring
5. Implement iterative development with regular testing