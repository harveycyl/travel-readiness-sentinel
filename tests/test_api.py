"""
API endpoint tests for Travel Readiness Sentinel.
Tests all FastAPI endpoints using TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import pandas as pd

from src.api import app


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_itinerary_data(self):
        """Valid itinerary data for testing."""
        return {
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
    
    @pytest.fixture
    def invalid_itinerary_data(self):
        """Invalid itinerary data (misaligned dates)."""
        return {
            "trip_details": {
                "destination": "London",
                "start_date": "2025-05-10",
                "end_date": "2025-05-17",
                "total_duration_days": 7
            },
            "flights": [
                {
                    "type": "arrival",
                    "flight_number": "BA117",
                    "arrival_date": "2025-05-11"  # Misaligned
                },
                {
                    "type": "departure",
                    "flight_number": "BA118",
                    "departure_date": "2025-05-16"  # Misaligned
                }
            ],
            "accommodation": {
                "hotel_name": "The Savoy",
                "check_in": "2025-05-10",
                "check_out": "2025-05-15"  # Too short
            }
        }
    
    def test_root_endpoint(self, client):
        """Test GET / returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert data["documentation_url"] == "/docs"
        assert data["health_check_url"] == "/health"
    
    def test_health_check(self, client):
        """Test GET /health returns healthy status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "version" in data
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["api"] == "operational"
    
    def test_validate_valid_itinerary(self, client, valid_itinerary_data):
        """Test POST /validate with valid itinerary data."""
        response = client.post("/validate", json=valid_itinerary_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["status"] == "success"
        assert data["destination"] == "Tokyo"
        assert data["total_checks"] == 3
        assert data["passed_checks"] == 3
        assert data["failed_checks"] == 0
        
        # Check individual results
        assert len(data["checks"]) == 3
        for check in data["checks"]:
            assert check["passed"] is True
            assert "check_name" in check
            assert "message" in check
    
    def test_validate_invalid_itinerary(self, client, invalid_itinerary_data):
        """Test POST /validate with invalid itinerary (business logic failures)."""
        response = client.post("/validate", json=invalid_itinerary_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["status"] == "failed"
        assert data["destination"] == "London"
        assert data["total_checks"] == 3
        assert data["passed_checks"] == 0
        assert data["failed_checks"] == 3
        
        # All checks should fail
        assert len(data["checks"]) == 3
        for check in data["checks"]:
            assert check["passed"] is False
    
    def test_validate_malformed_data(self, client):
        """Test POST /validate with malformed data (Pydantic validation error)."""
        malformed_data = {
            "trip_details": {
                "destination": "Paris"
                # Missing required fields
            }
        }
        
        response = client.post("/validate", json=malformed_data)
        
        assert response.status_code == 422
        data = response.json()
        
        # FastAPI returns 'detail' key for validation errors
        assert "detail" in data
    
    def test_validate_invalid_flight_number(self, client, valid_itinerary_data):
        """Test POST /validate with invalid flight number."""
        valid_itinerary_data["flights"][0]["flight_number"] = "AB"  # Too short
        
        response = client.post("/validate", json=valid_itinerary_data)
        
        assert response.status_code == 422
    
    def test_upload_excel_file(self, client):
        """Test POST /upload with Excel file."""
        # Create temporary Excel file
        excel_data = {
            'Field': [
                'Trip Destination',
                'Trip Start Date', 
                'Trip End Date',
                'Total Duration (Days)',
                '',
                'Arrival Flight Number',
                'Arrival Date',
                '',
                'Departure Flight Number', 
                'Departure Date',
                '',
                'Hotel Name',
                'Hotel Check-in Date',
                'Hotel Check-out Date'
            ],
            'Value': [
                'Tokyo',
                '2025-04-10',
                '2025-04-17', 
                7,
                '',
                'NH110',
                '2025-04-10',
                '',
                'NH111',
                '2025-04-17',
                '',
                'Park Hyatt Tokyo',
                '2025-04-10',
                '2025-04-17'
            ]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            df = pd.DataFrame(excel_data)
            df.to_excel(temp_file.name, sheet_name='Travel Itinerary', index=False)
            temp_path = temp_file.name
        
        try:
            # Upload file
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/upload",
                    files={"file": ("itinerary.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert data["destination"] == "Tokyo"
            assert data["passed_checks"] == 3
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_upload_unsupported_file_type(self, client):
        """Test POST /upload with unsupported file type."""
        # Create a text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"Some text content")
            temp_path = temp_file.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "Unsupported file type" in data["detail"]
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    # Note: CORS is configured but TestClient doesn't simulate CORS middleware
    # CORS should be tested with actual HTTP requests or browser testing
    
    def test_openapi_docs_available(self, client):
        """Test that OpenAPI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "paths" in openapi_spec
        assert "/validate" in openapi_spec["paths"]
        assert "/upload" in openapi_spec["paths"]
        assert "/health" in openapi_spec["paths"]
