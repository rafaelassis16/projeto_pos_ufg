from dataclasses import dataclass
from datetime import date, time


class InvalidReservationError(ValueError):
    """Raised when a reservation breaks a business rule."""


@dataclass(frozen=True)
class Reservation:
    """Represents a room reservation request.

    Attributes:
        room_id: Identifier of the reserved room.
        booking_date: Day of the reservation.
        start_time: Time when the reservation starts.
        end_time: Time when the reservation ends.
    """

    room_id: str
    booking_date: date
    start_time: time
    end_time: time


@dataclass(frozen=True)
class ConflictResult:
    """Result of the conflict check for a reservation request.

    Attributes:
        has_conflict: Whether the requested reservation overlaps another one.
        conflicting_reservations: Reservations that conflict with the request.
    """

    has_conflict: bool
    conflicting_reservations: tuple[Reservation, ...]


class RoomBookingService:
    """Checks room reservation conflicts using in-memory data."""

    @staticmethod
    def check_conflicts(
        requested_reservation: Reservation,
        existing_reservations: list[Reservation],
    ) -> ConflictResult:
        """Check whether a requested reservation conflicts with existing ones.

        Args:
            requested_reservation: Reservation that should be evaluated.
            existing_reservations: Reservations already registered.

        Returns:
            ConflictResult with the conflict flag and overlapping reservations.

        Raises:
            InvalidReservationError: If any reservation has invalid fields.
        """

        RoomBookingService._validate_reservation(requested_reservation)

        conflicts = tuple(
            existing_reservation
            for existing_reservation in existing_reservations
            if RoomBookingService._has_conflict(
                requested_reservation,
                existing_reservation,
            )
        )

        return ConflictResult(
            has_conflict=bool(conflicts),
            conflicting_reservations=conflicts,
        )

    @staticmethod
    def can_reserve(
        requested_reservation: Reservation,
        existing_reservations: list[Reservation],
    ) -> bool:
        """Return True when the requested reservation has no conflict."""

        return not RoomBookingService.check_conflicts(
            requested_reservation,
            existing_reservations,
        ).has_conflict

    @staticmethod
    def _has_conflict(
        requested_reservation: Reservation,
        existing_reservation: Reservation,
    ) -> bool:
        RoomBookingService._validate_reservation(existing_reservation)

        if requested_reservation.room_id != existing_reservation.room_id:
            return False

        if requested_reservation.booking_date != existing_reservation.booking_date:
            return False

        return (
            requested_reservation.start_time < existing_reservation.end_time
            and requested_reservation.end_time > existing_reservation.start_time
        )

    @staticmethod
    def _validate_reservation(reservation: Reservation) -> None:
        if not reservation.room_id.strip():
            raise InvalidReservationError("room_id must not be empty.")

        if reservation.end_time <= reservation.start_time:
            raise InvalidReservationError("end_time must be after start_time.")
