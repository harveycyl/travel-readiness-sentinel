"""
API request/response schemas.
Separate from domain models to allow API versioning and evolution.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class ValidationCheckResult(BaseModel):
    """Result of a single validation check."""
    check_name: str = Field(..., description="Name of the validation check")
    passed: bool = Field(..., description="Whether the check passed")
    message: str = Field(..., description="Human-readable result message")


class ValidationResponse(BaseModel):
    """Response from validation endpoints."""
    status: Literal["success", "failed"] = Field(..., description="Overall validation status")
    destination: str = Field(..., description="Trip destination")
    total_checks: int = Field(..., description="Total number of checks performed")
    passed_checks: int = Field(..., description="Number of checks that passed")
    failed_checks: int = Field(..., description="Number of checks that failed")
    checks: List[ValidationCheckResult] = Field(..., description="Detailed check results")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")


class ValidationErrorResponse(BaseModel):
    """Response when validation cannot be performed due to data errors."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["ok", "degraded", "down"] = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Optional[dict] = Field(None, description="Individual health check results")


class APIInfoResponse(BaseModel):
    """Root endpoint information."""
    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version")
    description: str = Field(..., description="API description")
    documentation_url: str = Field(..., description="URL to interactive API documentation")
    health_check_url: str = Field(..., description="URL to health check endpoint")
