from typing import List, Dict

def score_confidence(findings: List[Dict], threshold: float = 0.5) -> List[Dict]:
    """
    Assign a confidence score (0-1) to each finding and filter by threshold.

    Confidence = min(1.0, normalized length + normalized source count)

    Args:
        findings: List of findings dict with 'data' and 'sources' keys
        threshold: minimum confidence to keep

    Returns:
        Filtered and scored findings with added 'confidence' and 'sources' count
    """
    max_len = max(len(f["data"]) for f in findings) if findings else 1
    max_sources = max(len(f["sources"]) for f in findings) if findings else 1

    scored = []
    for f in findings:
        length_score = len(f["data"]) / max_len
        source_score = len(f["sources"]) / max_sources
        confidence = min(1.0, (length_score + source_score) / 2)

        if confidence >= threshold:
            scored.append({
                **f,
                "confidence": round(confidence, 3),
                "sources": len(f["sources"]),
            })

    return scored
