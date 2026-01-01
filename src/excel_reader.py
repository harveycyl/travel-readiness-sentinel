import pandas as pd
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class ExcelItineraryReader:
    """Reads travel itinerary data from Excel files and converts to YAML format"""
    
    def __init__(self):
        self.field_mapping = {
            'Trip Destination': ('trip_details', 'destination'),
            'Trip Start Date': ('trip_details', 'start_date'),
            'Trip End Date': ('trip_details', 'end_date'),
            'Total Duration (Days)': ('trip_details', 'total_duration_days'),
            'Arrival Flight Number': ('flights', 'arrival', 'flight_number'),
            'Arrival Date': ('flights', 'arrival', 'arrival_date'),
            'Departure Flight Number': ('flights', 'departure', 'flight_number'),
            'Departure Date': ('flights', 'departure', 'departure_date'),
            'Hotel Name': ('accommodation', 'hotel_name'),
            'Hotel Check-in Date': ('accommodation', 'check_in'),
            'Hotel Check-out Date': ('accommodation', 'check_out')
        }
    
    def read_excel(self, excel_path: str) -> Dict[str, Any]:
        """Read Excel file and convert to itinerary dictionary"""
        try:
            df = pd.read_excel(excel_path, sheet_name='Travel Itinerary')
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {e}")
        
        # Create the data structure
        data = {
            'trip_details': {},
            'flights': [],
            'accommodation': {}
        }
        
        # Process each row
        for _, row in df.iterrows():
            field = str(row.get('Field', '')).strip()
            value = row.get('Value', '')
            
            # Skip empty fields or rows
            if not field or pd.isna(value) or str(value).strip() == '':
                continue
                
            if field in self.field_mapping:
                self._set_nested_value(data, field, value)
        
        # Validate required fields
        self._validate_data(data)
        
        # Format flights as list
        self._format_flights(data)
        
        return data
    
    def _set_nested_value(self, data: Dict[str, Any], field: str, value: Any):
        """Set nested dictionary value based on field mapping"""
        path = self.field_mapping[field]
        
        if path[0] == 'trip_details':
            if path[1] == 'total_duration_days':
                data['trip_details'][path[1]] = int(value)
            else:
                data['trip_details'][path[1]] = str(value).strip()
                
        elif path[0] == 'flights':
            # Initialize flight type if not exists
            if path[1] not in data:
                data[path[1]] = {}
            data[path[1]][path[2]] = str(value).strip()
            data[path[1]]['type'] = path[1]
            
        elif path[0] == 'accommodation':
            data['accommodation'][path[1]] = str(value).strip()
    
    def _format_flights(self, data: Dict[str, Any]):
        """Convert flight dictionaries to proper list format"""
        flights = []
        
        # Add arrival flight if exists
        if 'arrival' in data and 'flight_number' in data['arrival']:
            flights.append(data['arrival'])
        
        # Add departure flight if exists  
        if 'departure' in data and 'flight_number' in data['departure']:
            flights.append(data['departure'])
        
        # Clean up temporary flight data
        data.pop('arrival', None)
        data.pop('departure', None)
        data['flights'] = flights
    
    def _validate_data(self, data: Dict[str, Any]):
        """Basic validation of required fields"""
        required_trip_fields = ['destination', 'start_date', 'end_date', 'total_duration_days']
        required_accommodation_fields = ['hotel_name', 'check_in', 'check_out']
        
        # Check trip details
        for field in required_trip_fields:
            if field not in data.get('trip_details', {}):
                raise ValueError(f"Missing required trip detail: {field}")
        
        # Check accommodation
        for field in required_accommodation_fields:
            if field not in data.get('accommodation', {}):
                raise ValueError(f"Missing required accommodation detail: {field}")
        
        # Check flights
        if 'arrival' not in data or 'flight_number' not in data.get('arrival', {}):
            raise ValueError("Missing arrival flight information")
        
        if 'departure' not in data or 'flight_number' not in data.get('departure', {}):
            raise ValueError("Missing departure flight information")
    
    def excel_to_yaml(self, excel_path: str, yaml_path: str = None) -> str:
        """Convert Excel file to YAML file"""
        data = self.read_excel(excel_path)
        
        if yaml_path is None:
            # Generate YAML filename based on Excel filename
            excel_file = Path(excel_path)
            yaml_path = excel_file.with_suffix('.yaml')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return str(yaml_path)


def create_sample_excel():
    """Create a sample Excel file with example data"""
    import pandas as pd
    
    data = {
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
            'Paris',
            '2025-06-15',
            '2025-06-22', 
            '7',
            '',
            'AF83',
            '2025-06-15',
            '',
            'AF84',
            '2025-06-22',
            '',
            'Hotel Plaza Athénée',
            '2025-06-15',
            '2025-06-22'
        ],
        'Format/Notes': [
            'Text (e.g., Tokyo, Paris, London)',
            'YYYY-MM-DD format',
            'YYYY-MM-DD format',
            'Number of days',
            '',
            'Airline code + number (e.g., JL041, BA117)',
            'YYYY-MM-DD format',
            '',
            'Airline code + number (e.g., JL042, BA118)', 
            'YYYY-MM-DD format',
            '',
            'Hotel name or accommodation',
            'YYYY-MM-DD format',
            'YYYY-MM-DD format'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('itinerary_sample.xlsx', sheet_name='Travel Itinerary', index=False)
    return 'itinerary_sample.xlsx'


if __name__ == "__main__":
    # Test the Excel reader
    reader = ExcelItineraryReader()
    
    # Create sample Excel
    excel_file = create_sample_excel()
    print(f"Created sample Excel: {excel_file}")
    
    # Convert to YAML
    yaml_file = reader.excel_to_yaml(excel_file)
    print(f"Converted to YAML: {yaml_file}")
    
    # Display the YAML content
    with open(yaml_file, 'r') as f:
        print("\nGenerated YAML content:")
        print(f.read())