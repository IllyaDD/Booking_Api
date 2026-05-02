class BookingNotFound(Exception):
    def __init__(self, booking_id: int):
        super().__init__(f"Booking with id {booking_id} not found")


class Checkin_earlier_than_Chekout(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(f"Check in must be before check_out")


class Dated_Already_Booked(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Dates are already booked")


class Cant_book_in_past(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Cannt book in the past")


class GuestsCountExceedsCapacity(Exception):
    def __init__(self, guests_count: int, max_guests: int) -> None:
        super().__init__(
            f"Guests count {guests_count} exceeds apartment capacity {max_guests}"
        )
