"""Tests for HealthStatus value object."""

from fastapi_basic_example.domain.value_objects.health_status import HealthStatus


def test_health_status_creation():
    """Test creating a health status."""
    status = HealthStatus(value="custom")
    assert status.value == "custom"


def test_healthy_factory_method():
    """Test healthy factory method."""
    status = HealthStatus.healthy()
    assert status.value == "healthy"
    assert str(status) == "healthy"


def test_unhealthy_factory_method():
    """Test unhealthy factory method."""
    status = HealthStatus.unhealthy()
    assert status.value == "unhealthy"
    assert str(status) == "unhealthy"


def test_ready_factory_method():
    """Test ready factory method."""
    status = HealthStatus.ready()
    assert status.value == "ready"
    assert str(status) == "ready"


def test_alive_factory_method():
    """Test alive factory method."""
    status = HealthStatus.alive()
    assert status.value == "alive"
    assert str(status) == "alive"


def test_started_factory_method():
    """Test started factory method."""
    status = HealthStatus.started()
    assert status.value == "started"
    assert str(status) == "started"


def test_string_representation():
    """Test string representation."""
    status = HealthStatus(value="testing")
    assert str(status) == "testing"


def test_equality():
    """Test equality comparison."""
    status1 = HealthStatus(value="healthy")
    status2 = HealthStatus(value="healthy")
    status3 = HealthStatus(value="unhealthy")

    assert status1 == status2
    assert status1 != status3


def test_immutability():
    """Test that health status is frozen."""
    status = HealthStatus(value="healthy")
    assert status.value == "healthy"
