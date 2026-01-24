"""
FastAPI application for Travel Readiness Sentinel.
Provides REST API endpoints for itinerary validation.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from pathlib import Path
import tempfile
import yaml
import time
from typing import Union

from .config import settings
from .core.model import Itinerary
from .core.validation import run_all_checks
from .ingestion.excel import ExcelIngestion
from .ingestion.yaml import YAMLIngestion
from .core.schemas import (
    ValidationResponse,
    ValidationCheckResult,
    ValidationErrorResponse,
    HealthResponse,
    APIInfoResponse
)
from .logging_config import setup_logging, logger
from .middleware import LoggingMiddleware
from .metrics import metrics, get_metrics


# Application startup time for uptime tracking
app_start_time = time.time()

# Initialize logging
setup_logging(log_level=settings.log_level, log_format=settings.log_format)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add logging middleware
if settings.enable_metrics:
    app.add_middleware(LoggingMiddleware)
    logger.info("Logging middleware enabled")

# Set application version in metrics
if settings.enable_metrics:
    metrics.set_app_version(settings.app_version)
    logger.info("Metrics collection enabled")


# Exception handlers
@app.exception_handler(PydanticValidationError)
async def pydantic_validation_exception_handler(request, exc: PydanticValidationError):
    """Handle Pydantic validation errors with structured response."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Data validation failed",
            "details": exc.errors()
        }
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc: ValueError):
    """Handle ValueError with structured response."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValueError",
            "message": str(exc)
        }
    )


# API Endpoints
@app.get("/", response_model=APIInfoResponse)
async def root():
    """
    Root endpoint with API information.
    """
    return APIInfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        documentation_url="/docs",
        health_check_url="/health"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns service status, version information, and basic metrics.
    """
    uptime_seconds = int(time.time() - app_start_time)
    
    checks = {
        "api": "operational",
        "validation_engine": "operational"
    }
    
    if settings.enable_metrics:
        checks["metrics"] = "operational"
    
    response = HealthResponse(
        status="ok",
        version=settings.app_version,
        checks=checks
    )
    
    # Add uptime to response (not in schema, but useful)
    response_dict = response.model_dump()
    response_dict["uptime_seconds"] = uptime_seconds
    
    return response_dict


@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus exposition format.
    
    Metrics include:
    - HTTP request counts and latency
    - Validation check results
    - File upload statistics
    """
    if not settings.enable_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrics collection is disabled"
        )
    
    return get_metrics()


@app.post("/validate", response_model=ValidationResponse)
async def validate_itinerary(itinerary: Itinerary):
    """
    Validate a travel itinerary from JSON data.
    
    Accepts a complete itinerary object and runs all validation checks.
    Returns detailed results for each check.
    
    **Example Request:**
    ```json
    {
        "trip_details": {
            "destination": "Tokyo",
            "start_date": "2025-04-10",
            "end_date": "2025-04-17",
            "total_duration_days": 7
        },
        "flights": [
            {
                "type": "arrival",
                "flight_number": "NH110",
                "arrival_date": "2025-04-10"
            },
            {
                "type": "departure",
                "flight_number": "NH111",
                "departure_date": "2025-04-17"
            }
        ],
        "accommodation": {
            "hotel_name": "Park Hyatt Tokyo",
            "check_in": "2025-04-10",
            "check_out": "2025-04-17"
        }
    }
    ```
    """
    # Run all validation checks
    check_results = run_all_checks(itinerary)
    
    # Record metrics for each check
    if settings.enable_metrics:
        metrics.record_validation_request("json")
        for result in check_results:
            metrics.record_validation_check(result.check_name, result.passed)
    
    # Convert to API schema
    api_checks = [
        ValidationCheckResult(
            check_name=result.check_name,
            passed=result.passed,
            message=result.message
        )
        for result in check_results
    ]
    
    # Calculate summary
    passed_count = sum(1 for r in check_results if r.passed)
    failed_count = len(check_results) - passed_count
    
    return ValidationResponse(
        status="success" if failed_count == 0 else "failed",
        destination=itinerary.trip_details.destination,
        total_checks=len(check_results),
        passed_checks=passed_count,
        failed_checks=failed_count,
        checks=api_checks
    )


@app.post("/upload", response_model=ValidationResponse)
async def upload_and_validate(
    file: UploadFile = File(..., description="Excel (.xlsx) or YAML (.yaml/.yml) file")
):
    """
    Upload and validate a travel itinerary file.
    
    Accepts Excel (.xlsx) or YAML (.yaml, .yml) files.
    Parses the file and runs all validation checks.
    
    **Supported Formats:**
    - Excel: Use the template format with Field/Value columns
    - YAML: Standard itinerary structure
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_file_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Allowed: {settings.allowed_file_extensions}"
        )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        # Write uploaded content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Parse file based on extension
        if file_ext == '.xlsx':
            reader = ExcelIngestion()
            raw_data = reader.parse(temp_path)
            source_type = "excel"
        elif file_ext in ['.yaml', '.yml']:
            reader = YAMLIngestion()
            raw_data = reader.parse(temp_path)
            source_type = "yaml"
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")
        
        # Create Itinerary object (will validate via Pydantic)
        itinerary = Itinerary(**raw_data)
        
        # Run validation checks
        check_results = run_all_checks(itinerary)
        
        # Record metrics
        if settings.enable_metrics:
            metrics.record_validation_request(source_type)
            metrics.record_file_upload(file_ext.lstrip('.'), success=True)
            for result in check_results:
                metrics.record_validation_check(result.check_name, result.passed)
        
        # Convert to API schema
        api_checks = [
            ValidationCheckResult(
                check_name=result.check_name,
                passed=result.passed,
                message=result.message
            )
            for result in check_results
        ]
        
        # Calculate summary
        passed_count = sum(1 for r in check_results if r.passed)
        failed_count = len(check_results) - passed_count
        
        return ValidationResponse(
            status="success" if failed_count == 0 else "failed",
            destination=itinerary.trip_details.destination,
            total_checks=len(check_results),
            passed_checks=passed_count,
            failed_checks=failed_count,
            checks=api_checks
        )
    
    finally:
        # Clean up temporary file
        Path(temp_path).unlink(missing_ok=True)


