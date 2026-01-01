from .model import Itinerary

class ReadinessCheck:
    """
    Base class for all checks. 
    Mapped from: AuditAssertion (Completeness, Accuracy, Cut-off).
    """
    def __init__(self, name: str):
        self.name = name

    def run(self, data: Itinerary) -> bool:
        raise NotImplementedError

class ArrivalAlignmentCheck(ReadinessCheck):
    """
    Check 1: Does flight arrival match hotel check-in?
    """
    def run(self, data: Itinerary) -> bool:
        arrival_flight = next(f for f in data.flights if f.type == 'arrival')
        
        if arrival_flight.flight_date == data.accommodation.check_in:
            print(f"✅ [PASS] {self.name}")
            return True
        else:
            print(f"❌ [FAIL] {self.name}: Flight lands on {arrival_flight.flight_date}, but Hotel check-in is {data.accommodation.check_in}")
            return False

class DurationCoverageCheck(ReadinessCheck):
    """
    Check 2: Does the hotel cover the full trip duration?
    """
    def run(self, data: Itinerary) -> bool:
        trip_days = data.trip_details.total_duration_days
        hotel_days = data.accommodation.stay_duration
        
        if hotel_days >= trip_days:
            print(f"✅ [PASS] {self.name}")
            return True
        else:
            print(f"❌ [FAIL] {self.name}: Gap Detected! Trip is {trip_days} nights, but hotel is only {hotel_days} nights.")
            return False

class DepartureAlignmentCheck(ReadinessCheck):
    """
    Check 3: Does departure flight match trip end date?
    """
    def run(self, data: Itinerary) -> bool:
        dept_flight = next(f for f in data.flights if f.type == 'departure')
        
        if dept_flight.flight_date == data.trip_details.end_date:
            print(f"✅ [PASS] {self.name}")
            return True
        else:
            print(f"❌ [FAIL] {self.name}: Visa Risk! Trip ends on {data.trip_details.end_date} but flight is {dept_flight.flight_date}")
            return False

def get_all_checks():
    return [
        ArrivalAlignmentCheck("Arrival Date Alignment"),
        DurationCoverageCheck("Full Accommodation Coverage"),
        DepartureAlignmentCheck("Exit Strategy Alignment")
    ]