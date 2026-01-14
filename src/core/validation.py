"""
Validation checks for travel itinerary readiness.
Refactored to return structured results for both CLI and API usage.
"""
from dataclasses import dataclass
from typing import List
from .model import Itinerary


@dataclass
class CheckResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str


class ReadinessCheck:
    """
    Base class for all checks. 
    Mapped from: AuditAssertion (Completeness, Accuracy, Cut-off).
    """
    def __init__(self, name: str):
        self.name = name

    def run(self, data: Itinerary) -> CheckResult:
        """Run the check and return structured result."""
        raise NotImplementedError


class ArrivalAlignmentCheck(ReadinessCheck):
    """
    Check 1: Does flight arrival match hotel check-in?
    """
    def run(self, data: Itinerary) -> CheckResult:
        arrival_flight = next(f for f in data.flights if f.type == 'arrival')
        
        if arrival_flight.flight_date == data.accommodation.check_in:
            return CheckResult(
                check_name=self.name,
                passed=True,
                message=f"Flight arrival ({arrival_flight.flight_date}) matches hotel check-in"
            )
        else:
            return CheckResult(
                check_name=self.name,
                passed=False,
                message=f"Flight lands on {arrival_flight.flight_date}, but Hotel check-in is {data.accommodation.check_in}"
            )


class DurationCoverageCheck(ReadinessCheck):
    """
    Check 2: Does the hotel cover the full trip duration?
    """
    def run(self, data: Itinerary) -> CheckResult:
        trip_days = data.trip_details.total_duration_days
        hotel_days = data.accommodation.stay_duration
        
        if hotel_days >= trip_days:
            return CheckResult(
                check_name=self.name,
                passed=True,
                message=f"Hotel covers full trip duration ({hotel_days} nights >= {trip_days} nights)"
            )
        else:
            return CheckResult(
                check_name=self.name,
                passed=False,
                message=f"Gap Detected! Trip is {trip_days} nights, but hotel is only {hotel_days} nights."
            )


class DepartureAlignmentCheck(ReadinessCheck):
    """
    Check 3: Does departure flight match trip end date?
    """
    def run(self, data: Itinerary) -> CheckResult:
        dept_flight = next(f for f in data.flights if f.type == 'departure')
        
        if dept_flight.flight_date == data.trip_details.end_date:
            return CheckResult(
                check_name=self.name,
                passed=True,
                message=f"Departure flight ({dept_flight.flight_date}) matches trip end date"
            )
        else:
            return CheckResult(
                check_name=self.name,
                passed=False,
                message=f"Visa Risk! Trip ends on {data.trip_details.end_date} but flight is {dept_flight.flight_date}"
            )


def get_all_checks() -> List[ReadinessCheck]:
    """Get all validation checks."""
    return [
        ArrivalAlignmentCheck("Arrival Date Alignment"),
        DurationCoverageCheck("Full Accommodation Coverage"),
        DepartureAlignmentCheck("Exit Strategy Alignment")
    ]


def run_all_checks(itinerary: Itinerary) -> List[CheckResult]:
    """
    Run all validation checks and return structured results.
    Useful for API endpoints.
    """
    checks = get_all_checks()
    return [check.run(itinerary) for check in checks]