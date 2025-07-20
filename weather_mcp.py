"""
Weather MCP Server for VSCode
Exposes weather data from Open-Meteo API as MCP tools
"""

import requests
from typing import Optional, TypedDict, List
from pydantic import BaseModel, Field
from geopy.geocoders import Nominatim

# Import MCP SDK
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("weather")

# Define structured output models


class CurrentWeather(BaseModel):
    """Current weather conditions"""
    temperature: float = Field(description="Temperature in degrees")
    feels_like: float = Field(description="Apparent temperature")
    humidity: float = Field(description="Relative humidity percentage")
    wind_speed: float = Field(description="Wind speed")
    precipitation: float = Field(description="Precipitation amount")
    conditions: str = Field(description="Weather conditions description")
    units: dict = Field(description="Measurement units")


class DailyForecast(BaseModel):
    """Daily weather forecast"""
    date: str = Field(description="Forecast date")
    min_temp: float = Field(description="Minimum temperature")
    max_temp: float = Field(description="Maximum temperature")
    precipitation: float = Field(description="Precipitation amount")
    conditions: str = Field(description="Weather conditions description")


class WeatherResponse(BaseModel):
    """Complete weather response"""
    location: str = Field(description="Location name")
    coordinates: tuple = Field(description="Latitude and longitude")
    current: CurrentWeather = Field(description="Current weather conditions")
    forecast: List[DailyForecast] = Field(description="Daily weather forecast")


class LocationCoordinates(TypedDict):
    """Location coordinates result"""
    latitude: float
    longitude: float
    location_name: str


def geocode_location(city: str, state: Optional[str] = None, country: str = "USA") -> Optional[LocationCoordinates]:
    """
    Convert city and state to latitude and longitude coordinates

    Args:
        city: City name
        state: State name or code (optional)
        country: Country name (default: USA)

    Returns:
        Location coordinates or None if not found
    """
    try:
        # Initialize geolocator with a user agent
        geolocator = Nominatim(user_agent="weather_mcp_server")

        # Build query string
        query = city
        if state:
            query += f", {state}"
        if country:
            query += f", {country}"

        print(f"[DEBUG] Geocoding query: {query}")  # Enhanced debug info
        print(f"[DEBUG] Function called with: city={city}, state={state}, country={country}")
        
        # Get location with increased timeout
        location = geolocator.geocode(query, timeout=15)

        if location:
            print(f"[DEBUG] Found location: {location.latitude}, {location.longitude}")  # Enhanced debug info
            print(f"[DEBUG] Address: {location.address}")
            return LocationCoordinates(
                latitude=location.latitude,
                longitude=location.longitude,
                location_name=location.address  # Use the full address from geocoder
            )
        else:
            print(f"[DEBUG] No location found for query: {query}")  # Enhanced debug info
            return None
    except Exception as e:
        print(f"Error during geocoding: {e}")
        return None


