import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from src.excel_reader import ExcelItineraryReader
from src.model import Itinerary


class TestExcelItineraryReader:
    """Test Excel reading functionality"""
    
    @pytest.fixture
    def reader(self):
        """Fixture providing ExcelItineraryReader instance"""
        return ExcelItineraryReader()
    
    @pytest.fixture
    def valid_excel_data(self):
        """Valid Excel data structure"""
        return {
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
                'London',
                '2025-04-10',
                '2025-04-17', 
                7,
                '',
                'BA117',
                '2025-04-10',
                '',
                'BA118',
                '2025-04-17',
                '',
                'The Savoy',
                '2025-04-10',
                '2025-04-17'
            ]
        }
    
    @pytest.fixture
    def invalid_excel_data(self):
        """Invalid Excel data - missing required fields"""
        return {
            'Field': [
                'Trip Destination',
                'Trip Start Date', 
                # Missing Trip End Date
                'Total Duration (Days)',
                '',
                'Arrival Flight Number',
                'Arrival Date',
            ],
            'Value': [
                'London',
                '2025-04-10',
                7,
                '',
                'BA117',
                '2025-04-10',
            ]
        }
    
    def create_temp_excel_file(self, data):
        """Helper to create temporary Excel file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        temp_file.close()
        
        df = pd.DataFrame(data)
        df.to_excel(temp_file.name, sheet_name='Travel Itinerary', index=False)
        
        return temp_file.name
    
    def test_read_valid_excel_file(self, reader, valid_excel_data):
        """Test reading a valid Excel file"""
        temp_file = self.create_temp_excel_file(valid_excel_data)
        
        try:
            data = reader.read_excel(temp_file)
            
            # Verify structure
            assert 'trip_details' in data
            assert 'flights' in data
            assert 'accommodation' in data
            
            # Verify trip details
            trip = data['trip_details']
            assert trip['destination'] == 'London'
            assert trip['start_date'] == '2025-04-10'
            assert trip['end_date'] == '2025-04-17'
            assert trip['total_duration_days'] == 7
            
            # Verify flights
            flights = data['flights']
            assert len(flights) == 2
            
            # Check arrival flight
            arrival = next(f for f in flights if f['type'] == 'arrival')
            assert arrival['flight_number'] == 'BA117'
            assert arrival['arrival_date'] == '2025-04-10'
            
            # Check departure flight
            departure = next(f for f in flights if f['type'] == 'departure')
            assert departure['flight_number'] == 'BA118'
            assert departure['departure_date'] == '2025-04-17'
            
            # Verify accommodation
            hotel = data['accommodation']
            assert hotel['hotel_name'] == 'The Savoy'
            assert hotel['check_in'] == '2025-04-10'
            assert hotel['check_out'] == '2025-04-17'
            
        finally:
            os.unlink(temp_file)
    
    def test_read_invalid_excel_file(self, reader, invalid_excel_data):
        """Test reading an Excel file with missing required fields"""
        temp_file = self.create_temp_excel_file(invalid_excel_data)
        
        try:
            with pytest.raises(ValueError, match="Missing required"):
                reader.read_excel(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_read_nonexistent_file(self, reader):
        """Test reading a non-existent Excel file"""
        with pytest.raises(ValueError, match="Failed to read Excel file"):
            reader.read_excel("nonexistent_file.xlsx")
    
    def test_excel_to_yaml_conversion(self, reader, valid_excel_data):
        """Test converting Excel to YAML"""
        excel_file = self.create_temp_excel_file(valid_excel_data)
        yaml_file = tempfile.NamedTemporaryFile(suffix='.yaml', delete=False)
        yaml_file.close()
        
        try:
            result_yaml_path = reader.excel_to_yaml(excel_file, yaml_file.name)
            
            assert result_yaml_path == yaml_file.name
            assert Path(yaml_file.name).exists()
            
            # Verify YAML content by loading it back
            import yaml
            with open(yaml_file.name, 'r') as f:
                yaml_data = yaml.safe_load(f)
            
            # Should be able to create valid Itinerary from YAML
            itinerary = Itinerary(**yaml_data)
            assert itinerary.trip_details.destination == 'London'
            assert len(itinerary.flights) == 2
            
        finally:
            os.unlink(excel_file)
            os.unlink(yaml_file.name)
    
    def test_auto_yaml_filename_generation(self, reader, valid_excel_data):
        """Test automatic YAML filename generation"""
        excel_file = self.create_temp_excel_file(valid_excel_data)
        
        try:
            yaml_path = reader.excel_to_yaml(excel_file)
            
            # Should generate YAML file with same name as Excel
            expected_yaml = Path(excel_file).with_suffix('.yaml')
            assert yaml_path == str(expected_yaml)
            assert expected_yaml.exists()
            
        finally:
            os.unlink(excel_file)
            if Path(excel_file).with_suffix('.yaml').exists():
                os.unlink(Path(excel_file).with_suffix('.yaml'))
    
    def test_field_mapping_validation(self, reader):
        """Test that field mapping covers all required fields"""
        mapping = reader.field_mapping
        
        # Verify all essential fields are mapped
        required_fields = [
            'Trip Destination', 'Trip Start Date', 'Trip End Date', 'Total Duration (Days)',
            'Arrival Flight Number', 'Arrival Date',
            'Departure Flight Number', 'Departure Date', 
            'Hotel Name', 'Hotel Check-in Date', 'Hotel Check-out Date'
        ]
        
        for field in required_fields:
            assert field in mapping, f"Missing field mapping for: {field}"
    
    def test_empty_excel_file(self, reader):
        """Test handling of empty Excel file"""
        empty_data = {'Field': [], 'Value': []}
        temp_file = self.create_temp_excel_file(empty_data)
        
        try:
            with pytest.raises(ValueError, match="Missing required"):
                reader.read_excel(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_excel_with_extra_columns(self, reader, valid_excel_data):
        """Test Excel file with extra columns (should be ignored)"""
        # Add extra column
        valid_excel_data['Extra Column'] = [''] * len(valid_excel_data['Field'])
        
        temp_file = self.create_temp_excel_file(valid_excel_data)
        
        try:
            data = reader.read_excel(temp_file)
            # Should still work and ignore the extra column
            assert 'trip_details' in data
            assert data['trip_details']['destination'] == 'London'
        finally:
            os.unlink(temp_file)