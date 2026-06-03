"""
Router — Search & Records endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List

from database import get_db
import models
import schemas

router = APIRouter(tags=["Search"])


@router.get("/records/all", summary="Get all processed emails (paginated)")
def get_all_records(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    emails = db.query(models.Email).offset(skip).limit(limit).all()
    total = db.query(models.Email).count()
    return {"total": total, "skip": skip, "limit": limit, "data": emails}


@router.get("/search/tonnage", summary="Search tonnage records")
def search_tonnage(
    open_port: Optional[str] = Query(None),
    min_dwt: Optional[int] = Query(None),
    max_dwt: Optional[int] = Query(None),
    flag: Optional[str] = Query(None),
    built_year: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(models.Tonnage)
    if open_port:
        q = q.filter(models.Tonnage.open_port.ilike(f"%{open_port}%"))
    if flag:
        q = q.filter(models.Tonnage.flag.ilike(f"%{flag}%"))
    if built_year:
        q = q.filter(models.Tonnage.built_year == built_year)
    if min_dwt is not None:
        q = q.filter(models.Tonnage.vessel_size_dwt >= str(min_dwt))
    if max_dwt is not None:
        q = q.filter(models.Tonnage.vessel_size_dwt <= str(max_dwt))
    total = q.count()
    return {"total": total, "data": q.offset(skip).limit(limit).all()}


@router.get("/search/cargo_vc", summary="Search voyage charter cargo records")
def search_cargo_vc(
    loading_port: Optional[str] = Query(None),
    discharge_port: Optional[str] = Query(None),
    laycan_month: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(models.CargoVC)
    if loading_port:
        q = q.filter(models.CargoVC.loading_port.ilike(f"%{loading_port}%"))
    if discharge_port:
        q = q.filter(models.CargoVC.discharge_port.ilike(f"%{discharge_port}%"))
    if laycan_month:
        q = q.filter(models.CargoVC.laycan_raw.ilike(f"%{laycan_month}%"))
    total = q.count()
    return {"total": total, "data": q.offset(skip).limit(limit).all()}


@router.get("/search/cargo_tc", summary="Search time charter cargo records")
def search_cargo_tc(
    delivery_port: Optional[str] = Query(None),
    redelivery_port: Optional[str] = Query(None),
    vessel_size: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(models.CargoTC)
    if delivery_port:
        q = q.filter(models.CargoTC.delivery_port.ilike(f"%{delivery_port}%"))
    if redelivery_port:
        q = q.filter(models.CargoTC.redelivery_port.ilike(f"%{redelivery_port}%"))
    if vessel_size:
        q = q.filter(
            or_(
                models.CargoTC.vessel_size.ilike(f"%{vessel_size}%"),
            )
        )
    total = q.count()
    return {"total": total, "data": q.offset(skip).limit(limit).all()}
