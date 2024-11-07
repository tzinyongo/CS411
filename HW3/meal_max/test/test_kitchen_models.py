import pytest
import sqlite3
from unittest.mock import patch, MagicMock

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

@pytest.fixture
def mock_db_connection():
    """Fixture for mocking database connection."""
    with patch('meal_max.models.kitchen_model.get_db_connection') as mock:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        mock.return_value.__enter__.return_value = conn
        return mock, conn, cursor

@pytest.fixture
def sample_meal():
    """Fixture providing a sample meal instance."""
    return Meal(
        id=1,
        meal="Test Pizza",
        cuisine="Italian",
        price=15.99,
        difficulty="MED"
    )

class TestMeal:
    """Test cases for Meal class."""

    def test_valid_meal_creation(self):
        """Test creating a valid meal."""
        meal = Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="LOW")
        assert meal.id == 1
        assert meal.meal == "Pizza"
        assert meal.price == 10.0

    def test_invalid_price(self):
        """Test meal creation with invalid price."""
        with pytest.raises(ValueError, match="Price must be a positive value"):
            Meal(id=1, meal="Pizza", cuisine="Italian", price=-10.0, difficulty="LOW")

    def test_invalid_difficulty(self):
        """Test meal creation with invalid difficulty."""
        with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'"):
            Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="INVALID")

class TestCreateMeal:
    """Test cases for create_meal function."""

    def test_create_meal_success(self, mock_db_connection):
        """Test successful meal creation."""
        _, _, cursor = mock_db_connection
        create_meal("Pizza", "Italian", 10.0, "LOW")
        cursor.execute.assert_called_once()
        cursor.execute.assert_called_with(
            """
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
            """,
            ("Pizza", "Italian", 10.0, "LOW")
        )

    def test_create_meal_duplicate(self, mock_db_connection):
        """Test creating duplicate meal."""
        _, conn, _ = mock_db_connection
        conn.cursor.return_value.execute.side_effect = sqlite3.IntegrityError
        with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
            create_meal("Pizza", "Italian", 10.0, "LOW")

    def test_create_meal_invalid_price(self):
        """Test creating meal with invalid price."""
        with pytest.raises(ValueError, match="Invalid price"):
            create_meal("Pizza", "Italian", -10.0, "LOW")

class TestGetMealById:
    """Test cases for get_meal_by_id function."""

    def test_get_existing_meal(self, mock_db_connection, sample_meal):
        """Test retrieving existing meal by ID."""
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = (1, "Test Pizza", "Italian", 15.99, "MED", False)
        
        result = get_meal_by_id(1)
        assert isinstance(result, Meal)
        assert result.meal == sample_meal.meal
        assert result.price == sample_meal.price

    def test_get_deleted_meal(self, mock_db_connection):
        """Test retrieving deleted meal."""
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = (1, "Test Pizza", "Italian", 15.99, "MED", True)
        
        with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
            get_meal_by_id(1)

    def test_get_nonexistent_meal(self, mock_db_connection):
        """Test retrieving non-existent meal."""
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = None
        
        with pytest.raises(ValueError, match="Meal with ID 1 not found"):
            get_meal_by_id(1)

class TestGetLeaderboard:
    """Test cases for get_leaderboard function."""

    def test_get_leaderboard_wins(self, mock_db_connection):
        """Test retrieving leaderboard sorted by wins."""
        _, _, cursor = mock_db_connection
        cursor.fetchall.return_value = [
            (1, "Pizza", "Italian", 10.0, "LOW", 5, 3, 0.6),
            (2, "Burger", "American", 8.0, "MED", 4, 2, 0.5)
        ]
        
        result = get_leaderboard("wins")
        assert len(result) == 2
        assert result[0]['wins'] == 3
        assert result[0]['win_pct'] == 60.0

    def test_get_leaderboard_invalid_sort(self):
        """Test retrieving leaderboard with invalid sort parameter."""
        with pytest.raises(ValueError, match="Invalid sort_by parameter"):
            get_leaderboard("invalid")

class TestUpdateMealStats:
    """Test cases for update_meal_stats function."""

    def test_update_stats_win(self, mock_db_connection):
        """Test updating stats for a win."""
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = (False,)
        
        update_meal_stats(1, "win")
        cursor.execute.assert_any_call(
            "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?",
            (1,)
        )

    def test_update_stats_invalid_result(self, mock_db_connection):
        """Test updating stats with invalid result."""
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = (False,)
        
        with pytest.raises(ValueError, match="Invalid result"):
            update_meal_stats(1, "invalid") 