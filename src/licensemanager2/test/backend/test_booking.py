"""
Tests of the /booking API endpoints
"""
from httpx import AsyncClient
from pytest import fixture, mark

from licensemanager2.backend import booking, schema
from licensemanager2.backend.storage import database
from licensemanager2.test.backend.conftest import insert_objects


@fixture
def some_booking_rows():
    """
    Some BookingRows
    """
    inserts = [
        booking.BookingRow(
            job_id="hellodollybeans",
            product_feature="hello.world",
            booked=19,
        ),
        booking.BookingRow(
            job_id="hellodollybeans",
            product_feature="hello.dolly",
            booked=11,
        ),
        booking.BookingRow(
            job_id="coolbeans",
            product_feature="cool.beans",
            booked=11,
        ),
    ]
    return inserts


@mark.asyncio
@database.transaction(force_rollback=True)
async def test_get_bookings_job(
    backend_client: AsyncClient, some_licenses, some_booking_rows
):
    """
    Do I fetch a booking?
    """
    await insert_objects(some_licenses, schema.license_table)
    await insert_objects(some_booking_rows, schema.booking_table)
    resp = await backend_client.get("/api/v1/booking/job/coolbeans")
    assert resp.status_code == 200
    assert resp.json() == [
        dict(job_id="coolbeans", product_feature="cool.beans", booked=11),
    ]


@mark.asyncio
@database.transaction(force_rollback=True)
async def test_bookings_all(
    backend_client: AsyncClient, some_licenses, some_booking_rows
):
    """
    Do I fetch all the bookings in the db?
    """
    await insert_objects(some_licenses, schema.license_table)
    await insert_objects(some_booking_rows, schema.booking_table)
    resp = await backend_client.get("/api/v1/booking/all")
    assert resp.status_code == 200
    assert resp.json() == [
        dict(
            job_id="coolbeans",
            product_feature="cool.beans",
            booked=11,
        ),
        dict(
            job_id="hellodollybeans",
            product_feature="hello.dolly",
            booked=11,
        ),
        dict(
            job_id="hellodollybeans",
            product_feature="hello.world",
            booked=19,
        ),
    ]