def get_weather_data(latitude: float, longitude: float, days: int = 7):
    """
    Fetch weather data from Open-Meteo API

    Args:
        latitude: Location latitude
        longitude: Location longitude
        days: Number of forecast days (1-16)

    Returns:
        Weather data including current conditions and forecast
    """
    # Ensure days is within valid range
    days = min(max(1, days), 16)

    # Build API URL with parameters
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "weather_code", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "auto",
        "forecast_days": days
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def interpret_weather_code(code):
    """Convert weather code to human-readable description"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")


def process_weather_data(data, location_name):
    """Process raw weather data into structured format"""
    if not data:
        return None

    # Process current weather
    current = data.get("current", {})
    current_units = data.get("current_units", {})

    if not current:
        return None

    # Create current weather object
    current_weather = CurrentWeather(
        temperature=current.get("temperature_2m"),
        feels_like=current.get("apparent_temperature"),
        humidity=current.get("relative_humidity_2m"),
        wind_speed=current.get("wind_speed_10m"),
        precipitation=current.get("precipitation"),
        conditions=interpret_weather_code(current.get("weather_code", 0)),
        units={
            "temperature": current_units.get("temperature_2m", "°C"),
            "feels_like": current_units.get("apparent_temperature", "°C"),
            "humidity": current_units.get("relative_humidity_2m", "%"),
            "wind_speed": current_units.get("wind_speed_10m", "km/h"),
            "precipitation": current_units.get("precipitation", "mm")
        }
    )

    # Process forecast
    daily = data.get("daily", {})
    forecast_list = []

    if daily and "time" in daily:
        for i, date in enumerate(daily["time"]):
            if i < len(daily.get("weather_code", [])):
                forecast_list.append(
                    DailyForecast(
                        date=date,
                        min_temp=daily.get("temperature_2m_min", [])[i] if i < len(
                            daily.get("temperature_2m_min", [])) else 0,
                        max_temp=daily.get("temperature_2m_max", [])[i] if i < len(
                            daily.get("temperature_2m_max", [])) else 0,
                        precipitation=daily.get("precipitation_sum", [])[i] if i < len(
                            daily.get("precipitation_sum", [])) else 0,
                        conditions=interpret_weather_code(
                            daily.get("weather_code", [])[i])
                    )
                )

    # Create complete response
    return WeatherResponse(
        location=location_name,
        coordinates=(data.get("latitude"), data.get("longitude")),
        current=current_weather,
        forecast=forecast_list
    )

# MCP Tool: Get weather by city and state


@mcp.tool()
def get_weather(city: str, state: Optional[str] = None, country: str = "USA", days: int = 7) -> WeatherResponse:
    """
    Get weather forecast for a city

    Args:
        city: City name (e.g., 'Los Angeles')
        state: State name or code (e.g., 'CA' or 'California')
        country: Country name (default: USA)
        days: Number of forecast days (1-16)

    Returns:
        Weather data including current conditions and forecast
    """
    # Get coordinates for the location
    location = geocode_location(city, state, country)

    if not location:
        # If geocoding fails, return an error instead of defaulting to Los Angeles
        error_message = f"Could not find coordinates for {city}"
        if state:
            error_message += f", {state}"
        error_message += f", {country}. Please check the location name and try again."
        
        # Return a structured error response
        return WeatherResponse(
            location=f"Error: {error_message}",
            coordinates=(0.0, 0.0),
            current=CurrentWeather(
                temperature=0.0,
                feels_like=0.0,
                humidity=0.0,
                wind_speed=0.0,
                precipitation=0.0,
                conditions="Location not found",
                units={}
            ),
            forecast=[]
        )

    # Get weather data
    weather_data = get_weather_data(
        location["latitude"], location["longitude"], days)

    # Process and return structured data
    return process_weather_data(weather_data, location["location_name"])

# MCP Tool: Get weather by coordinates


@mcp.tool()
def get_weather_by_coordinates(latitude: float, longitude: float, days: int = 7) -> WeatherResponse:
    """
    Get weather forecast for specific coordinates

    Args:
        latitude: Location latitude
        longitude: Location longitude
        days: Number of forecast days (1-16)

    Returns:
        Weather data including current conditions and forecast
    """
    # Get weather data
    weather_data = get_weather_data(latitude, longitude, days)

    # Process and return structured data
    return process_weather_data(weather_data, f"coordinates ({latitude}, {longitude})")

# MCP Tool: Get weather alerts for a US state


@mcp.tool()
def get_alerts(state: str) -> dict:
    """
    Get weather alerts for a US state

    Args:
        state: Two-letter US state code (e.g. CA, NY)

    Returns:
        Dictionary with alert information
    """
    # This is a placeholder - in a real implementation, you would call a weather alerts API
    return {
        "result": f"No active weather alerts for {state}",
        "state": state,
        "alerts_count": 0
    }


if __name__ == "__main__":
    # Start the MCP server
    mcp.run()
