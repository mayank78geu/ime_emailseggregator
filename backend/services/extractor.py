"""
Extraction Engine — pulls structured fields from each classified block.
Uses regex patterns tuned against real-world shipping email formats.
"""

import re


# ──────────────────── HELPERS ────────────────────

def _find(pattern: str, text: str, group: int = 1, flags=re.IGNORECASE) -> str | None:
    """Run regex, return first group or None."""
    m = re.search(pattern, text, flags)
    if m:
        val = m.group(group)
        if val is None:
            # If the default group is None, try the first non-None captured group
            for g in m.groups():
                if g is not None:
                    val = g
                    break
        if val is not None:
            return val.strip().strip('.,;:').strip()
    return None


def _clean_port(raw: str | None) -> str | None:
    """Remove common trailing noise from port names and reject vessel terminology."""
    if not raw:
        return None
    # Remove parenthetical comments/details
    raw = re.sub(r'\(.*?\)', '', raw)
    # Clean up East Kalimantan / regional prefixes
    raw = re.sub(r'\b(?:E\s+)?KALI\s+OF\s+', '', raw, flags=re.IGNORECASE)
    # Standardize separators like "OR", "AND", "+" to "/"
    raw = re.sub(r'\s+(?:OR|AND|\+)\s+', '/', raw, flags=re.IGNORECASE)
    # Strip trailing words like VIA, WITH, FOR, ON, FROM, IN, TO
    raw = re.sub(
        r'\s+(VIA|WITH|FOR|ON|FROM|IN|TO|AFTER|BEFORE|DURING|EX|ETA|ETD)\b.*',
        '', raw, flags=re.IGNORECASE
    ).strip()
    # Standardize comma spacing
    raw = re.sub(r'\s*,\s*', ', ', raw)
    # Remove trailing punctuation
    raw = raw.strip('.,;:/-').strip()
    # Normalize double spaces
    raw = re.sub(r'\s+', ' ', raw)
    
    # Reject vessel descriptions/terminology mistaken for ports
    raw_u = raw.upper()
    blacklist = {
        'HATC', 'HATCH', 'BOX', 'HATC BOX', 'HATCH BOX', 'BOX SHAPED', 'BOX-SHAPED',
        'GEARED', 'GEARLESS', 'FITTED', 'SCRUBBER', 'SCRUBBER FITTED',
        'SID', 'OH', 'HO', 'HA', 'HO/HA', 'HH', 'H/H', 'ASF', 'AGW', 'WOG',
        'BULK', 'CARRIER', 'BULK CARRIER', 'TWEEN', 'TWEEN DECKER', 'TWEENDECKER',
        'OPEN', 'CLOSE', 'OWS'
    }
    if raw_u in blacklist:
        return None
    for term in ['HATCH', 'HATC BOX', 'BOX SHAPED', 'GEARLESS', 'SCRUBBER FITTED', 'BULK CARRIER']:
        if term in raw_u:
            return None
            
    return raw if raw else None


def _clean_name(raw: str | None) -> str | None:
    """Clean vessel name — remove extra DWT/OPEN/O/A fragments."""
    if not raw:
        return None
    # Stop at common noise keywords
    raw = re.split(r'\b(DWT|OPEN|O/A|FLAG|BUILT|CLASS|IMO|CALL|MMSI)\b', raw, flags=re.IGNORECASE)[0]
    return raw.strip().strip('.,;:/-').strip() or None


# ──────────────────── TONNAGE ────────────────────

