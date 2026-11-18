"""Small helpers shared across coursesmith."""
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


def slug(s, maxlen=60):
    s = re.sub(r"[\u2010-\u2015]", "-", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:maxlen].strip("-") or "x"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data, indent=1):
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=indent) + "\n")


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def write_jsonl(path, rows):
    atomic_write(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def words(text):
    return len(re.findall(r"\S+", text or ""))
