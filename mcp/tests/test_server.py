"""Tests for the weather MCP server."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from weather.server import format_alert, get_alerts, get_forecast, make_nws_request

# ---------------------------------------------------------------------------
# make_nws_request
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_make_nws_request_success() -> None:
    payload = {"properties": {"forecast": "https://api.weather.gov/gridpoints/XXX"}}
    mock_response = MagicMock()
    mock_response.json.return_value = payload
    mock_response.raise_for_status = MagicMock()

    with patch("weather.server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await make_nws_request("https://api.weather.gov/points/40,-75")

    assert result == payload


@pytest.mark.asyncio
async def test_make_nws_request_http_error() -> None:
    with patch("weather.server.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await make_nws_request("https://api.weather.gov/bad-url")

    assert result is None


# ---------------------------------------------------------------------------
# format_alert
# ---------------------------------------------------------------------------


def _make_feature(props: dict[str, Any]) -> dict[str, Any]:
    return {"properties": props}


def test_format_alert_full() -> None:
    feature = _make_feature(
        {
            "event": "Tornado Warning",
            "areaDesc": "Central TX",
            "severity": "Extreme",
            "description": "A tornado was spotted.",
            "instruction": "Take shelter immediately.",
        }
    )
    result = format_alert(feature)
    assert "Tornado Warning" in result
    assert "Central TX" in result
    assert "Extreme" in result
    assert "A tornado was spotted." in result
    assert "Take shelter immediately." in result


def test_format_alert_missing_fields() -> None:
    feature = _make_feature({})
    result = format_alert(feature)
    assert "Unknown" in result
    assert "No description available" in result
    assert "No specific instructions provided" in result


# ---------------------------------------------------------------------------
# get_alerts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_alerts_returns_formatted_alerts() -> None:
    mock_data = {
        "features": [
            _make_feature(
                {
                    "event": "Flood Watch",
                    "areaDesc": "South FL",
                    "severity": "Moderate",
                    "description": "Heavy rainfall expected.",
                    "instruction": "Monitor conditions.",
                }
            )
        ]
    }

    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_data
        result = await get_alerts("FL")

    assert "Flood Watch" in result
    assert "South FL" in result


@pytest.mark.asyncio
async def test_get_alerts_no_features() -> None:
    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"features": []}
        result = await get_alerts("CA")

    assert result == "No active alerts for this state."


@pytest.mark.asyncio
async def test_get_alerts_api_failure() -> None:
    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = None
        result = await get_alerts("TX")

    assert result == "Unable to fetch alerts or no alerts found."


@pytest.mark.asyncio
async def test_get_alerts_missing_features_key() -> None:
    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"something_else": []}
        result = await get_alerts("NY")

    assert result == "Unable to fetch alerts or no alerts found."


@pytest.mark.asyncio
async def test_get_alerts_multiple_alerts_joined() -> None:
    mock_data = {
        "features": [
            _make_feature(
                {"event": "Alert A", "areaDesc": "Area 1", "severity": "Minor"}
            ),
            _make_feature(
                {"event": "Alert B", "areaDesc": "Area 2", "severity": "Severe"}
            ),
        ]
    }

    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_data
        result = await get_alerts("WA")

    assert "Alert A" in result
    assert "Alert B" in result
    assert "---" in result


# ---------------------------------------------------------------------------
# get_forecast
# ---------------------------------------------------------------------------

_POINTS_RESPONSE: dict[str, Any] = {
    "properties": {"forecast": "https://api.weather.gov/gridpoints/PHI/50,60/forecast"}
}

_FORECAST_RESPONSE: dict[str, Any] = {
    "properties": {
        "periods": [
            {
                "name": "Tonight",
                "temperature": 55,
                "temperatureUnit": "F",
                "windSpeed": "10 mph",
                "windDirection": "NW",
                "detailedForecast": "Clear skies.",
            },
            {
                "name": "Wednesday",
                "temperature": 72,
                "temperatureUnit": "F",
                "windSpeed": "5 mph",
                "windDirection": "S",
                "detailedForecast": "Partly sunny.",
            },
        ]
    }
}


@pytest.mark.asyncio
async def test_get_forecast_success() -> None:
    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = [_POINTS_RESPONSE, _FORECAST_RESPONSE]
        result = await get_forecast(40.0, -75.0)

    assert "Tonight" in result
    assert "55°F" in result
    assert "Wednesday" in result
    assert "---" in result


@pytest.mark.asyncio
async def test_get_forecast_points_failure() -> None:
    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = None
        result = await get_forecast(40.0, -75.0)

    assert result == "Unable to fetch forecast data for this location."


@pytest.mark.asyncio
async def test_get_forecast_forecast_failure() -> None:
    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = [_POINTS_RESPONSE, None]
        result = await get_forecast(40.0, -75.0)

    assert result == "Unable to fetch detailed forecast."


@pytest.mark.asyncio
async def test_get_forecast_limits_to_five_periods() -> None:
    many_periods = [
        {
            "name": f"Period {i}",
            "temperature": 60 + i,
            "temperatureUnit": "F",
            "windSpeed": "5 mph",
            "windDirection": "N",
            "detailedForecast": f"Details for period {i}.",
        }
        for i in range(10)
    ]
    forecast_resp: dict[str, Any] = {"properties": {"periods": many_periods}}

    with patch("weather.server.make_nws_request", new_callable=AsyncMock) as mock_req:
        mock_req.side_effect = [_POINTS_RESPONSE, forecast_resp]
        result = await get_forecast(40.0, -75.0)

    assert "Period 0" in result
    assert "Period 4" in result
    assert "Period 5" not in result