def extract_tonnage(text: str) -> dict:
    text_u = text.upper()

    # Try to match the specific headline pattern line-by-line first
    h_vessel = None
    h_port = None
    h_date = None
    for line in text.split('\n'):
        line_u = line.strip().upper()
        # Pattern 1: <VESSEL_NAME> (...) - OPEN <PORT>, <COUNTRY> <DATE>
        m = re.search(
            r'^\s*([A-Z0-9\s\-]+?)\s*\([^\)]*?\)\s*[\-–—]\s*OPEN\s+([A-Z0-9\s,\-]+?)\s+(\d{1,2}[\dA-Z\s\-/]+?(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z0-9\s]*?)\s*$',
            line_u
        )
        if m:
            h_vessel = m.group(1).strip()
            h_port = m.group(2).strip()
            h_date = m.group(3).strip()
            break
        
        # Pattern 2: MV <VESSEL_NAME> (<SIZE>) - OPEN <DATE> <PORT>
        m2 = re.search(
            r'^\s*(?:MV|M/V)?\.?\s*([A-Z0-9\s\-]+?)\s*\([^\)]*?\)\s*[\-–—]\s*OPEN\s+(\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*)\s+([A-Z0-9\s,\-]+?)\s*$',
            line_u
        )
        if m2:
            h_vessel = m2.group(1).strip()
            h_date = m2.group(2).strip()
            h_port = m2.group(3).strip()
            break

    # Vessel name — "MV SHENG AN HAI" / "M/V SHENG AN HAI" / "MV. COS ORCHID"
    vessel_name = h_vessel
    if not vessel_name:
        vessel_name = _find(
            r'\bM[/\s\.]?V\.?\s*[:\-]?\s*([A-Z][A-Z0-9\s\-]+?)(?:\s*[\n/,]|\s+DWT|\s+\d{4,6}|\s+OPEN|\s+O/A|\s+–)',
            text_u
        )
    if not vessel_name:
        # Try bare vessel name after "VESSEL:" label
        vessel_name = _find(r'VESSEL\s*[:\-]\s*([A-Z][A-Z0-9\s\-]+?)[\n,]', text_u)
    vessel_name = _clean_name(vessel_name)

    # DWT — "56564 DWT" / "DWT 56564" / "56,564 MTDWT" / "SUMMER DWT:56704"
    dwt = _find(
        r'(?:SUMMER\s+)?DWT[\s:]*([0-9,\.]{4,10})\s*(?:MT|MTS)?|([0-9,\.]{4,10})\s*(?:MT\s*)?DWT',
        text_u
    )
    if not dwt:
        # Try alternate format like "56564.4MT ON"
        dwt = _find(r'([\d,\.]{5,10})\s*(?:MT|MTS)\s+ON\s+\d', text_u)
    
    # Try alternate format: slash-separated DWT like "/51K/" or "/51,000/" or "/51000/"
    if not dwt:
        slash_match = re.search(r'\bM[/\s\.]?V\.?\s*[^/\n]+?/([0-9,\.]{2,8}\s*K?)\b', text_u)
        if slash_match:
            dwt = slash_match.group(1).strip()

    if dwt:
        dwt_upper = dwt.upper()
        if 'K' in dwt_upper:
            # Convert K notation to thousands (e.g. 51K -> 51000)
            k_match = re.search(r'(\d+(?:\.\d+)?)\s*K', dwt_upper)
            if k_match:
                val = float(k_match.group(1))
                dwt = str(int(val * 1000))
        else:
            if '.' in dwt:
                parts = dwt.split('.')
                try:
                    prefix_val = int(parts[0].replace(',', '').strip())
                    if prefix_val < 1000:
                        # e.g., 51.241 -> 51241
                        dwt = "".join(parts)
                    else:
                        # e.g., 56564.4 -> 56564
                        dwt = parts[0]
                except ValueError:
                    dwt = parts[0]
            dwt = dwt.replace(',', '').strip()[:6]

    # Try alternate format: "- <PORT> , <DATE>" (often found in summary lists without the keyword OPEN)
    # E.g. "MV TRUE FRIEND/51K/ 09 - BEJAIA , 1ST JUNE ONW - EX OUR CP"
    slash_port = None
    slash_date = None
    port_date_match = re.search(
        r'\-\s*([A-Z][A-Z\s\-]{2,20}?)\s*,\s*([\dA-Z\s\-]+?(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z0-9\s]*?)(?:\s+\-|\s{2,}|$)',
        text_u
    )
    if port_date_match:
        slash_port = port_date_match.group(1).strip()
        slash_date = port_date_match.group(2).strip()

    # Open port — "OPEN XIAMEN, CHINA" / "OPEN: HAMBURG"
    open_port = _clean_port(h_port)
    if not open_port:
        open_port = _find(
            r'\bOPEN\b[\s:,\-]+([A-Z][A-Z\s,\-]+?)(?:\s*[\n/,]|\s+O/A|\s+\d|\s+–|\s+ETA|\s+ETD)',
            text_u
        )
        if not open_port:
            open_port = _find(r'\bOPEN\b[\s:,\-]+([A-Z][A-Z\s]+)', text_u)

        if not open_port:
            open_port = slash_port
        open_port = _clean_port(open_port)
        if not open_port:
            open_port = _clean_port(slash_port)

    # Open date — "O/A 2ND JUNE 2026" / "O/A 08-12 JUNE"
    open_date = h_date
    if not open_date:
        open_date = _find(
            r'O/A\s+([\dA-Z\s\-/THNDRDST]+?(?:JUNE|JULY|AUG|SEP|OCT|NOV|DEC|JAN|FEB|MAR|APR|MAY)\s*\d*)',
            text_u
        )
        if not open_date:
            open_date = _find(r'O/A\s+([\d\-/]+\s+[A-Z]+\s*\d*)', text_u)
        if not open_date:
            open_date = slash_date

    # Flag
    flag = _find(r'([A-Z][A-Z \t\-]{2,20})[ \t]+FLAG\b', text_u)
    if not flag:
        flag = _find(r'\bFLAG\s*[:\-]?\s*([A-Z][A-Z\s\-]+?)(?:\n|CLASS|BUILT|IMO|TYPE|\s{2,}|$)', text_u)
    if flag:
        flag = flag.strip()
        # Clean leading BLT or BUILT
        flag = re.sub(r'^(?:BLT|BUILT)\s*', '', flag, flags=re.IGNORECASE).strip()
        # Discard trailing keywords
        flag = re.split(r'\b(SDBC|SDSTBC|CLASS|BUILT|IMO|CALL|MMSI)\b', flag, flags=re.IGNORECASE)[0].strip()
        flag = flag.strip('.,;:/-').strip()
        if not flag or len(flag) < 2:
            flag = None

    # Built year
    built_year = _find(r'\bBUILT\s*[:\-]?\s*(\d{4})', text_u)
    if not built_year:
        built_year = _find(r'(\d{4})\s*BLT', text_u)
    if not built_year:
        built_year = _find(r'\b(?:DATE\s+OF\s+)?DELIVERY\s*[:\-]?\s*(?:[A-Z]+\s+)?(\d{4})', text_u)

    # Check for <FLAG>/<YY> format (e.g. "HONG KONG/11")
    hk_match = re.search(r'\b([A-Z][A-Z \t\-]{2,20})/(\d{2})\b', text_u)
    if hk_match:
        if not flag:
            flag = hk_match.group(1).strip()
            flag = re.split(r'\b(SDBC|SDSTBC|CLASS|BUILT|IMO)\b', flag, flags=re.IGNORECASE)[0].strip()
        if not built_year:
            yy = int(hk_match.group(2))
            built_year = str(2000 + yy if yy < 50 else 1900 + yy)

    return {
        "category": "TONNAGE",
        "vessel_name": vessel_name,
        "vessel_size_dwt": dwt,
        "open_port": open_port,
        "open_date": open_date,
        "flag": flag,
        "built_year": built_year,
        "account_name": None,
        "vessel_type": None,
    }


