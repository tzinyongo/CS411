import pytest
import requests
from unittest.mock import patch

from meal_max.utils.random_utils import get_random

@pytest.fixture
def mock_successful_response():
    """Fixture for mocking a successful API response."""
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.text = "0.42\n"
        mock_response.raise_for_status.return_value = None
        yield mock_get

@pytest.fixture
def mock_timeout_response():
    """Fixture for mocking a timeout response."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout
        yield mock_get

@pytest.fixture
def mock_request_exception():
    """Fixture for mocking a general request exception."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        yield mock_get

@pytest.fixture
def mock_invalid_response():
    """Fixture for mocking an invalid response format."""
    with patch('requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.text = "not_a_number\n"
        mock_response.raise_for_status.return_value = None
        yield mock_get

def test_get_random_successful(mock_successful_response):
    """Test successful random number retrieval."""
    result = get_random()
    assert isinstance(result, float)
    assert result == 0.42
    mock_successful_response.assert_called_once()

def test_get_random_timeout(mock_timeout_response):
    """Test handling of timeout exception."""
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_request_exception(mock_request_exception):
    """Test handling of general request exception."""
    with pytest.raises(RuntimeError, match="Request to random.org failed: API Error"):
        get_random()

def test_get_random_invalid_response(mock_invalid_response):
    """Test handling of invalid response format."""
    with pytest.raises(ValueError, match="Invalid response from random.org: not_a_number"):
        get_random()