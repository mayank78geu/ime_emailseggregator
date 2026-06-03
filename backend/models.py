from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)         # TONNAGE / CARGO_VC / CARGO_TC / MIXED
    upload_date = Column(DateTime, server_default=func.now())
    raw_content = Column(Text, nullable=False)


class Tonnage(Base):
    __tablename__ = "tonnage"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    vessel_name = Column(String(255), nullable=True)
    account_name = Column(String(255), nullable=True)
    open_port = Column(String(255), nullable=True)
    open_date = Column(String(100), nullable=True)
    vessel_type = Column(String(100), nullable=True)
    vessel_size_dwt = Column(String(50), nullable=True)
    flag = Column(String(100), nullable=True)
    built_year = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class CargoVC(Base):
    __tablename__ = "cargo_vc"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    account_name = Column(String(255), nullable=True)
    cargo_name = Column(String(255), nullable=True)
    loading_port = Column(String(255), nullable=True)
    discharge_port = Column(String(255), nullable=True)
    laycan_start = Column(String(100), nullable=True)
    laycan_end = Column(String(100), nullable=True)
    laycan_raw = Column(String(255), nullable=True)
    cargo_type = Column(String(100), nullable=True)
    quantity = Column(String(100), nullable=True)
    commission = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class CargoTC(Base):
    __tablename__ = "cargo_tc"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    account_name = Column(String(255), nullable=True)
    cargo_name = Column(String(255), nullable=True)
    delivery_port = Column(String(255), nullable=True)
    redelivery_port = Column(String(255), nullable=True)
    duration = Column(String(100), nullable=True)
    laycan_start = Column(String(100), nullable=True)
    laycan_end = Column(String(100), nullable=True)
    laycan_raw = Column(String(255), nullable=True)
    cargo_type = Column(String(100), nullable=True)
    vessel_size = Column(String(100), nullable=True)
    commission = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