# ──────────────────── CARGO VC ────────────────────

def extract_cargo_vc(text: str) -> dict:
    text_u = text.upper()

    # Cargo name / quantity — "20,000 MT HRC" / "15,000 - 20,000 MTS MOLOCHOPT"
    # Match pattern: number(s) + MT/MTS + cargo type word(s) — stop before FIOS/LOAD/newline
    # Using [ \t] instead of \s to prevent matching across lines
    cargo_name = _find(
        r'^([\d,\s\-\.]+\s*(?:MT|MTS|TONS?)\s+(?:\d+PCT\s+)?(?:MOLOCHOPT|HRC|IRON[A-Z \t]*|UREA|COAL|CLINKER|SLAG|GRAIN|FERTILIZER|STEEL|CEMENT|SALT|LIMESTONE|[A-Z]{2,}[A-Z \t]*))',
        text_u,
        flags=re.IGNORECASE | re.MULTILINE
    )
    if not cargo_name:
        cargo_name = _find(
            r'([\d,\s\-\.]+\s*(?:MT|MTS|TONS?)\s+[A-Z][A-Z0-9 \t/\-]{2,25}?)(?:\n|FIOS|LOAD|POL|POD|LP|DP|CQD|LAYCAN|\s{3,})',
            text_u
        )
    if not cargo_name:
        cargo_name = _find(r'CARGO\s*[:\-]\s*([A-Z0-9,\s\-]+?)(?:\n|LOAD|POL|LP)', text_u)

    quantity = None
    if cargo_name:
        # Strip trailing newlines if any got caught
        cargo_name = cargo_name.split('\n')[0].strip()
        q = re.search(r'([\d,\-\s\.]+\s*(?:MT|MTS|TONS?))', cargo_name, re.IGNORECASE)
        quantity = q.group(1).strip() if q else None
        cargo_name = cargo_name.strip().strip('.,;:').strip()

    # Loading port — "LOAD PORT: KOH SI CHANG" / "POL: JEDDAH"
    loading_port = _find(
        r'(?:LOAD(?:ING)?\s*PORT|LP)\s*[:\-,]+\s*([A-Z][A-Z\s,\-]+?)(?:\n|DISCH|POD|LOAD\s*RATE|LAYCAN)',
        text_u
    )
    if not loading_port:
        loading_port = _find(r'POL\s*[:\-]?\s*([A-Z][A-Z\s\-,+]+?)(?:\n|POD|DISCH|LAYCAN)', text_u)
    loading_port = _clean_port(loading_port)

    # Discharge port — "DISCHARGE PORT: BILBAO" / "POD: DOHA"
    discharge_port = _find(
        r'(?:DISCH(?:ARGE)?\s*(?:PORT)?|DP)\s*[:\-,]+\s*([A-Z][A-Z\s,\-+]+?)(?:\n|LOAD\s*RATE|DISCH\s*RATE|LAYCAN|COM)',
        text_u
    )
    if not discharge_port:
        discharge_port = _find(r'POD\s*[:\-]?\s*([A-Z][A-Z\s\-,+]+?)(?:\n|LAYCAN|LOAD|COM)', text_u)
    discharge_port = _clean_port(discharge_port)

    # Fallback to route format: e.g. "Jeddah / Bilbao" - restrict to single line using [A-Z \t\-]
    if not loading_port or not discharge_port:
        route_pat = re.compile(
            r'^[ \t]*([A-Z][A-Z \t\-]{2,20})\s*(?:/|->|\bTO\b)\s*([A-Z][A-Z \t\-]{2,20})[ \t]*$',
            re.IGNORECASE | re.MULTILINE
        )
        for m in route_pat.finditer(text_u):
            p1, p2 = m.group(1).strip(), m.group(2).strip()
            blacklist = {'REGARDS', 'DEAR', 'GOOD', 'DAY', 'BROKER', 'EMAIL', 'PHONE', 'FAX', 'TEL', 'SKYPE', 'HTTP', 'WWW', 'CLIENT', 'CHARTERER', 'OWNER', 'MASTER'}
            if any(term in p1 or term in p2 for term in blacklist):
                continue
            r_lp = _clean_port(m.group(1))
            r_dp = _clean_port(m.group(2))
            if r_lp and r_dp:
                if not loading_port:
                    loading_port = r_lp
                if not discharge_port:
                    discharge_port = r_dp
                break

    # Laycan — "LAYCAN: 25 JUNE - 5 JULY" / "MID JULY 2026"
    laycan_raw = _find(
        r'LAYCAN\s*[:\-]?\s*([A-Z0-9\s\-/]+?)(?:\n|COM|TTL|RATE|3\.|$)',
        text_u
    )
    if not laycan_raw:
        laycan_raw = _find(r'LC\s+([A-Z0-9\s\-/]+?)(?:\n|COM|TTL|$)', text_u)

    # Fallback to general date range when no keyword exists
    if not laycan_raw:
        months_pat = r'(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*'
        date_range_match = re.search(
            r'\b(\d{1,2}\s*(?:' + months_pat + r')?\s*[\-–/]\s*\d{1,2}\s*' + months_pat + r'(?:\s*\d{4})?)\b',
            text_u
        )
        if date_range_match:
            laycan_raw = date_range_match.group(1).strip()
        else:
            date_range_match2 = re.search(
                r'\b(\d{1,2}\s*[\-–/]\s*\d{1,2}\s+' + months_pat + r'(?:\s*\d{4})?)\b',
                text_u
            )
            if date_range_match2:
                laycan_raw = date_range_match2.group(1).strip()

    # Commission
    commission = _find(r'(?:COM(?:M(?:ISSION)?)?|ADC|ADDCOM)\s*[:\-]?\s*([\d\.]+\s*%?\s*(?:TTL|PCT|PUS)?)', text_u)
    if not commission:
        comm_match = re.search(
            r'\b([\d\.,]+\s*%\s*(?:TTL|PCT|PUS|HERE)?)\b',
            text_u
        )
        if comm_match:
            commission = comm_match.group(1).strip()

    return {
        "category": "CARGO_VC",
        "cargo_name": cargo_name,
        "quantity": quantity,
        "loading_port": loading_port,
        "discharge_port": discharge_port,
        "laycan_raw": laycan_raw,
        "cargo_type": None,
        "account_name": None,
        "commission": commission,
    }


