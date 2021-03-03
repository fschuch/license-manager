"""
Configuration of pytest for agent tests
"""
from unittest.mock import patch

from httpx import AsyncClient
from pytest import fixture
import respx

from licensemanager2.agent.main import app as agent_app
from licensemanager2.agent.settings import SETTINGS


@fixture
async def agent_client():
    """
    A client that can issue fake requests against endpoints in the agent
    """
    async with AsyncClient(app=agent_app, base_url="http://test") as ac:
        yield ac


@fixture(autouse=True)
def backend_setting():
    """
    Force a specific host for the backend
    """
    with patch.object(SETTINGS, "BACKEND_BASE_URL", "http://backend") as mck:
        yield mck


@fixture
def respx_mock():
    """
    Run a test in the respx context (similar to respx decorator, but it's a fixture)
    """
    with respx.mock as mock:
        yield mock
