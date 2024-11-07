import pytest
from unittest.mock import patch, MagicMock

from meal_max.models.battle_model import BattleModel
from ..meal_max.models.kitchen_model import Meal

@pytest.fixture
def battle_model():
    """Fixture providing a fresh BattleModel instance."""
    return BattleModel()

@pytest.fixture
def sample_meals():
    """Fixture providing sample meal instances."""
    meal1 = Meal(
        id=1,
        meal="Pizza",
        cuisine="Italian",
        price=15.99,
        difficulty="MED"
    )
    meal2 = Meal(
        id=2,
        meal="Burger",
        cuisine="American",
        price=12.99,
        difficulty="LOW"
    )
    return meal1, meal2

class TestBattleModel:
    """Test cases for BattleModel class."""

    def test_init(self, battle_model):
        """Test BattleModel initialization."""
        assert battle_model.combatants == []

    def test_prep_combatant(self, battle_model, sample_meals):
        """Test adding combatants to the battle."""
        meal1, meal2 = sample_meals
        
        battle_model.prep_combatant(meal1)
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0] == meal1

        battle_model.prep_combatant(meal2)
        assert len(battle_model.combatants) == 2
        assert battle_model.combatants[1] == meal2

    def test_prep_combatant_full(self, battle_model, sample_meals):
        """Test adding combatant when list is full."""
        meal1, meal2 = sample_meals
        
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        
        with pytest.raises(ValueError, match="Combatant list is full"):
            battle_model.prep_combatant(meal1)

    def test_clear_combatants(self, battle_model, sample_meals):
        """Test clearing combatants list."""
        meal1, _ = sample_meals
        battle_model.prep_combatant(meal1)
        battle_model.clear_combatants()
        assert len(battle_model.combatants) == 0

    def test_get_battle_score(self, battle_model, sample_meals):
        """Test battle score calculation."""
        meal1, _ = sample_meals
        score = battle_model.get_battle_score(meal1)
        
        # Score = (price * len(cuisine)) - difficulty_modifier
        expected_score = (15.99 * len("Italian")) - 2  # MED difficulty modifier is 2
        assert score == pytest.approx(expected_score, 0.01)

    def test_get_combatants(self, battle_model, sample_meals):
        """Test retrieving combatants list."""
        meal1, meal2 = sample_meals
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        
        combatants = battle_model.get_combatants()
        assert len(combatants) == 2
        assert combatants[0] == meal1
        assert combatants[1] == meal2

    @patch('meal_max.models.battle_model.get_random')
    @patch('meal_max.models.battle_model.update_meal_stats')
    def test_battle_first_wins(self, mock_update_stats, mock_random, battle_model, sample_meals):
        """Test battle where first combatant wins."""
        meal1, meal2 = sample_meals
        mock_random.return_value = 0.1  # Small random number ensures first combatant wins
        
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        
        winner = battle_model.battle()
        
        assert winner == meal1.meal
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0] == meal1
        
        # Verify stats were updated
        mock_update_stats.assert_any_call(meal1.id, 'win')
        mock_update_stats.assert_any_call(meal2.id, 'loss')

    @patch('meal_max.models.battle_model.get_random')
    @patch('meal_max.models.battle_model.update_meal_stats')
    def test_battle_second_wins(self, mock_update_stats, mock_random, battle_model, sample_meals):
        """Test battle where second combatant wins."""
        meal1, meal2 = sample_meals
        mock_random.return_value = 0.9  # Large random number ensures second combatant wins
        
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        
        winner = battle_model.battle()
        
        assert winner == meal2.meal
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0] == meal2
        
        # Verify stats were updated
        mock_update_stats.assert_any_call(meal2.id, 'win')
        mock_update_stats.assert_any_call(meal1.id, 'loss')

    def test_battle_not_enough_combatants(self, battle_model, sample_meals):
        """Test battle with insufficient combatants."""
        meal1, _ = sample_meals
        battle_model.prep_combatant(meal1)
        
        with pytest.raises(ValueError, match="Two combatants must be prepped"):
            battle_model.battle()

    @patch('meal_max.models.battle_model.get_random')
    def test_battle_score_delta(self, mock_random, battle_model, sample_meals):
        """Test battle score delta calculation."""
        meal1, meal2 = sample_meals
        mock_random.return_value = 0.5
        
        battle_model.prep_combatant(meal1)
        battle_model.prep_combatant(meal2)
        
        # Calculate expected scores
        score1 = battle_model.get_battle_score(meal1)
        score2 = battle_model.get_battle_score(meal2)
        expected_delta = abs(score1 - score2) / 100
        
        # Execute battle and verify delta calculation
        battle_model.battle()
        
        # The winner should be determined by comparing delta with mock_random value
        assert (expected_delta > 0.5) == (battle_model.combatants[0] == meal1)