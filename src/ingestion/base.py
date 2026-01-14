"""
Abstract base class for all itinerary ingestion sources.
Provides a consistent interface for parsing different input formats.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IngestionSource(ABC):
    """
    Base class for all itinerary input sources (Excel, YAML, JSON, etc.).
    
    All ingestion sources must implement the parse() method to convert
    their specific format into a standardized dictionary structure that
    can be validated by the Itinerary Pydantic model.
    """
    
    @abstractmethod
    def parse(self, source: Any) -> Dict[str, Any]:
        """
        Parse the input source and return raw itinerary data.
        
        Args:
            source: Input source (file path, file object, string, etc.)
        
        Returns:
            Dictionary containing itinerary data in the expected schema format
        
        Raises:
            ValueError: If parsing fails or data is invalid
        """
        pass
    
    @property
    @abstractmethod
    def source_type(self) -> str:
        """
        Return the source type identifier for metrics and logging.
        
        Returns:
            Source type string (e.g., "excel", "yaml", "json")
        """
        pass