# ──────────────────── CARGO TC ────────────────────

def extract_cargo_tc(text: str) -> dict:
    text_u = text.upper()

    # Delivery port — "DELIVERY TM VANCOUVER" / "DELY TO MAKE SANGATTA" / "Delivery: ECI"
    delivery_port = _find(
        r'(?:DELIVERY|DELY)\s*[:\-]?\s*(?:TO\s+MAKE\s+|TM\s+)?([A-Z0-9\s,\-\(\)/\.]+?)(?:\n|LC|LAYCAN|SMX|UMX|PMAX|REDELIVERY|REDEL|$)',
        text_u
    )
    delivery_port = _clean_port(delivery_port)

    # Redelivery port — "REDELIVERY CHITTAGONG" / "REDEL: MED"
    redelivery_port = _find(
        r'(?:REDELIVERY|REDEL)\s*[:\-]?\s*([A-Z][A-Z\s,\-]+?)(?:\n|LC|LAYCAN|DURATION|3\.)',
        text_u
    )
    if not redelivery_port:
        # Fallback for "1 TCT WITH CLINKER TO BDESH"
        redelivery_port = _find(
            r'\b\d+\s*TCT\s+(?:WITH|W/)\s+[A-Z0-9\s/]+?\s+TO\s+([A-Z][A-Z\s\-]+)',
            text_u
        )
    redelivery_port = _clean_port(redelivery_port)

    # Duration — support common TC duration patterns: 1 TCT, trip, days/months/years
    duration = _find(
        r'DURATION\s*[:\-]?\s*([A-Z0-9\s\-]+?(?:DAYS?|MONTHS?|YEARS?|TCT|R/V|TRIP)\s*(?:WOG)?)',
        text_u
    )
    if not duration:
        # Match common duration formats (e.g. "1 TCT", "2 TCT", "1-3 YEARS")
        duration = _find(
            r'\b((?:ABT\s+)?\d+(?:\-\d+)?\s*(?:TCT|DAYS?|MONTHS?|YEARS?)\s*(?:WOG)?)\b',
            text_u
        )
    if not duration:
        # Match "TRIP" or "R/V" or "ROUND VOYAGE"
        duration = _find(
            r'\b(R/V|TRIP|ROUND\s+VOYAGE)\b',
            text_u
        )
    if not duration:
        duration = _find(
            r'\b(ABT\s+[\d\-]+\s*(?:DAYS?|MONTHS?|YEARS?)\s*(?:WOG)?)\b',
            text_u
        )

    # Laycan — "LC 10-17 JUNE" / "LAYCAN: 15-18 JULY"
    laycan_raw = _find(
        r'(?:LAYCAN|LC)\s*[:\-]?\s*([A-Z0-9\s\-/]+?)(?:\n|SMX|UMX|REDELIVERY|REDEL|DURATION|3\.)',
        text_u
    )
    if not laycan_raw:
        # Fallback to general date range (e.g. "29-2ND JUN" or "21-23 JULY") when no keyword exists
        fallback_match = re.search(
            r'\b(\d{1,2}\s*-\s*\d{1,2}(?:ST|ND|RD|TH)?\s*(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*)\b',
            text_u
        )
        if fallback_match:
            laycan_raw = fallback_match.group(1).strip()
            
    if laycan_raw:
        # Normalize crossed month boundary laycan like "29-2ND JUN" -> "29 MAY - 2 JUN"
        norm_match = re.search(
            r'\b(\d{1,2})\s*-\s*\d{1,2}(?:ST|ND|RD|TH)?\s*(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)',
            laycan_raw.upper()
        )
        if norm_match:
            d1 = int(norm_match.group(1))
            # Find the second number in the range (e.g. "2ND" -> 2)
            d2_match = re.search(r'-\s*(\d{1,2})', laycan_raw)
            if d2_match:
                d2 = int(d2_match.group(1))
                # The second capture group is the month
                m2 = norm_match.group(2)
                if d1 > d2:
                    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    try:
                        idx2 = months.index(m2[:3])
                        idx1 = (idx2 - 1) % 12
                        m1 = months[idx1]
                        laycan_raw = f"{d1} {m1} - {d2} {m2}"
                    except ValueError:
                        pass

    # Vessel size hint — "22k dwt" / "SMX-UMX" / "SUPRA/ULTRA"
    vessel_size = _find(r'(\d+[Kk]?\s*DWT\s*(?:UPTO|TO)?\s*(?:SMX|UMX|PMAX|HMAX|SUPRA|ULTRA|HANDY|PANAMAX|CAPESIZE)?)', text_u)
    if not vessel_size:
        keywords = r'(?:SMX|UMX|PMAX|HMAX|SUPRA|ULTRA|HANDY|PANAMAX|CAPESIZE)'
        vessel_size = _find(r'\b(' + keywords + r'(?:\s*[\-/]|\s+OR\s+)?\s*' + keywords + r'?)\b', text_u)

    # Commission — support common broker abbreviations and format to <number>%
    comm_match = re.search(
        r'\b(\d+(?:\.\d+)?)\s*(?:%|(?:PCT|ADDCOM|ADDOM|ADC|ADCOM|TTL|PUS)\b)',
        text_u
    )
    if not comm_match:
        comm_match = re.search(
            r'\b(?:ADDCOM|ADDOM|ADC|ADCOM|COMM?|TTL)\s*[:\-]?\s*(\d+(?:\.\d+)?)\b',
            text_u
        )
    commission = f"{comm_match.group(1)}%" if comm_match else None


    # Account / charterer
    account = _find(r'A[/\s]?C\s+([A-Z][A-Z\s]+?)(?:\n|DELIVERY|DELY|SMX)', text_u)

    # Cargo type hint
    cargo_name = _find(r'(?:WITH|W/)\s+([A-Z][A-Z\s/]+?)(?:\n|FROM|TO|DELY|REDELIVERY)', text_u)

    return {
        "category": "CARGO_TC",
        "account_name": account,
        "cargo_name": cargo_name,
        "delivery_port": delivery_port,
        "redelivery_port": redelivery_port,
        "duration": duration,
        "laycan_raw": laycan_raw,
        "cargo_type": None,
        "vessel_size": vessel_size,
        "commission": commission,
    }