@app.post("/export/notion")
async def export_to_notion_endpoint(itinerary: Itinerary):
    """
    Validate itinerary and export results to Notion.
    
    This endpoint combines validation with automatic Notion export.
    It validates the itinerary, exports the results to a Notion page,
    and returns both validation results and the Notion page URL.
    
    **Requirements:**
    - Notion integration must be configured (NOTION_API_TOKEN and NOTION_PAGE_ID)
    - See README for setup instructions
    
    **Response includes:**
    - All standard validation results
    - `notion_url`: Direct link to the created Notion page
    - `notion_page_id`: ID of the created page
    - `exported_at`: Timestamp of export
    """
    # Check if Notion is configured
    if not settings.notion_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "NotionNotConfigured",
                "message": "Notion integration is not configured. Please set NOTION_API_TOKEN and NOTION_PAGE_ID in your .env file.",
                "documentation": "See README for setup instructions"
            }
        )
    
    # Run validation (same as /validate endpoint)
    check_results = run_all_checks(itinerary)
    
    # Record metrics
    if settings.enable_metrics:
        metrics.record_validation_request("json")
        for result in check_results:
            metrics.record_validation_check(result.check_name, result.passed)
    
    # Convert to API schema
    api_checks = [
        ValidationCheckResult(
            check_name=result.check_name,
            passed=result.passed,
            message=result.message
        )
        for result in check_results
    ]
    
    # Calculate summary
    passed_count = sum(1 for r in check_results if r.passed)
    failed_count = len(check_results) - passed_count
    
    validation_response = ValidationResponse(
        status="success" if failed_count == 0 else "failed",
        destination=itinerary.trip_details.destination,
        total_checks=len(check_results),
        passed_checks=passed_count,
        failed_checks=failed_count,
        checks=api_checks
    )
    
    # Export to Notion
    try:
        from .integrations.notion_exporter import export_to_notion
        
        logger.info(f"Exporting validation results to Notion for {itinerary.trip_details.destination}")
        export_result = await export_to_notion(
            validation_response=validation_response,
            notion_token=settings.notion_api_token,
            parent_page_id=settings.notion_page_id
        )
        
        # Add Notion export info to response
        response_dict = validation_response.model_dump(mode='json')
        response_dict["notion_export"] = export_result
        
        logger.info(f"Successfully exported to Notion: {export_result['notion_url']}")
        return response_dict
        
    except Exception as e:
        logger.error(f"Failed to export to Notion: {e}")
        # Still return validation results even if Notion export fails
        response_dict = validation_response.model_dump(mode='json')
        response_dict["notion_export"] = {
            "error": str(e),
            "message": "Validation completed but Notion export failed"
        }
        return JSONResponse(
            status_code=status.HTTP_207_MULTI_STATUS,
            content=response_dict
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
