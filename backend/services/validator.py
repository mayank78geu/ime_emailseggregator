"""
Validation Engine — checks extracted fields and appends _warnings list.
"""

from dateutil.parser import parse as date_parse


def validate(record: dict) -> dict:
    """
    Validate an extracted record dict and add a '_warnings' key.
    Modifies the dict in-place and returns it.
    """
    warnings = []
    category = record.get("category", "")

    if category == "TONNAGE":
        # Vessel name
        if not record.get("vessel_name"):
            warnings.append("vessel_name is missing")

        # DWT validation
        dwt = record.get("vessel_size_dwt")
        if dwt is None:
            warnings.append("vessel_size_dwt is missing")
        else:
            try:
                dwt_int = int(str(dwt).replace(",", "").replace(".", "").strip())
                if not (1000 <= dwt_int <= 500000):
                    warnings.append(f"vessel_size_dwt '{dwt}' is out of valid range (1000-500000)")
            except ValueError:
                warnings.append(f"vessel_size_dwt '{dwt}' is not a valid number")

        # Port name
        if not record.get("open_port"):
            warnings.append("open_port is missing")
        elif not _valid_port(record["open_port"]):
            warnings.append(f"open_port '{record['open_port']}' looks invalid")

        # Date
        if not record.get("open_date"):
            warnings.append("open_date is missing")
        else:
            if not _valid_date(record["open_date"]):
                warnings.append(f"open_date '{record['open_date']}' could not be parsed as a date")

    elif category == "CARGO_VC":
        if not record.get("cargo_name"):
            warnings.append("cargo_name is missing")
        if not record.get("loading_port"):
            warnings.append("loading_port is missing")
        elif not _valid_port(record["loading_port"]):
            warnings.append(f"loading_port '{record['loading_port']}' looks invalid")
        if not record.get("discharge_port"):
            warnings.append("discharge_port is missing")
        elif not _valid_port(record["discharge_port"]):
            warnings.append(f"discharge_port '{record['discharge_port']}' looks invalid")
        if not record.get("laycan_raw"):
            warnings.append("laycan is missing")

    elif category == "CARGO_TC":
        if not record.get("delivery_port"):
            warnings.append("delivery_port is missing")
        if not record.get("redelivery_port"):
            warnings.append("redelivery_port is missing")
        if not record.get("duration"):
            warnings.append("duration is missing")
        if not record.get("laycan_raw"):
            warnings.append("laycan is missing")

    record["_warnings"] = warnings
    return record


def _valid_port(port: str) -> bool:
    """A port name should be non-empty and mostly alphabetical."""
    if not port:
        return False
    cleaned = port.replace(" ", "").replace("-", "").replace(",", "").replace("+", "").replace("/", "")
    return cleaned.isalpha() and len(port.strip()) >= 2


def _valid_date(date_str: str) -> bool:
    """Try to parse a date string with dateutil."""
    try:
        date_parse(date_str, fuzzy=True)
        return True
    except Exception:
        return False
