"""
Router — POST /upload
Accepts .txt, .pdf, .docx files, extracts text, runs the same pipeline as /extract-email.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.parser import parse_file
from services.splitter import split_email_into_blocks
from services.classifier import classify
from services.extractor import extract, merge_records
from services.validator import validate
import models

router = APIRouter(tags=["Upload"])

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}


@router.post("/upload", summary="Upload a .txt/.pdf/.docx file and extract shipping data")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type .{ext}. Allowed: txt, pdf, docx")

    content = await file.read()

    try:
        raw_text = parse_file(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {str(e)}")

    # Save raw email
    email_record = models.Email(
        filename=file.filename,
        category=None,
        raw_content=raw_text,
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)

    # Split → Classify → Extract → Validate
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
        _save_to_db(db, email_record.id, category, validated)

    if len(categories_seen) == 1:
        email_record.category = categories_seen.pop()
    elif categories_seen:
        email_record.category = "MIXED"
    db.commit()

    return {"filename": file.filename, "records_found": len(results), "data": results}


def _save_to_db(db: Session, email_id: int, category: str, data: dict):
    try:
        if category == "TONNAGE":
            db.add(models.Tonnage(
                email_id=email_id,
                vessel_name=data.get("vessel_name"),
                account_name=data.get("account_name"),
                open_port=data.get("open_port"),
                open_date=data.get("open_date"),
                vessel_type=data.get("vessel_type"),
                vessel_size_dwt=data.get("vessel_size_dwt"),
                flag=data.get("flag"),
                built_year=data.get("built_year"),
            ))
        elif category == "CARGO_VC":
            db.add(models.CargoVC(
                email_id=email_id,
                account_name=data.get("account_name"),
                cargo_name=data.get("cargo_name"),
                loading_port=data.get("loading_port"),
                discharge_port=data.get("discharge_port"),
                laycan_raw=data.get("laycan_raw"),
                cargo_type=data.get("cargo_type"),
                quantity=data.get("quantity"),
                commission=data.get("commission"),
            ))
        elif category == "CARGO_TC":
            db.add(models.CargoTC(
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
            ))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Save error: {e}")
