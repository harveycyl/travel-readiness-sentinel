"""
YAML file ingestion for travel itineraries.
Reads YAML files and converts them to standardized itinerary format.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Union

from .base import IngestionSource


class YAMLIngestion(IngestionSource):
    """Reads travel itinerary data from YAML files."""
    
    @property
    def source_type(self) -> str:
        """Return source type identifier."""
        return "yaml"
    
    def parse(self, source: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse YAML file and return itinerary data.
        
        Args:
            source: Path to YAML file (string or Path object)
        
        Returns:
            Dictionary containing itinerary data
        
        Raises:
            ValueError: If file cannot be read or YAML is invalid
        """
        try:
            with open(source, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"YAML file not found: {source}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to read YAML file: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("YAML file must contain a dictionary/object at the root level")
        
        return data

