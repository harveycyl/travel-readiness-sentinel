import pytest
import yaml
import tempfile
import os
from datetime import date
from unittest.mock import patch
from io import StringIO
import sys
from src.core.model import Itinerary
from src.core.validation import get_all_checks
from src import __main__ as main


class TestMainIntegration:
    """Integration tests for the main application"""
    
    @pytest.fixture
    def valid_yaml_content(self):
        """Valid YAML content for testing"""
        return """
trip_details:
  destination: "Tokyo"
  start_date: "2025-12-20"
  end_date: "2025-12-27"
  total_duration_days: 7

flights:
  - type: "arrival"
    flight_number: "JL041"
    arrival_date: "2025-12-20"
  
  - type: "departure"
    flight_number: "JL042"
    departure_date: "2025-12-27"

accommodation:
  hotel_name: "Shinjuku Granbell"
  check_in: "2025-12-20"
  check_out: "2025-12-27"
"""
    
    @pytest.fixture
    def problematic_yaml_content(self):
        """Problematic YAML content for testing failures"""
        return """
trip_details:
  destination: "Tokyo"
  start_date: "2025-12-20"
  end_date: "2025-12-27"
  total_duration_days: 7

flights:
  - type: "arrival"
    flight_number: "JL041"
    arrival_date: "2025-12-21"
  
  - type: "departure"
    flight_number: "JL042"
    departure_date: "2025-12-28"

accommodation:
  hotel_name: "Shinjuku Granbell"
  check_in: "2025-12-20"
  check_out: "2025-12-26"
"""
    
    @pytest.fixture
    def invalid_yaml_content(self):
        """Invalid YAML content for testing validation errors"""
        return """
trip_details:
  destination: "Tokyo"
  start_date: "2025-12-20"
  end_date: "2025-12-27"
  # Missing total_duration_days

flights:
  - type: "arrival"
    flight_number: "JL"  # Invalid flight number
    arrival_date: "2025-12-20"

accommodation:
  hotel_name: "Shinjuku Granbell"
  check_in: "2025-12-20"
  check_out: "2025-12-27"
"""
    
    def create_temp_yaml_file(self, content):
        """Helper to create temporary YAML file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_load_itinerary_valid_file(self, valid_yaml_content):
        """Test loading a valid itinerary file"""
        temp_file = self.create_temp_yaml_file(valid_yaml_content)
        
        try:
            itinerary = main.load_itinerary(temp_file)
            
            assert isinstance(itinerary, Itinerary)
            assert itinerary.trip_details.destination == "Tokyo"
            assert len(itinerary.flights) == 2
            assert itinerary.accommodation.hotel_name == "Shinjuku Granbell"
        finally:
            os.unlink(temp_file)
    
    def test_load_itinerary_file_not_found(self, capsys):
        """Test loading non-existent file"""
        with pytest.raises(SystemExit) as exc_info:
            main.load_itinerary("nonexistent_file.yaml")
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: File nonexistent_file.yaml not found." in captured.out
    
    def test_load_itinerary_validation_error(self, invalid_yaml_content, capsys):
        """Test loading file with validation errors"""
        temp_file = self.create_temp_yaml_file(invalid_yaml_content)
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main.load_itinerary(temp_file)
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Data Integrity Error:" in captured.out
        finally:
            os.unlink(temp_file)
    
    @patch('sys.argv', ['main.py', '--itinerary', 'test_itinerary.yaml'])
    def test_main_successful_validation(self, valid_yaml_content, capsys):
        """Test main function with successful validation"""
        temp_file = self.create_temp_yaml_file(valid_yaml_content)
        
        try:
            with patch('sys.argv', ['main.py', '--itinerary', temp_file]):
                # Should complete normally without SystemExit
                main.main()
                
                captured = capsys.readouterr()
                assert "🔍 Ingesting Itinerary Data..." in captured.out
                assert "✈️  Validating Trip to Tokyo..." in captured.out
                assert "🎉 TRSS Status: READY FOR DEPARTURE" in captured.out
        finally:
            os.unlink(temp_file)
    
    @patch('sys.argv', ['main.py', '--itinerary', 'test_itinerary.yaml'])
    def test_main_failed_validation(self, problematic_yaml_content, capsys):
        """Test main function with failed validation"""
        temp_file = self.create_temp_yaml_file(problematic_yaml_content)
        
        try:
            with patch('sys.argv', ['main.py', '--itinerary', temp_file]):
                with pytest.raises(SystemExit) as exc_info:
                    main.main()
                
                # Should exit with code 1 (failure)
                assert exc_info.value.code == 1
                
                captured = capsys.readouterr()
                assert "🔍 Ingesting Itinerary Data..." in captured.out
                assert "✈️  Validating Trip to Tokyo..." in captured.out
                assert "🚨 TRSS Status: GROUNDED (3 Critical Errors Found)" in captured.out
        finally:
            os.unlink(temp_file)
    
    def test_main_missing_required_argument(self, capsys):
        """Test main function without required --itinerary argument"""
        with patch('sys.argv', ['main.py']):
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            
            # ArgumentParser exits with code 2 for missing required arguments
            assert exc_info.value.code == 2


class TestEndToEndScenarios:
    """End-to-end testing scenarios"""
    
    def test_perfect_tokyo_trip(self, capsys):
        """Test a perfect Tokyo trip scenario"""
        yaml_content = """
