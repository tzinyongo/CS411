from typing import Any, Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.migration_tracking.migration_manager import MigrationManager 
from wildlife_tracker.animal_management.animal_manager import AnimalManager
from wildlife_tracker.habitat_management.habitat_manger import HabitatManager

class Animal:

    pass

    def __init__(self, animal_id: int, species: str, health_status: Optional[str] = None):
        self.animal_id: int = animal_id
        self.species: str = species
        self.health_status: Optional[str] = health_status
