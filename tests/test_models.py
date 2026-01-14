import pytest
from datetime import date
from pydantic import ValidationError
from src.core.model import Flight, Hotel, TripContext, Itinerary


class TestFlight:
    """Test Flight model validation and behavior"""
    
    def test_valid_arrival_flight(self):
        """Test creating a valid arrival flight"""
        flight = Flight(
            type="arrival",
            flight_number="JL041",
            arrival_date=date(2025, 12, 20)
        )
        assert flight.type == "arrival"
        assert flight.flight_number == "JL041"
        assert flight.flight_date == date(2025, 12, 20)
    
    def test_valid_departure_flight(self):
        """Test creating a valid departure flight"""
        flight = Flight(
            type="departure",
            flight_number="JL042",
            departure_date=date(2025, 12, 27)
        )
        assert flight.type == "departure"
        assert flight.flight_number == "JL042"
        assert flight.flight_date == date(2025, 12, 27)
    
    def test_arrival_flight_missing_arrival_date(self):
        """Test that arrival flights require arrival_date"""
        with pytest.raises(ValidationError, match="Arrival flights must have arrival_date"):
            Flight(
                type="arrival",
                flight_number="JL041"
            )
    
    def test_departure_flight_missing_departure_date(self):
        """Test that departure flights require departure_date"""
        with pytest.raises(ValidationError, match="Departure flights must have departure_date"):
            Flight(
                type="departure",
                flight_number="JL042"
            )
    
    def test_arrival_flight_with_departure_date(self):
        """Test that arrival flights cannot have departure_date"""
        with pytest.raises(ValidationError, match="Arrival flights should not have departure_date"):
            Flight(
                type="arrival",
                flight_number="JL041",
                arrival_date=date(2025, 12, 20),
                departure_date=date(2025, 12, 27)
            )
    
    def test_departure_flight_with_arrival_date(self):
        """Test that departure flights cannot have arrival_date"""
        with pytest.raises(ValidationError, match="Departure flights should not have arrival_date"):
            Flight(
                type="departure",
                flight_number="JL042",
                arrival_date=date(2025, 12, 20),
                departure_date=date(2025, 12, 27)
            )
    
    def test_invalid_flight_number(self):
        """Test flight number validation"""
        with pytest.raises(ValidationError, match="Invalid Flight Number"):
            Flight(
                type="arrival",
                flight_number="JL",
                arrival_date=date(2025, 12, 20)
            )
    
    def test_flight_number_validation_passes(self):
        """Test valid flight numbers pass validation"""
        flight = Flight(
            type="arrival",
            flight_number="ABC123",
            arrival_date=date(2025, 12, 20)
        )
        assert flight.flight_number == "ABC123"


class TestHotel:
    """Test Hotel model validation and behavior"""
    
    def test_valid_hotel(self):
        """Test creating a valid hotel booking"""
        hotel = Hotel(
            hotel_name="Shinjuku Granbell",
            check_in=date(2025, 12, 20),
            check_out=date(2025, 12, 27)
        )
        assert hotel.hotel_name == "Shinjuku Granbell"
        assert hotel.check_in == date(2025, 12, 20)
        assert hotel.check_out == date(2025, 12, 27)
    
    def test_stay_duration_calculation(self):
        """Test that stay_duration calculates correctly"""
        hotel = Hotel(
            hotel_name="Test Hotel",
            check_in=date(2025, 12, 20),
            check_out=date(2025, 12, 27)
        )
        assert hotel.stay_duration == 7
    
    def test_stay_duration_one_night(self):
        """Test stay_duration for one night"""
        hotel = Hotel(
            hotel_name="Test Hotel",
            check_in=date(2025, 12, 20),
            check_out=date(2025, 12, 21)
        )
        assert hotel.stay_duration == 1


class TestTripContext:
    """Test TripContext model validation"""
    
    def test_valid_trip_context(self):
        """Test creating valid trip context"""
        trip = TripContext(
            destination="Tokyo",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 27),
            total_duration_days=7
        )
        assert trip.destination == "Tokyo"
        assert trip.start_date == date(2025, 12, 20)
        assert trip.end_date == date(2025, 12, 27)
        assert trip.total_duration_days == 7


class TestItinerary:
    """Test complete Itinerary model"""
    
    @pytest.fixture
    def sample_itinerary_data(self):
        """Fixture providing sample itinerary data"""
        return {
            "trip_details": {
                "destination": "Tokyo",
                "start_date": "2025-12-20",
                "end_date": "2025-12-27",
                "total_duration_days": 7
            },
            "flights": [
                {
                    "type": "arrival",
                    "flight_number": "JL041",
                    "arrival_date": "2025-12-20"
                },
                {
                    "type": "departure",
                    "flight_number": "JL042",
                    "departure_date": "2025-12-27"
                }
            ],
            "accommodation": {
                "hotel_name": "Shinjuku Granbell",
                "check_in": "2025-12-20",
                "check_out": "2025-12-27"
            }
        }
    
    def test_valid_complete_itinerary(self, sample_itinerary_data):
        """Test creating a complete valid itinerary"""
        itinerary = Itinerary(**sample_itinerary_data)
        
        assert itinerary.trip_details.destination == "Tokyo"
        assert len(itinerary.flights) == 2
        assert itinerary.accommodation.hotel_name == "Shinjuku Granbell"
    
    def test_itinerary_with_missing_fields(self):
        """Test itinerary validation with missing required fields"""
        incomplete_data = {
            "trip_details": {
                "destination": "Tokyo",
                "start_date": "2025-12-20",
                "end_date": "2025-12-27"
                # Missing total_duration_days
            }
        }
        
        with pytest.raises(ValidationError):
            Itinerary(**incomplete_data)
    
    def test_itinerary_date_parsing(self, sample_itinerary_data):
        """Test that string dates are properly parsed"""
        itinerary = Itinerary(**sample_itinerary_data)
        
        assert itinerary.trip_details.start_date == date(2025, 12, 20)
        assert itinerary.trip_details.end_date == date(2025, 12, 27)
        assert itinerary.accommodation.check_in == date(2025, 12, 20)
        assert itinerary.accommodation.check_out == date(2025, 12, 27)