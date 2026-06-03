"""
Router — POST /extract-email (PRIMARY endpoint)
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.splitter import split_email_into_blocks
from services.classifier import classify
from services.extractor import extract, merge_records
from services.validator import validate

router = APIRouter(tags=["Extract"])


class EmailInput(BaseModel):
    email_text: str


@router.post("/extract-email", summary="Extract structured data from shipping email text")
def extract_email(input: EmailInput):
    """
    Accepts raw shipping email text.
    Returns an array of structured JSON records — one per vessel or cargo found.
    Always returns an array, even for a single record.
    """
    raw_text = input.email_text

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

    return results
