import pytest
from datetime import date
from unittest.mock import patch
from io import StringIO
import sys
from src.model import Flight, Hotel, TripContext, Itinerary
from src.validation import (
    ReadinessCheck, 
    ArrivalAlignmentCheck, 
    DurationCoverageCheck, 
    DepartureAlignmentCheck,
    get_all_checks
)


class TestReadinessCheck:
    """Test base ReadinessCheck class"""
    
    def test_base_check_initialization(self):
        """Test ReadinessCheck base class initialization"""
        check = ReadinessCheck("Test Check")
        assert check.name == "Test Check"
    
    def test_base_check_run_not_implemented(self):
        """Test that base class run method raises NotImplementedError"""
        check = ReadinessCheck("Test Check")
        with pytest.raises(NotImplementedError):
            check.run(None)


class TestArrivalAlignmentCheck:
    """Test arrival flight and hotel check-in alignment"""
    
    @pytest.fixture
    def sample_itinerary(self):
        """Sample itinerary for testing"""
        return Itinerary(
            trip_details=TripContext(
                destination="Tokyo",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 27),
                total_duration_days=7
            ),
            flights=[
                Flight(
                    type="arrival",
                    flight_number="JL041",
                    arrival_date=date(2025, 12, 20)
                ),
                Flight(
                    type="departure",
                    flight_number="JL042",
                    departure_date=date(2025, 12, 27)
                )
            ],
            accommodation=Hotel(
                hotel_name="Shinjuku Granbell",
                check_in=date(2025, 12, 20),
                check_out=date(2025, 12, 27)
            )
        )
    
    def test_arrival_alignment_pass(self, sample_itinerary, capsys):
        """Test arrival alignment when dates match"""
        check = ArrivalAlignmentCheck("Arrival Date Alignment")
        
        result = check.run(sample_itinerary)
        
        assert result is True
        captured = capsys.readouterr()
        assert "✅ [PASS] Arrival Date Alignment" in captured.out
    
    def test_arrival_alignment_fail(self, sample_itinerary, capsys):
        """Test arrival alignment when dates don't match"""
        # Modify hotel check-in to be different from arrival
        sample_itinerary.accommodation.check_in = date(2025, 12, 21)
        
        check = ArrivalAlignmentCheck("Arrival Date Alignment")
        result = check.run(sample_itinerary)
        
        assert result is False
        captured = capsys.readouterr()
        assert "❌ [FAIL] Arrival Date Alignment" in captured.out
        assert "Flight lands on 2025-12-20" in captured.out
        assert "Hotel check-in is 2025-12-21" in captured.out


class TestDurationCoverageCheck:
    """Test hotel duration coverage validation"""
    
    @pytest.fixture
    def sample_itinerary(self):
        """Sample itinerary for testing"""
        return Itinerary(
            trip_details=TripContext(
                destination="Tokyo",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 27),
                total_duration_days=7
            ),
            flights=[
                Flight(
                    type="arrival",
                    flight_number="JL041",
                    arrival_date=date(2025, 12, 20)
                ),
                Flight(
                    type="departure",
                    flight_number="JL042",
                    departure_date=date(2025, 12, 27)
                )
            ],
            accommodation=Hotel(
                hotel_name="Shinjuku Granbell",
                check_in=date(2025, 12, 20),
                check_out=date(2025, 12, 27)
            )
        )
    
    def test_duration_coverage_pass(self, sample_itinerary, capsys):
        """Test duration coverage when hotel covers full trip"""
        check = DurationCoverageCheck("Full Accommodation Coverage")
        
        result = check.run(sample_itinerary)
        
        assert result is True
        captured = capsys.readouterr()
        assert "✅ [PASS] Full Accommodation Coverage" in captured.out
    
    def test_duration_coverage_pass_extra_nights(self, sample_itinerary, capsys):
        """Test duration coverage when hotel has extra nights"""
        # Extend hotel checkout by one day
        sample_itinerary.accommodation.check_out = date(2025, 12, 28)
        
        check = DurationCoverageCheck("Full Accommodation Coverage")
        result = check.run(sample_itinerary)
        
        assert result is True
        captured = capsys.readouterr()
        assert "✅ [PASS] Full Accommodation Coverage" in captured.out
    
    def test_duration_coverage_fail(self, sample_itinerary, capsys):
        """Test duration coverage when hotel is too short"""
        # Make hotel checkout one day early
        sample_itinerary.accommodation.check_out = date(2025, 12, 26)
        
        check = DurationCoverageCheck("Full Accommodation Coverage")
        result = check.run(sample_itinerary)
        
        assert result is False
        captured = capsys.readouterr()
        assert "❌ [FAIL] Full Accommodation Coverage" in captured.out
        assert "Trip is 7 nights" in captured.out
        assert "hotel is only 6 nights" in captured.out


