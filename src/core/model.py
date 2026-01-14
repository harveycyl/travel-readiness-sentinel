from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Literal, Union
from datetime import date

class Flight(BaseModel):
    type: Literal['arrival', 'departure']
    flight_number: str
    arrival_date: Union[date, None] = None
    departure_date: Union[date, None] = None
    
    @model_validator(mode='after')
    def validate_flight_date(self):
        if self.type == 'arrival' and self.arrival_date is None:
            raise ValueError('Arrival flights must have arrival_date')
        if self.type == 'departure' and self.departure_date is None:
            raise ValueError('Departure flights must have departure_date')
        if self.type == 'arrival' and self.departure_date is not None:
            raise ValueError('Arrival flights should not have departure_date')
        if self.type == 'departure' and self.arrival_date is not None:
            raise ValueError('Departure flights should not have arrival_date')
        return self
    
    @property
    def flight_date(self) -> date:
        return self.arrival_date if self.type == 'arrival' else self.departure_date

    @field_validator('flight_number')
    def validate_flight_code(cls, v):
        if len(v) < 3:
            raise ValueError('Invalid Flight Number')
        return v

class Hotel(BaseModel):
    hotel_name: str
    check_in: date
    check_out: date

    @property
    def stay_duration(self) -> int:
        return (self.check_out - self.check_in).days

class TripContext(BaseModel):
    destination: str
    start_date: date
    end_date: date
    total_duration_days: int

class Itinerary(BaseModel):
    trip_details: TripContext
    flights: List[Flight]
    accommodation: Hotel