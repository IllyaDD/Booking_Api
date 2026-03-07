class AmenityNotFound(Exception):
    def __init__(self, amenity_id: int):
        self.amenity_id = amenity_id
        super().__init__(f"Amenity with id {amenity_id} not found")


class AmenityAlreadyExists(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Amenity with name '{name}' already exists")
