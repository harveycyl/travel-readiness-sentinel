"""
Configuration management for Travel Readiness Sentinel API.
Uses Pydantic Settings for environment-based configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Metadata
    app_name: str = "Travel Readiness Sentinel API"
    app_version: str = "1.0.0"
    app_description: str = "Automated validation engine for travel itinerary completeness"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # File Upload Limits
    max_upload_size_mb: int = 10
    allowed_file_extensions: List[str] = [".xlsx", ".yaml", ".yml"]
    
    # Observability Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    enable_metrics: bool = True
    
    # Notion Integration (Optional)
    notion_api_token: str = ""
    notion_page_id: str = ""
    
    @property
    def notion_enabled(self) -> bool:
        """Check if Notion integration is properly configured."""
        return bool(self.notion_api_token and self.notion_page_id)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
