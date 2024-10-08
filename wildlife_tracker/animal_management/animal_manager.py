from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.migration_tracking.migration_manager import MigrationManager 
from wildlife_tracker.animal_management.animal_manager import AnimalManager
from wildlife_tracker.habitat_management.habitat_manger import HabitatManager

class AnimalManager:

    def __init__(self) -> None:
        animals: dict[int, Animal] = {}

    def get_animal_by_id(self, animal_id: int) -> Optional[Animal]:
        pass

    def register_animal(Animal) -> None:
        pass

    def remove_animal(animal_id: int) -> None:
        pass

    def update_animal_details(animal_id: int, **kwargs: Any) -> None:
        pass

    def get_animal_details(animal_id) -> dict[str, Any]:
        pass

   