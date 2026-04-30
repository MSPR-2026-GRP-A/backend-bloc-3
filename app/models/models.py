from typing import Optional
from datetime import time, date
from sqlmodel import SQLModel, Field


#class HelloMessage(SQLModel, table=True):
    #id: int | None = Field(default=None, primary_key=True)
    #content: str
    #language: str


class Agency(SQLModel, table=True):
    __tablename__ = "dim_agencies"

    agency_id: str = Field(primary_key=True)
    agency_name: Optional[str] = None
    agency_url: Optional[str] = None
    agency_logo_url: Optional[str] = None


class Route(SQLModel, table=True):
    __tablename__ = "dim_routes"

    route_id: str = Field(primary_key=True)
    agency_id: Optional[str] = Field(default=None, foreign_key="dim_agencies.agency_id")
    route_short_name: Optional[str] = None
    route_long_name: Optional[str] = None
    route_desc: Optional[str] = None
    countries: Optional[str] = None
    is_active: Optional[str] = None
    picture_url: Optional[str] = None


class Calendar(SQLModel, table=True):
    __tablename__ = "dim_calendar"

    service_id: str = Field(primary_key=True)
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Stop(SQLModel, table=True):
    __tablename__ = "dim_stops"

    stop_id: str = Field(primary_key=True)
    stop_name: str
    stop_country: Optional[str] = None
    stop_lat: Optional[float] = None
    stop_lon: Optional[float] = None
    stop_timezone: Optional[str] = None


class Trip(SQLModel, table=True):
    __tablename__ = "fact_trips"

    trip_id: str = Field(primary_key=True)
    route_id: Optional[str] = Field(default=None, foreign_key="dim_routes.route_id")
    service_id: Optional[str] = Field(default=None, foreign_key="dim_calendar.service_id")
    trip_origin: Optional[str] = None
    trip_headsign: Optional[str] = None
    origin_departure_time: Optional[time] = None
    destination_arrival_time: Optional[time] = None
    duration: Optional[int] = None
    classes: Optional[str] = None
    distance: Optional[float] = None
    emissions_co2e: Optional[float] = None
    via: Optional[str] = None
    is_active: Optional[str] = None
    plugs: Optional[str] = None
    wheelchair_accessible: Optional[str] = None
    bikes_allowed: Optional[str] = None
    car_transport: Optional[str] = None


class TripStop(SQLModel, table=True):
    __tablename__ = "fact_trip_stops"

    train_stop_id: str = Field(primary_key=True)
    trip_id: Optional[str] = Field(default=None, foreign_key="fact_trips.trip_id")
    stop_id: Optional[str] = Field(default=None, foreign_key="dim_stops.stop_id")
    stop_sequence: Optional[int] = None
    arrival_time: Optional[time] = None
    departure_time: Optional[time] = None
    no_exit: Optional[str] = None
    no_entry: Optional[str] = None


class CalendarDate(SQLModel, table=True):
    __tablename__ = "fact_calendar_dates"

    uid: Optional[int] = Field(default=None, primary_key=True)
    service_id: Optional[str] = Field(default=None, foreign_key="dim_calendar.service_id")
    exception_date: Optional[date] = None
    exception_type: int