trip_details:
  destination: "Tokyo"
  start_date: "2025-03-15"
  end_date: "2025-03-22"
  total_duration_days: 7

flights:
  - type: "arrival"
    flight_number: "NH102"
    arrival_date: "2025-03-15"
  
  - type: "departure"
    flight_number: "NH103"
    departure_date: "2025-03-22"

accommodation:
  hotel_name: "Park Hyatt Tokyo"
  check_in: "2025-03-15"
  check_out: "2025-03-22"
"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_file.write(yaml_content)
        temp_file.close()
        
        try:
            with patch('sys.argv', ['main.py', '--itinerary', temp_file.name]):
                # Should complete normally without SystemExit
                main.main()
                
                captured = capsys.readouterr()
                assert "🎉 TRSS Status: READY FOR DEPARTURE" in captured.out
                assert captured.out.count("✅ [PASS]") == 3
        finally:
            os.unlink(temp_file.name)
    
    def test_business_trip_with_early_departure(self, capsys):
        """Test business trip where departure is before trip officially ends"""
        yaml_content = """
trip_details:
  destination: "London"
  start_date: "2025-06-10"
  end_date: "2025-06-15"
  total_duration_days: 5

flights:
  - type: "arrival"
    flight_number: "BA117"
    arrival_date: "2025-06-10"
  
  - type: "departure"
    flight_number: "BA118"
    departure_date: "2025-06-14"

accommodation:
  hotel_name: "The Savoy"
  check_in: "2025-06-10"
  check_out: "2025-06-15"
"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_file.write(yaml_content)
        temp_file.close()
        
        try:
            with patch('sys.argv', ['main.py', '--itinerary', temp_file.name]):
                with pytest.raises(SystemExit) as exc_info:
                    main.main()
                
                assert exc_info.value.code == 1  # Failure
                captured = capsys.readouterr()
                assert "🚨 TRSS Status: GROUNDED" in captured.out
                assert "Exit Strategy Alignment" in captured.out
                assert "❌ [FAIL]" in captured.out
        finally:
            os.unlink(temp_file.name)
    
    def test_extended_hotel_stay(self, capsys):
        """Test scenario where hotel booking extends beyond trip dates"""
        yaml_content = """
trip_details:
  destination: "Paris"
  start_date: "2025-09-01"
  end_date: "2025-09-05"
  total_duration_days: 4

flights:
  - type: "arrival"
    flight_number: "AF83"
    arrival_date: "2025-09-01"
  
  - type: "departure"
    flight_number: "AF84"
    departure_date: "2025-09-05"

accommodation:
  hotel_name: "Hotel Plaza Athénée"
  check_in: "2025-09-01"
  check_out: "2025-09-07"
"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_file.write(yaml_content)
        temp_file.close()
        
        try:
            with patch('sys.argv', ['main.py', '--itinerary', temp_file.name]):
                # Should pass - extra hotel nights are okay
                main.main()
                
                captured = capsys.readouterr()
                assert "🎉 TRSS Status: READY FOR DEPARTURE" in captured.out
                assert captured.out.count("✅ [PASS]") == 3
        finally:
            os.unlink(temp_file.name)