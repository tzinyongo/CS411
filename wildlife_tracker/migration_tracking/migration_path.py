from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.migration_tracking.migration_manager import MigrationManager 
from wildlife_tracker.animal_management.animal_manager import AnimalManager
from wildlife_tracker.habitat_management.habitat_manger import HabitatManager


class MigrationPath:

    pass
    def __init__(self, path_id: int, species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None):
        self.path_id: int = path_id
        self.species: str = species
        self.start_location: Habitat = start_location
        self.destination: Habitat = destination
        self.duration: Optional[int] = duration

   

    def get_migration_paths() -> list[MigrationPath]:
        pass

    def get_migration_paths_by_destination(destination: Habitat) -> list[MigrationPath]:
        pass

    def get_migration_paths_by_species(species: str) -> list[MigrationPath]:
        pass

    def get_migration_paths_by_start_location(start_location: Habitat) -> list[MigrationPath]:
        pass

    def get_migration_path_details(path_id) -> dict:
        pass

    