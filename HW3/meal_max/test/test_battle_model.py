import pytest
from unittest.mock import patch, MagicMock
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture
def battle_model():
    """Fixture to create a fresh BattleModel instance for each test."""
    return BattleModel()

@pytest.fixture
def sample_meals():
    """Fixture to create sample meal objects for testing."""
    meal1 = Meal(id=1, meal="Pizza", cuisine="Italian", price=15.99, difficulty="MED")
    meal2 = Meal(id=2, meal="Burger", cuisine="American", price=12.99, difficulty="LOW")
    return meal1, meal2

class TestBattleModel:
    def test_init(self, battle_model):
        """Test BattleModel initialization."""
        assert isinstance(battle_model.combatants, list)
        assert len(battle_model.combatants) == 0

    def test_prep_combatant(self, battle_model, sample_meals):
        """Test adding a combatant to the battle."""
        meal1, _ = sample_meals
        battle_model.prep_combatant(meal1)
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0] == meal1

    def test_prep_combatant_full_list(self, battle_model, sample_meals):
        """Test adding a combatant when list is full."""
        meal1, meal2 = sample_meals
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        
        meal3 = Meal(id=3, meal="Sushi", cuisine="Japanese", price=20.99, difficulty="HIGH")
        with pytest.raises(ValueError, match="Combatant list is full"):
            battle_model.prep_combatant(meal3)

    def test_clear_combatants(self, battle_model, sample_meals):
        """Test clearing the combatants list."""
        meal1, _ = sample_meals
        battle_model.prep_combatant(meal1)
        battle_model.clear_combatants()
        assert len(battle_model.combatants) == 0

    def test_get_combatants(self, battle_model, sample_meals):
        """Test retrieving the combatants list."""
        meal1, meal2 = sample_meals
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        combatants = battle_model.get_combatants()
        assert len(combatants) == 2
        assert combatants[0] == meal1
        assert combatants[1] == meal2

    def test_get_battle_score(self, battle_model, sample_meals):
        """Test battle score calculation."""
        meal1, _ = sample_meals
        score = battle_model.get_battle_score(meal1)
        # Pizza: (15.99 * len("Italian")) - 2 (MED difficulty)
        expected_score = (15.99 * len("Italian")) - 2
        assert score == pytest.approx(expected_score, 0.001)

    def test_battle_insufficient_combatants(self, battle_model, sample_meals):
        """Test battle with insufficient combatants."""
        meal1, _ = sample_meals
        battle_model.prep_combatant(meal1)
        with pytest.raises(ValueError, match="Two combatants must be prepped"):
            battle_model.battle()

    
    
    