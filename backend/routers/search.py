"""
Router — Search & Records endpoints
"""

from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(tags=["Search"])


@router.get("/records/all", summary="Get all processed emails (paginated)")
def get_all_records(
    skip: int = 0,
    limit: int = 50,
):
    return {"total": 0, "skip": skip, "limit": limit, "data": []}


@router.get("/search/tonnage", summary="Search tonnage records")
def search_tonnage(
    open_port: Optional[str] = Query(None),
    min_dwt: Optional[int] = Query(None),
    max_dwt: Optional[int] = Query(None),
    flag: Optional[str] = Query(None),
    built_year: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    return {"total": 0, "data": []}


@router.get("/search/cargo_vc", summary="Search voyage charter cargo records")
def search_cargo_vc(
    loading_port: Optional[str] = Query(None),
    discharge_port: Optional[str] = Query(None),
    laycan_month: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    return {"total": 0, "data": []}


@router.get("/search/cargo_tc", summary="Search time charter cargo records")
def search_cargo_tc(
    delivery_port: Optional[str] = Query(None),
    redelivery_port: Optional[str] = Query(None),
    vessel_size: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    return {"total": 0, "data": []}
