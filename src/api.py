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
from typing import Union

from .config import settings
from .model import Itinerary
from .validation import run_all_checks
from .excel_reader import ExcelItineraryReader
from .schemas import (
    ValidationResponse,
    ValidationCheckResult,
    ValidationErrorResponse,
    HealthResponse,
    APIInfoResponse
)


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
    Returns service status and version information.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        checks={
            "api": "operational",
            "validation_engine": "operational"
        }
    )


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
            reader = ExcelItineraryReader()
            raw_data = reader.read_excel(temp_path)
        elif file_ext in ['.yaml', '.yml']:
            with open(temp_path, 'r') as f:
                raw_data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")
        
        # Create Itinerary object (will validate via Pydantic)
        itinerary = Itinerary(**raw_data)
        
        # Run validation checks
        check_results = run_all_checks(itinerary)
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