class TestDepartureAlignmentCheck:
    """Test departure flight and trip end alignment"""
    
    @pytest.fixture
    def sample_itinerary(self):
        """Sample itinerary for testing"""
        return Itinerary(
            trip_details=TripContext(
                destination="Tokyo",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 27),
                total_duration_days=7
            ),
            flights=[
                Flight(
                    type="arrival",
                    flight_number="JL041",
                    arrival_date=date(2025, 12, 20)
                ),
                Flight(
                    type="departure",
                    flight_number="JL042",
                    departure_date=date(2025, 12, 27)
                )
            ],
            accommodation=Hotel(
                hotel_name="Shinjuku Granbell",
                check_in=date(2025, 12, 20),
                check_out=date(2025, 12, 27)
            )
        )
    
    def test_departure_alignment_pass(self, sample_itinerary, capsys):
        """Test departure alignment when dates match"""
        check = DepartureAlignmentCheck("Exit Strategy Alignment")
        
        result = check.run(sample_itinerary)
        
        assert result is True
        captured = capsys.readouterr()
        assert "✅ [PASS] Exit Strategy Alignment" in captured.out
    
    def test_departure_alignment_fail(self, sample_itinerary, capsys):
        """Test departure alignment when dates don't match"""
        # Change departure flight date
        sample_itinerary.flights[1].departure_date = date(2025, 12, 28)
        
        check = DepartureAlignmentCheck("Exit Strategy Alignment")
        result = check.run(sample_itinerary)
        
        assert result is False
        captured = capsys.readouterr()
        assert "❌ [FAIL] Exit Strategy Alignment" in captured.out
        assert "Trip ends on 2025-12-27" in captured.out
        assert "flight is 2025-12-28" in captured.out


class TestGetAllChecks:
    """Test the get_all_checks function"""
    
    def test_get_all_checks_returns_list(self):
        """Test that get_all_checks returns a list of checks"""
        checks = get_all_checks()
        
        assert isinstance(checks, list)
        assert len(checks) == 3
        
        # Check that all checks are ReadinessCheck instances
        for check in checks:
            assert isinstance(check, ReadinessCheck)
    
    def test_get_all_checks_correct_types(self):
        """Test that get_all_checks returns the correct check types"""
        checks = get_all_checks()
        
        check_types = [type(check).__name__ for check in checks]
        expected_types = [
            "ArrivalAlignmentCheck",
            "DurationCoverageCheck", 
            "DepartureAlignmentCheck"
        ]
        
        assert check_types == expected_types
    
    def test_get_all_checks_correct_names(self):
        """Test that get_all_checks returns checks with correct names"""
        checks = get_all_checks()
        
        check_names = [check.name for check in checks]
        expected_names = [
            "Arrival Date Alignment",
            "Full Accommodation Coverage",
            "Exit Strategy Alignment"
        ]
        
        assert check_names == expected_names


class TestIntegratedValidation:
    """Test integrated validation scenarios"""
    
    def test_perfect_itinerary_all_pass(self, capsys):
        """Test that a perfect itinerary passes all checks"""
        itinerary = Itinerary(
            trip_details=TripContext(
                destination="Tokyo",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 27),
                total_duration_days=7
            ),
            flights=[
                Flight(
                    type="arrival",
                    flight_number="JL041",
                    arrival_date=date(2025, 12, 20)
                ),
                Flight(
                    type="departure",
                    flight_number="JL042",
                    departure_date=date(2025, 12, 27)
                )
            ],
            accommodation=Hotel(
                hotel_name="Shinjuku Granbell",
                check_in=date(2025, 12, 20),
                check_out=date(2025, 12, 27)
            )
        )
        
        checks = get_all_checks()
        failures = 0
        
        for check in checks:
            if not check.run(itinerary):
                failures += 1
        
        assert failures == 0
        captured = capsys.readouterr()
        assert captured.out.count("✅ [PASS]") == 3
        assert captured.out.count("❌ [FAIL]") == 0
    
    def test_problematic_itinerary_all_fail(self, capsys):
        """Test that a problematic itinerary fails all checks"""
        itinerary = Itinerary(
            trip_details=TripContext(
                destination="Tokyo",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 27),
                total_duration_days=7
            ),
            flights=[
                Flight(
                    type="arrival",
                    flight_number="JL041",
                    arrival_date=date(2025, 12, 21)  # Misaligned arrival
                ),
                Flight(
                    type="departure",
                    flight_number="JL042",
                    departure_date=date(2025, 12, 28)  # Misaligned departure
                )
            ],
            accommodation=Hotel(
                hotel_name="Shinjuku Granbell",
                check_in=date(2025, 12, 20),
                check_out=date(2025, 12, 26)  # Insufficient coverage
            )
        )
        
        checks = get_all_checks()
        failures = 0
        
        for check in checks:
            if not check.run(itinerary):
                failures += 1
        
        assert failures == 3
        captured = capsys.readouterr()
        assert captured.out.count("✅ [PASS]") == 0
        assert captured.out.count("❌ [FAIL]") == 3