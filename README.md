# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather data from the Open-Meteo API for VS Code and other MCP-compatible IDEs.

## Features

- **Current Weather**: Get real-time weather conditions for any location
- **Weather Forecasts**: Retrieve up to 16 days of weather forecasts
- **Geocoding**: Convert city/state names to coordinates automatically
- **Coordinate Support**: Get weather data using latitude/longitude coordinates
- **Weather Alerts**: Check for weather alerts by US state (placeholder implementation)
- **Structured Data**: Returns well-formatted weather information with proper units

## Installation

### Prerequisites

- Python 3.8+
- VS Code or another MCP-compatible IDE
- Required Python packages (see `requirements.txt`)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/NickDatLe/mcp-weather.git
cd MCP-Weather
```

2. Install required dependencies:

   **Option A: Using requirements.txt (recommended):**
   ```bash
   pip install -r requirements.txt
   ```

   **Option B: Using uv (fast and reliable):**
   ```bash
   uv pip install -r requirements.txt
   ```

   **Option C: Using conda (recommended for Apple Silicon Macs):**
   ```bash
   conda install requests pydantic geopy -c conda-forge
   pip install mcp  # Install the official MCP Python SDK
   ```

   **Option D: Manual installation:**
   ```bash
   pip install requests pydantic geopy mcp
   ```

   **Note**: The `mcp` package is the [official Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Configuration

### VS Code Setup

1. Open VS Code settings (Cmd/Ctrl + ,)
2. Search for "MCP" or navigate to Extensions > GitHub Copilot > Model Context Protocol
3. Add the following configuration to your MCP settings:

```json
{
    "servers": {
        "weatherServer": {
            "type": "stdio",
            "command": "/path/to/your/python",
            "args": ["${workspaceFolder}/weather_mcp.py"]
        }
    }
}
```

**Note**: Replace `/path/to/your/python` with your actual Python executable path. You can find this by running:
```bash
which python3
```

### Example Configuration

For a conda environment (update the environment name to match yours):
```json
{
    "servers": {
        "weatherServer": {
            "type": "stdio",
            "command": "/Users/nick/miniconda3/envs/venv/bin/python",
            "args": ["${workspaceFolder}/weather_mcp.py"]
        }
    }
}
```

## Available Tools

### 1. `get_weather`
Get weather forecast for a city by name.

**Parameters:**
- `city` (string): City name (e.g., 'Los Angeles')
- `state` (string, optional): State name or code (e.g., 'CA' or 'California')
- `country` (string, optional): Country name (default: 'USA')
- `days` (integer, optional): Number of forecast days 1-16 (default: 7)

**Example:**
```
Get weather for San Francisco, CA for the next 5 days
```

### 2. `get_weather_by_coordinates`
Get weather forecast for specific latitude/longitude coordinates.

**Parameters:**
- `latitude` (float): Location latitude
- `longitude` (float): Location longitude
- `days` (integer, optional): Number of forecast days 1-16 (default: 7)

**Example:**
```
Get weather for coordinates 37.7749, -122.4194
```

### 3. `get_alerts`
Get weather alerts for a US state (placeholder implementation).

**Parameters:**
- `state` (string): Two-letter US state code (e.g., 'CA', 'NY')

**Example:**
```
Check weather alerts for California
```

## Usage Examples

Once configured in VS Code with GitHub Copilot, you can ask natural language questions like:

- "What's the weather like in New York City?"
- "Give me a 10-day forecast for Los Angeles, California"
- "What's the current temperature in Miami, Florida?"
- "Get weather for coordinates 40.7128, -74.0060"
- "Are there any weather alerts for Texas?"

## Data Sources

- **Weather Data**: [Open-Meteo API](https://open-meteo.com/) - Free weather API with no API key required
- **Geocoding**: [Nominatim/OpenStreetMap](https://nominatim.org/) - Free geocoding service

## Response Format

The weather tools return structured data including:

### Current Weather
- Temperature and "feels like" temperature
- Humidity percentage
- Wind speed
- Precipitation amount
- Weather conditions description
- Measurement units

### Daily Forecast
- Date
- Minimum and maximum temperatures
- Precipitation amount
- Weather conditions

### Location Information
- Location name (from geocoder)
- Coordinates (latitude, longitude)

## Weather Conditions

The server interprets weather codes from Open-Meteo into human-readable descriptions:

- Clear sky, partly cloudy, overcast
- Various types of rain (light, moderate, heavy)
- Snow conditions
- Fog and freezing conditions
- Thunderstorms and hail


### Common Issues

1. **Location not found**: The geocoder couldn't find the specified location
   - Try using different variations of the city/state name
   - Check spelling of location names
   - Try including the country name

2. **Python path issues**: Make sure the Python path in your MCP configuration is correct
   - Use absolute paths to your Python executable
   - For conda environments, use the full path to the environment's Python

3. **Missing dependencies**: Install all required packages
   ```bash
   # Using requirements.txt (recommended)
   pip install -r requirements.txt
   
   # Using uv (fast)
   uv pip install -r requirements.txt
   
   # Using conda + pip
   conda install requests pydantic geopy -c conda-forge
   pip install mcp
   
   # Manual installation
   pip install requests pydantic geopy mcp
   ```

4. **Architecture issues on Apple Silicon Macs**: If you get architecture mismatch errors (x86_64 vs arm64)
   - **Recommended solution**: Create a fresh conda environment:
     ```bash
     conda deactivate
     conda remove --name your_env_name --all  # Remove existing environment
     conda create -n weather_mcp python=3.11 -y
     conda activate weather_mcp
     conda install requests pydantic geopy -c conda-forge
     pip install mcp
     ```
   - Ensure you're not mixing x86_64 and ARM64 packages
   - Use `uv pip` as an alternative which handles architecture better
   - Check your conda installation is ARM64 native: `conda info` should show `platform: osx-arm64`

5. **Permission errors**: Make sure the script is executable
   ```bash
   chmod +x weather_mcp.py
   ```

### Testing the Installation

To verify everything is working correctly:

```bash
python weather_mcp.py
```

The server should start without errors. You can then test it by configuring it in VS Code and asking weather-related questions through GitHub Copilot.

## License

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This means you can do whatever you want with this code: use it, modify it, distribute it, sell it, etc. No restrictions!

## API Limits

- Open-Meteo API: Free tier with reasonable limits for personal use
- Nominatim: Please be respectful with geocoding requests