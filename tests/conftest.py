import pytest


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "0901234567"
    }


@pytest.fixture
def sample_destination_data():
    """Sample destination data for testing"""
    return {
        "destination_name": "Test Destination",
        "location_address": "Test Address",
        "destination_type": "Historical",
        "popularity_score": 80
    }