# ──────────────────── MAIN ENTRY ────────────────────

def extract(text: str, category: str) -> dict:
    if category == "TONNAGE":
        return extract_tonnage(text)
    elif category == "CARGO_VC":
        return extract_cargo_vc(text)
    elif category == "CARGO_TC":
        return extract_cargo_tc(text)
    else:
        return {"category": category, "raw_text": text[:200]}


def merge_tonnage_records(r1: dict, r2: dict) -> dict:
    """Merge two tonnage records according to preference rules."""
    # Count particulars fields filled for each
    r1_part_score = sum(1 for f in ["flag", "built_year", "vessel_type"] if r1.get(f))
    r2_part_score = sum(1 for f in ["flag", "built_year", "vessel_type"] if r2.get(f))
    
    merged = {}
    for key in r1.keys():
        val1 = r1.get(key)
        val2 = r2.get(key)
        
        if key in ["open_port", "open_date"]:
            # Prefer the summary record (the one with lower particulars score)
            if r2_part_score < r1_part_score and val2:
                merged[key] = val2
            else:
                merged[key] = val1 or val2
        elif key in ["flag", "built_year"]:
            # Prefer the particulars record (the one with higher particulars score)
            if r2_part_score > r1_part_score and val2:
                merged[key] = val2
            else:
                merged[key] = val1 or val2
        else:
            # For other fields (like DWT), prefer the particulars record's value
            if r2_part_score > r1_part_score and val2:
                merged[key] = val2
            else:
                merged[key] = val1 or val2
                
    return merged


