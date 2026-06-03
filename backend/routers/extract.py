"""
Router — POST /extract-email (PRIMARY endpoint)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services.splitter import split_email_into_blocks
from services.classifier import classify
from services.extractor import extract, merge_records
from services.validator import validate
import models

router = APIRouter(tags=["Extract"])


class EmailInput(BaseModel):
    email_text: str


@router.post("/extract-email", summary="Extract structured data from shipping email text")
def extract_email(input: EmailInput, db: Session = Depends(get_db)):
    """
    Accepts raw shipping email text.
    Returns an array of structured JSON records — one per vessel or cargo found.
    Always returns an array, even for a single record.
    """
    raw_text = input.email_text

    # Step 1 — Save the raw email
    email_record = models.Email(
        filename=None,
        category=None,
        raw_content=raw_text,
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)

    # Step 2 — Split → Classify → Extract → Validate
    blocks = split_email_into_blocks(raw_text)
    
    extracted_records = []
    for block in blocks:
        category = classify(block)
        extracted = extract(block, category)
        extracted_records.append(extracted)

    # Perform the post-processing merge stage
    merged_records = merge_records(extracted_records)

    results = []
    categories_seen = set()

    for record in merged_records:
        category = record.get("category")
        categories_seen.add(category)
        validated = validate(record)
        results.append(validated)

        # Step 3 — Persist to correct table
        _save_to_db(db, email_record.id, category, validated)

    # Update email record category summary
    if len(categories_seen) == 1:
        email_record.category = categories_seen.pop()
    elif categories_seen:
        email_record.category = "MIXED"
    db.commit()

    return results


def _save_to_db(db: Session, email_id: int, category: str, data: dict):
    """Save extracted record to the correct table."""
    try:
        if category == "TONNAGE":
            row = models.Tonnage(
                email_id=email_id,
                vessel_name=data.get("vessel_name"),
                account_name=data.get("account_name"),
                open_port=data.get("open_port"),
                open_date=data.get("open_date"),
                vessel_type=data.get("vessel_type"),
                vessel_size_dwt=data.get("vessel_size_dwt"),
                flag=data.get("flag"),
                built_year=data.get("built_year"),
            )
            db.add(row)

        elif category == "CARGO_VC":
            row = models.CargoVC(
                email_id=email_id,
                account_name=data.get("account_name"),
                cargo_name=data.get("cargo_name"),
                loading_port=data.get("loading_port"),
                discharge_port=data.get("discharge_port"),
                laycan_raw=data.get("laycan_raw"),
                cargo_type=data.get("cargo_type"),
                quantity=data.get("quantity"),
                commission=data.get("commission"),
            )
            db.add(row)

        elif category == "CARGO_TC":
            row = models.CargoTC(
                email_id=email_id,
                account_name=data.get("account_name"),
                cargo_name=data.get("cargo_name"),
                delivery_port=data.get("delivery_port"),
                redelivery_port=data.get("redelivery_port"),
                duration=data.get("duration"),
                laycan_raw=data.get("laycan_raw"),
                cargo_type=data.get("cargo_type"),
                vessel_size=data.get("vessel_size"),
                commission=data.get("commission"),
            )
            db.add(row)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Failed to save {category} record: {e}")
