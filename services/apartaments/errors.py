class ApartamentsNotFound(Exception):
    def __init__(self, apartament_id: int):
        self.apartament_id = apartament_id
        super().__init__(f"Apartment with id {apartament_id} not found")


class ApartamentAlreadyExists(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Apartment with name '{name}' already exists")


class InvalidFilters(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)