def _is_empty_record(r: dict) -> bool:
    """Check if a record is completely empty/placeholder with no category-specific fields."""
    cat = r.get("category")
    if cat == "TONNAGE":
        vessel_fields = ["vessel_name", "vessel_size_dwt", "open_port", "open_date", "flag", "built_year", "vessel_type"]
        return all(r.get(f) is None or str(r.get(f)).strip() == "" for f in vessel_fields)
    elif cat == "CARGO_VC":
        vc_fields = ["cargo_name", "quantity", "loading_port", "discharge_port", "laycan_raw", "commission"]
        return all(r.get(f) is None or str(r.get(f)).strip() == "" for f in vc_fields)
    elif cat == "CARGO_TC":
        tc_fields = ["cargo_name", "delivery_port", "redelivery_port", "duration", "laycan_raw", "vessel_size", "commission"]
        return all(r.get(f) is None or str(r.get(f)).strip() == "" for f in tc_fields)
    return True


def merge_records(records: list) -> list:
    """
    Merge tonnage records with matching vessel names.
    Keep all other record categories (CARGO_VC, CARGO_TC, etc.) untouched.
    """
    # Step 1: Propagate last seen vessel name for tonnage records that have no name
    last_vessel_name = None
    for r in records:
        if r.get("category") == "TONNAGE":
            name = r.get("vessel_name")
            if name:
                last_vessel_name = name
            elif last_vessel_name:
                r["vessel_name"] = last_vessel_name

    tonnage_records = [r for r in records if r.get("category") == "TONNAGE"]
    other_records = [r for r in records if r.get("category") != "TONNAGE"]
    
    merged_tonnage = {}
    
    for r in tonnage_records:
        name = r.get("vessel_name")
        if not name:
            # If no name, keep it as is by mapping to a unique key
            key = f"UNNAMED_{id(r)}"
        else:
            key = name.strip().upper()
            
        if key not in merged_tonnage:
            merged_tonnage[key] = r
        else:
            # Merge with existing record
            merged_tonnage[key] = merge_tonnage_records(merged_tonnage[key], r)
            
    final_records = list(merged_tonnage.values()) + other_records
    
    # Filter out empty/placeholder records (e.g. TONNAGE records with no extracted vessel fields)
    final_records = [r for r in final_records if not _is_empty_record(r)]
    
    # Calculate confidence scoring for each final record
    for r in final_records:
        add_confidence_scoring(r)
        
    return final_records


