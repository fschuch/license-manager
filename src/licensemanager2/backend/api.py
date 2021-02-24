"""
Endpoints for the backend
"""
from fastapi import APIRouter, Depends, Header

from licensemanager2.backend.booking import router_booking
from licensemanager2.backend.license import router_license
from licensemanager2.backend.schema import booking_table, license_table
from licensemanager2.backend.storage import database
from licensemanager2.common_api import OK, debug


api_v1 = APIRouter()
api_v1.include_router(router_license, prefix="/license", tags=["License"])
api_v1.include_router(router_booking, prefix="/booking", tags=["Booking"])


@database.transaction()
@api_v1.put("/reset", response_model=OK)
async def reset_everything(debug=Depends(debug), x_reconcile_reset=Header(...)):
    """
    Reset all database data (only permitted in DEBUG mode)

    Set the header `X-Reconcile-Reset:` to anything you want.
    """
    await database.execute(license_table.delete())
    await database.execute(booking_table.delete())
    return OK()
