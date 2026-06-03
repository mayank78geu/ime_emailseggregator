from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ──────────────────── INPUT ────────────────────
class EmailInput(BaseModel):
    email_text: str


# ──────────────────── OUTPUT RECORDS ────────────────────
class TonnageRecord(BaseModel):
    category: str = "TONNAGE"
    vessel_name: Optional[str] = None
    account_name: Optional[str] = None
    open_port: Optional[str] = None
    open_date: Optional[str] = None
    vessel_type: Optional[str] = None
    vessel_size_dwt: Optional[str] = None
    flag: Optional[str] = None
    built_year: Optional[str] = None
    _warnings: Optional[List[str]] = []

    class Config:
        populate_by_name = True


class CargoVCRecord(BaseModel):
    category: str = "CARGO_VC"
    account_name: Optional[str] = None
    cargo_name: Optional[str] = None
    loading_port: Optional[str] = None
    discharge_port: Optional[str] = None
    laycan_raw: Optional[str] = None
    cargo_type: Optional[str] = None
    quantity: Optional[str] = None
    commission: Optional[str] = None
    _warnings: Optional[List[str]] = []

    class Config:
        populate_by_name = True


class CargoTCRecord(BaseModel):
    category: str = "CARGO_TC"
    account_name: Optional[str] = None
    cargo_name: Optional[str] = None
    delivery_port: Optional[str] = None
    redelivery_port: Optional[str] = None
    duration: Optional[str] = None
    laycan_raw: Optional[str] = None
    cargo_type: Optional[str] = None
    vessel_size: Optional[str] = None
    commission: Optional[str] = None
    _warnings: Optional[List[str]] = []

    class Config:
        populate_by_name = True


# ──────────────────── DB RESPONSE SCHEMAS ────────────────────
class EmailResponse(BaseModel):
    id: int
    filename: Optional[str]
    category: Optional[str]
    upload_date: Optional[datetime]

    class Config:
        from_attributes = True


class TonnageResponse(BaseModel):
    id: int
    email_id: Optional[int]
    vessel_name: Optional[str]
    open_port: Optional[str]
    open_date: Optional[str]
    vessel_size_dwt: Optional[str]
    flag: Optional[str]
    built_year: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class CargoVCResponse(BaseModel):
    id: int
    email_id: Optional[int]
    cargo_name: Optional[str]
    loading_port: Optional[str]
    discharge_port: Optional[str]
    laycan_raw: Optional[str]
    quantity: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class CargoTCResponse(BaseModel):
    id: int
    email_id: Optional[int]
    delivery_port: Optional[str]
    redelivery_port: Optional[str]
    duration: Optional[str]
    laycan_raw: Optional[str]
    vessel_size: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