def add_confidence_scoring(record: dict) -> dict:
    """Calculate confidence score (0-100) and confidence level (HIGH/MEDIUM/LOW)."""
    category = record.get("category")
    score = 0
    
    if category == "TONNAGE":
        if record.get("vessel_name"): score += 30
        if record.get("vessel_size_dwt"): score += 20
        if record.get("open_port"): score += 20
        if record.get("open_date"): score += 20
        if record.get("flag"): score += 5
        if record.get("built_year"): score += 5
    elif category == "CARGO_VC":
        if record.get("cargo_name"): score += 30
        if record.get("loading_port"): score += 20
        if record.get("discharge_port"): score += 20
        if record.get("laycan_raw"): score += 20
        if record.get("quantity"): score += 10
    elif category == "CARGO_TC":
        if record.get("delivery_port"): score += 30
        if record.get("redelivery_port"): score += 20
        if record.get("laycan_raw"): score += 20
        if record.get("duration"): score += 20
        if record.get("vessel_size"): score += 10
    else:
        score = 100
        
    record["confidence_score"] = score
    
    if score >= 80:
        record["confidence_level"] = "HIGH"
    elif score >= 40:
        record["confidence_level"] = "MEDIUM"
    else:
        record["confidence_level"] = "LOW"
        
    return record
