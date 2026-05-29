"""
writer.py — read/write the record store (data/records/<id>.json).

One JSON file per record, matching schema/record.md exactly.
The viewer globs data/records/*.json; we write, it reads.
"""

import json
from pathlib import Path
from typing import Optional

RECORDS_DIR = Path(__file__).parents[2] / 'data' / 'records'


def write_record(record: dict) -> Path:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    out = RECORDS_DIR / f"{record['id']}.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')
    return out


def load_record(record_id: str) -> Optional[dict]:
    p = RECORDS_DIR / f'{record_id}.json'
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None


def list_records() -> list[dict]:
    if not RECORDS_DIR.exists():
        return []
    out = []
    for p in sorted(RECORDS_DIR.glob('*.json')):
        try:
            out.append(json.loads(p.read_text(encoding='utf-8')))
        except Exception:
            pass
    return out


def prune_records(prefix: str, keep_ids: set[str]) -> int:
    """Delete stale generated records for one prefix while leaving .gitkeep intact."""
    if not RECORDS_DIR.exists():
        return 0

    removed = 0
    for p in RECORDS_DIR.glob(f'{prefix}*.json'):
        record_id = p.stem
        if record_id in keep_ids:
            continue
        p.unlink(missing_ok=True)
        removed += 1
    return removed
