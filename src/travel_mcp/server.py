from mcp.server.mcpserver import MCPServer


mcp = MCPServer("travel-companion")


@mcp.tool()
def get_flight_info(
    origin: str,
    destination: str,
    travel_date: str | None = None,
) -> dict:
    """
    Get flight information between two locations.

    This is currently mock data for learning MCP.
    """

    return {
        "origin": origin,
        "destination": destination,
        "travel_date": travel_date,
        "status": "success",
        "message": (
            f"Flight information from {origin} "
            f"to {destination} is currently available."
        ),
        "flights": [
            {
                "airline": "Example Airlines",
                "departure": "08:00",
                "arrival": "14:30",
                "duration": "6h 30m",
                "stops": 0,
            },
            {
                "airline": "Example Air",
                "departure": "14:00",
                "arrival": "21:15",
                "duration": "7h 15m",
                "stops": 1,
            },
        ],
    }


@mcp.tool()
def get_currency_exchange_rate(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
) -> dict:
    """
    Get currency conversion information.

    This is currently mock data for learning MCP.
    """

    rates = {
        ("USD", "SGD"): 1.28,
        ("SGD", "USD"): 0.78,
        ("INR", "SGD"): 0.015,
        ("SGD", "INR"): 66.50,
        ("EUR", "SGD"): 1.50,
        ("SGD", "EUR"): 0.67,
    }

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    rate = rates.get(
        (from_currency, to_currency)
    )

    if rate is None:
        return {
            "status": "error",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "message": (
                f"No exchange rate is configured for "
                f"{from_currency} to {to_currency}."
            ),
        }

    converted_amount = amount * rate

    return {
        "status": "success",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "exchange_rate": rate,
        "converted_amount": round(
            converted_amount,
            2,
        ),
    }


@mcp.tool()
def get_weather(
    destination: str,
) -> dict:
    """
    Get current weather information for a destination.

    This is currently mock data for learning MCP.
    """

    weather_data = {
        "Singapore": {
            "temperature_celsius": 30,
            "condition": "Partly cloudy",
            "humidity": 78,
            "precipitation_probability": 30,
        },
        "Bali": {
            "temperature_celsius": 29,
            "condition": "Sunny",
            "humidity": 75,
            "precipitation_probability": 20,
        },
    }

    weather = weather_data.get(destination)

    if weather is None:
        return {
            "status": "error",
            "destination": destination,
            "message": (
                f"No weather data is available for "
                f"{destination}."
            ),
        }

    return {
        "status": "success",
        "destination": destination,
        **weather,
    }


if __name__ == "__main__":
    mcp.run()