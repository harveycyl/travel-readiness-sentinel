"""
Prometheus metrics collection for Travel Readiness Sentinel API.
Tracks request counts, latency, validation results, and file uploads.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from fastapi import Response
import time

# Create a custom registry to avoid conflicts
registry = CollectorRegistry()

# HTTP Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Validation Metrics
validation_checks_total = Counter(
    'validation_checks_total',
    'Total validation checks performed',
    ['check_name', 'result'],  # result: pass or fail
    registry=registry
)

validation_requests_total = Counter(
    'validation_requests_total',
    'Total validation requests',
    ['source_type'],  # source_type: json, excel, yaml
    registry=registry
)

# File Upload Metrics
file_uploads_total = Counter(
    'file_uploads_total',
    'Total file uploads',
    ['file_type', 'status'],  # file_type: xlsx, yaml, yml; status: success, error
    registry=registry
)

# System Metrics
app_info = Gauge(
    'app_info',
    'Application information',
    ['version'],
    registry=registry
)


class MetricsCollector:
    """Helper class for collecting metrics throughout the application."""
    
    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """
        Record HTTP request metrics.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def record_validation_check(check_name: str, passed: bool):
        """
        Record validation check result.
        
        Args:
            check_name: Name of the validation check
            passed: Whether the check passed
        """
        result = "pass" if passed else "fail"
        validation_checks_total.labels(
            check_name=check_name,
            result=result
        ).inc()
    
    @staticmethod
    def record_validation_request(source_type: str):
        """
        Record validation request by source type.
        
        Args:
            source_type: Type of input source (json, excel, yaml)
        """
        validation_requests_total.labels(
            source_type=source_type
        ).inc()
    
    @staticmethod
    def record_file_upload(file_type: str, success: bool):
        """
        Record file upload.
        
        Args:
            file_type: File extension (xlsx, yaml, yml)
            success: Whether upload was successful
        """
        status = "success" if success else "error"
        file_uploads_total.labels(
            file_type=file_type,
            status=status
        ).inc()
    
    @staticmethod
    def set_app_version(version: str):
        """
        Set application version metric.
        
        Args:
            version: Application version string
        """
        app_info.labels(version=version).set(1)


def get_metrics() -> Response:
    """
    Generate Prometheus metrics response.
    
    Returns:
        FastAPI Response with Prometheus metrics
    """
    metrics_output = generate_latest(registry)
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )


# Initialize metrics collector
metrics = MetricsCollector()
