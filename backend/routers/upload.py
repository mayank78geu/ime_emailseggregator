"""
Router — POST /upload
Accepts .txt, .pdf, .docx files, extracts text, runs the same pipeline as /extract-email.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.parser import parse_file
from services.splitter import split_email_into_blocks
from services.classifier import classify
from services.extractor import extract, merge_records
from services.validator import validate

router = APIRouter(tags=["Upload"])

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}


@router.post("/upload", summary="Upload a .txt/.pdf/.docx file and extract shipping data")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type .{ext}. Allowed: txt, pdf, docx")

    content = await file.read()

    try:
        raw_text = parse_file(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {str(e)}")

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
    for record in merged_records:
        validated = validate(record)
        results.append(validated)

    return {"filename": file.filename, "records_found": len(results), "data": results, "raw_content": raw_text}
