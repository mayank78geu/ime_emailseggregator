import re

def is_summary_line(line: str) -> bool:
    """Detect if a line is a standalone vessel summary line."""
    line_u = line.strip().upper()
    if not re.search(r'\bM[/\s\.]?V\b', line_u):
        return False
    
    # Summary lines are short standalone lines
    if len(line_u) > 150:
        return False
        
    # Check for keywords indicating a summary list line
    indicators = [
        r'\bDWT\b',
        r'\bOPEN\b',
        r'\bO/A\b',
        r'\bO\.A\.\b',
        r'\bONW\b',
        r'\bOPENING\b',
        # Month names
        r'\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    ]
    return any(re.search(pat, line_u) for pat in indicators)


def contains_particulars(block: str) -> bool:
    """Detect if a block contains detailed vessel particulars."""
    block_u = block.upper()
    particulars_indicators = [
        r'\bBUILT\b', r'\bFLAG\b', r'\bLOA\b', r'\bBEAM\b', 
        r'\bSPEED\b', r'\bCONS\b', r'\bCLASS\b', r'\bHO/HA\b',
        r'\bCRANES?\b', r'\bGRAIN\b', r'\bBALE\b'
    ]
    return any(re.search(pat, block_u) for pat in particulars_indicators)


def is_valid_cargo_block(block: str) -> bool:
    """Detect if a block contains a valid cargo requirement (VC or TC)."""
    block_u = block.upper()
    cargo_indicators = [
        r'\bLP\b', r'\bDP\b', r'\bPOL\b', r'\bPOD\b', 
        r'\bLOAD\s*PORT\b', r'\bDISCHARGE\s*PORT\b', 
        r'\bDELIVERY\b', r'\bREDELIVERY\b', r'\bDELY\b', r'\bREDEL\b',
        r'\bTCT\b', r'\bDURATION\b', r'\bLAYCAN\b', r'\bCARGO\b'
    ]
    if any(re.search(pat, block_u) for pat in cargo_indicators):
        return True
    
    # Check cargo qty pattern
    if re.search(r'\b[\d,\-\s\.]+\s*(?:MT|MTS|TONS?)\b', block_u):
        return True
    
    # Check route pattern while filtering out signature fake routes
    route_pat = re.compile(
        r'^[ \t]*([A-Z][A-Z \t\-]{2,20})\s*(?:/|->|\bTO\b)\s*([A-Z][A-Z \t\-]{2,20})[ \t]*$',
        re.IGNORECASE | re.MULTILINE
    )
    for m in route_pat.finditer(block_u):
        p1, p2 = m.group(1).strip(), m.group(2).strip()
        blacklist = {'REGARDS', 'DEAR', 'GOOD', 'DAY', 'BROKER', 'EMAIL', 'PHONE', 'FAX', 'TEL', 'SKYPE', 'HTTP', 'WWW', 'CLIENT', 'CHARTERER', 'OWNER', 'MASTER'}
        if any(term in p1 or term in p2 for term in blacklist):
            continue
        return True
        
    return False


def get_vessel_name(text: str) -> str | None:
    """Extract vessel name from a summary line or header line."""
    text_u = text.upper()
    # Match MV/M/V and then match capital letters and numbers until DWT or OPEN or O/A or a comma/dash
    match = re.search(r'\bM[/\s\.]?V\.?\s*[:\-]?\s*([A-Z0-9\s\-]{3,30}?)(?:\s+DWT|\s+–|\s+OPEN|\s+O/A|\s*,|\s*\(|$)', text_u)
    if match:
        return match.group(1).strip()
    return None


def split_cargo_block(block: str) -> list[str]:
    """Split a block of text into separate opportunities when it contains multiple cargo listings."""
    lines = block.split('\n')
    opportunities = []
    current_lines = []
    
    cargo_qty_pat = re.compile(
        r'^\s*(?:CARGO\s*[:\-]\s*)?[\d,\-\s\.]+\s*(?:MT|MTS|TONS?)\b',
        re.IGNORECASE
    )
    ac_pat = re.compile(r'^\s*\*?\s*(?:A/C|ACC)\b', re.IGNORECASE)
    num_pat = re.compile(r'^\s*(?:Cargo\s*\d+|\b\d+\s*(?:[\):]|\.(?!\d)))', re.IGNORECASE)
    route_pat = re.compile(
        r'^[ \t]*([A-Z][A-Z \t\-]{2,20})\s*(?:/|->|\bTO\b)\s*([A-Z][A-Z \t\-]{2,20})[ \t]*$',
        re.IGNORECASE
    )
    keywords_pat = re.compile(
        r'^\s*(?:POL|POD|LP|DP|LOAD\s*PORT|DISCHARGE\s*PORT|DELIVERY|DELY|REDELIVERY|REDEL|LAYCAN|LC)\b',
        re.IGNORECASE
    )

    has_cargo_name_or_qty = False
    has_ports = False
    has_laycan = False
    has_ac = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append(line)
            continue
            
        is_new = False
        is_rate = any(k in stripped.upper() for k in ['FHINC', 'SHINC', 'SSHEX', 'FHEX', 'CQD', 'PWWD', 'DISCH', 'LOAD RATE', 'DISCHARGE RATE'])
        
        if num_pat.search(stripped):
            is_new = True
        elif ac_pat.search(stripped) and (has_cargo_name_or_qty or has_ports or has_laycan or has_ac):
            is_new = True
        elif cargo_qty_pat.search(stripped) and has_cargo_name_or_qty and not is_rate:
            is_new = True
        elif route_pat.search(stripped) and has_ports:
            r_m = route_pat.search(stripped)
            p1, p2 = r_m.group(1).strip().upper(), r_m.group(2).strip().upper()
            blacklist = {'REGARDS', 'DEAR', 'GOOD', 'DAY', 'BROKER', 'EMAIL', 'PHONE', 'FAX', 'TEL', 'SKYPE', 'HTTP', 'WWW', 'CLIENT', 'CHARTERER', 'OWNER', 'MASTER'}
            if not any(term in p1 or term in p2 for term in blacklist):
                is_new = True
        elif keywords_pat.search(stripped):
            kw_match = keywords_pat.search(stripped).group().upper()
            if ('POL' in kw_match or 'LP' in kw_match or 'LOAD' in kw_match or 'DELY' in kw_match or 'DELIVERY' in kw_match) and has_ports:
                is_new = True
            elif ('LAYCAN' in kw_match or 'LC' in kw_match) and has_laycan:
                is_new = True
        
        if is_new and any(l.strip() for l in current_lines):
            opportunities.append('\n'.join(current_lines).strip())
            current_lines = []
            has_cargo_name_or_qty = False
            has_ports = False
            has_laycan = False
            has_ac = False
            
        if cargo_qty_pat.search(stripped) and not is_rate:
            has_cargo_name_or_qty = True
        if route_pat.search(stripped) or ('POL' in stripped.upper() or 'POD' in stripped.upper() or 'LP:' in stripped.upper() or 'DP:' in stripped.upper() or 'DELY' in stripped.upper()):
            is_valid_route = True
            if route_pat.search(stripped):
                r_m = route_pat.search(stripped)
                p1, p2 = r_m.group(1).strip().upper(), r_m.group(2).strip().upper()
                blacklist = {'REGARDS', 'DEAR', 'GOOD', 'DAY', 'BROKER', 'EMAIL', 'PHONE', 'FAX', 'TEL', 'SKYPE', 'HTTP', 'WWW', 'CLIENT', 'CHARTERER', 'OWNER', 'MASTER'}
                if any(term in p1 or term in p2 for term in blacklist):
                    is_valid_route = False
            if is_valid_route:
                has_ports = True
        if 'LAYCAN' in stripped.upper() or 'LC' in stripped.upper() or 'JULY' in stripped.upper() or 'JUNE' in stripped.upper() or 'AUG' in stripped.upper():
            has_laycan = True
        if ac_pat.search(stripped):
            has_ac = True
            
        current_lines.append(line)
        
    if any(l.strip() for l in current_lines):
        opportunities.append('\n'.join(current_lines).strip())
        
    return [op for op in opportunities if op]


def split_email_into_blocks(text: str) -> list:
    """
    Split a shipping email into individual record blocks.
    Each block represents one vessel (TONNAGE) or one cargo (VC/TC).
    Tuned for real-world shipping email formats.
    """
    original = text.strip()
    
    # Pre-clean heading underlines (e.g. "MV VESSEL\n======") to prevent splitting a title from its block
    # Exclude general section headers (like VSL PARTICULAR:) using a negative lookahead
    cleaned_text = re.sub(
        r'(\n[^\n]*\b(?:M[/\s\.]?V|VESSEL|VSL)\b(?!.*(?:PARTICULAR|LIST|SPEC|DETAIL|INFO))[^\n]*)\n\s*[-*=_]{3,}\s*(?=\n|$)',
        r'\1',
        "\n" + original
    ).strip()
    
    # ── Step 1: Split into major sections using horizontal separators and signature boundaries
    split_pat = re.compile(
        r'(?:\n|^)\s*(?:[^a-zA-Z0-9\n]*?[-*=_+~#—]{3,}[^a-zA-Z0-9\n]*?\s*(?:\n|$)|--\s*(?:\n|$)|Best\s+regards|Kind\s+regards|Regards|Thanks\s*(?:&\s*|and\s*)regards)\b',
        re.IGNORECASE
    )
    raw_blocks = split_pat.split(cleaned_text)
    
    processed_blocks = []
    
    # ── Step 2: Process each block
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
            
        if contains_particulars(block):
            # If the block contains detailed particulars, keep it as a whole
            processed_blocks.append(block)
        else:
            # If it doesn't contain particulars, check if it has summary lines
            lines = block.split('\n')
            summary_lines = []
            for line in lines:
                if is_summary_line(line):
                    summary_lines.append(line.strip())
            
            if summary_lines:
                # If we found summary lines, add each summary line as a standalone block
                processed_blocks.extend(summary_lines)
            else:
                # If there are no summary lines, check if it's a valid cargo block
                if is_valid_cargo_block(block):
                    cargo_opps = split_cargo_block(block)
                    for opp in cargo_opps:
                        if is_valid_cargo_block(opp):
                            processed_blocks.append(opp)
                # Otherwise, discard it as headers/footers/junk
                
    return processed_blocks
