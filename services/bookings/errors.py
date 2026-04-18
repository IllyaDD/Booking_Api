class BookingNotFound(Exception):
    def __init__(self, booking_id: int):
        super().__init__(f"Booking with id {booking_id} not found")
