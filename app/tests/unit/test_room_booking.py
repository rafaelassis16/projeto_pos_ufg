from datetime import date, time

import pytest

from app.services.room_booking import (
    InvalidReservationError,
    Reservation,
    RoomBookingService,
)


BOOKING_DATE = date(2026, 9, 26)


def make_reservation(
    room_id: str = "SALA-01",
    start_time: time = time(10, 0),
    end_time: time = time(11, 0),
    booking_date: date = BOOKING_DATE,
) -> Reservation:
    return Reservation(
        room_id=room_id,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
    )


def test_returns_conflict_for_overlapping_reservation_in_same_room_and_day():
    existing_reservations = [make_reservation()]
    requested_reservation = make_reservation(
        start_time=time(10, 30),
        end_time=time(11, 30),
    )

    result = RoomBookingService.check_conflicts(
        requested_reservation,
        existing_reservations,
    )

    assert result.has_conflict is True
    assert result.conflicting_reservations == tuple(existing_reservations)


def test_allows_reservation_starting_when_previous_one_ends():
    existing_reservations = [make_reservation()]
    requested_reservation = make_reservation(
        start_time=time(11, 0),
        end_time=time(12, 0),
    )

    assert RoomBookingService.can_reserve(
        requested_reservation,
        existing_reservations,
    )


def test_ignores_overlap_when_room_is_different():
    existing_reservations = [make_reservation(room_id="SALA-01")]
    requested_reservation = make_reservation(
        room_id="SALA-02",
        start_time=time(10, 30),
        end_time=time(11, 30),
    )

    assert RoomBookingService.can_reserve(
        requested_reservation,
        existing_reservations,
    )


def test_ignores_overlap_when_date_is_different():
    existing_reservations = [make_reservation()]
    requested_reservation = make_reservation(
        booking_date=date(2026, 9, 27),
        start_time=time(10, 30),
        end_time=time(11, 30),
    )

    assert RoomBookingService.can_reserve(
        requested_reservation,
        existing_reservations,
    )


def test_rejects_reservation_when_end_time_is_not_after_start_time():
    requested_reservation = make_reservation(
        start_time=time(11, 0),
        end_time=time(11, 0),
    )

    with pytest.raises(InvalidReservationError, match="end_time"):
        RoomBookingService.check_conflicts(requested_reservation, [])


def test_rejects_reservation_with_empty_room_id():
    requested_reservation = make_reservation(room_id=" ")

    with pytest.raises(InvalidReservationError, match="room_id"):
        RoomBookingService.check_conflicts(requested_reservation, [])
