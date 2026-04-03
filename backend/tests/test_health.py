"""Tests for the health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(async_client: AsyncClient):
    """Health endpoint should return HTTP 200."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_schema(async_client: AsyncClient):
    """Health endpoint response should have the expected fields."""
    response = await async_client.get("/api/health")
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "huggingface_api" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Root endpoint should return API info."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
