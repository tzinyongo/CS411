import os
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
from meal_max.utils.sql_utils import DB_PATH
import tempfile

def setup_module(module):
    """Setup function that runs before all tests"""
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    
    # Temporarily override the DB_PATH for testing
    global DB_PATH
    DB_PATH = os.path.join(temp_dir, "test.db")
    
    # Create the database and tables
    try:
        conn = sqlite3.connect(DB_PATH)
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal TEXT UNIQUE NOT NULL,
                    cuisine TEXT NOT NULL,
                    price REAL NOT NULL,
                    difficulty TEXT NOT NULL,
                    battles INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    deleted BOOLEAN DEFAULT FALSE
                );
            """)
    except sqlite3.Error as e:
        print(f"Database setup error: {e}")
        print(f"Attempted to create database at: {DB_PATH}")
        raise

@pytest.fixture
def sample_meal():
    return Meal(
        id=1,
        meal="Pizza",
        cuisine="Italian",
        price=15.99,
        difficulty="MED"
    )

@pytest.fixture
def mock_db_connection():
    with patch('meal_max.models.kitchen_model.get_db_connection') as mock:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        mock.return_value.__enter__.return_value = conn
        yield mock, conn, cursor

class TestMeal:
    def test_valid_meal_creation(self, sample_meal):
        assert sample_meal.id == 1
        assert sample_meal.meal == "Pizza"
        assert sample_meal.price == 15.99
        assert sample_meal.difficulty == "MED"

    def test_invalid_price(self):
        with pytest.raises(ValueError, match="Price must be a positive value"):
            Meal(id=1, meal="Pizza", cuisine="Italian", price=-10.0, difficulty="MED")

    def test_invalid_difficulty(self):
        with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'"):
            Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="INVALID")

class TestCreateMeal:
    def test_create_meal_success(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        create_meal("Pizza", "Italian", 15.99, "MED")
        cursor.execute.assert_called_once()
        conn.commit.assert_called_once()

    def test_create_meal_duplicate(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        cursor.execute.side_effect = sqlite3.IntegrityError
        with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
            create_meal("Pizza", "Italian", 15.99, "MED")

    def test_create_meal_invalid_price(self):
        with pytest.raises(ValueError, match="Invalid price"):
            create_meal("Pizza", "Italian", -15.99, "MED")

    def test_create_meal_invalid_difficulty(self):
        with pytest.raises(ValueError, match="Invalid difficulty level"):
            create_meal("Pizza", "Italian", 15.99, "INVALID")

class TestDeleteMeal:
    def test_delete_meal_success(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        cursor.fetchone.return_value = [False]
        delete_meal(1)
        assert cursor.execute.call_count == 2
        conn.commit.assert_called_once()

    def test_delete_meal_already_deleted(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        cursor.fetchone.return_value = [True]
        with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
            delete_meal(1)

    def test_delete_meal_not_found(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        cursor.fetchone.return_value = None
        with pytest.raises(ValueError, match="Meal with ID 1 not found"):
            delete_meal(1)

class TestGetLeaderboard:
    def test_get_leaderboard_by_wins(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchall.return_value = [(1, "Pizza", "Italian", 15.99, "MED", 10, 5, 0.5)]
        result = get_leaderboard("wins")
        assert len(result) == 1
        assert result[0]["win_pct"] == 50.0

    def test_get_leaderboard_by_win_pct(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchall.return_value = [(1, "Pizza", "Italian", 15.99, "MED", 10, 5, 0.5)]
        result = get_leaderboard("win_pct")
        assert len(result) == 1
        assert result[0]["wins"] == 5

    def test_get_leaderboard_invalid_sort(self):
        with pytest.raises(ValueError, match="Invalid sort_by parameter"):
            get_leaderboard("invalid")

class TestGetMealById:
    def test_get_meal_by_id_success(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = [1, "Pizza", "Italian", 15.99, "MED", False]
        meal = get_meal_by_id(1)
        assert isinstance(meal, Meal)
        assert meal.meal == "Pizza"

    def test_get_meal_by_id_deleted(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = [1, "Pizza", "Italian", 15.99, "MED", True]
        with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
            get_meal_by_id(1)

    def test_get_meal_by_id_not_found(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = None
        with pytest.raises(ValueError, match="Meal with ID 1 not found"):
            get_meal_by_id(1)

class TestUpdateMealStats:
    def test_update_meal_stats_win(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        cursor.fetchone.return_value = [False]
        update_meal_stats(1, "win")
        assert cursor.execute.call_count == 2
        conn.commit.assert_called_once()

    def test_update_meal_stats_loss(self, mock_db_connection):
        _, conn, cursor = mock_db_connection
        cursor.fetchone.return_value = [False]
        update_meal_stats(1, "loss")
        assert cursor.execute.call_count == 2
        conn.commit.assert_called_once()

    def test_update_meal_stats_invalid_result(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = [False]
        with pytest.raises(ValueError, match="Invalid result"):
            update_meal_stats(1, "invalid")

    def test_update_meal_stats_deleted(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = [True]
        with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
            update_meal_stats(1, "win")

    def test_update_meal_stats_not_found(self, mock_db_connection):
        _, _, cursor = mock_db_connection
        cursor.fetchone.return_value = None
        with pytest.raises(ValueError, match="Meal with ID 1 not found"):
            update_meal_stats(1, "win")