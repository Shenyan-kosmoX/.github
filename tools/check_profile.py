"""Validate published profile assets and local links without network access."""
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []
for required in ("profile/README.md", "MANIFESTO.md", "ASSET-SOURCES.md", "BRAND.md", "LICENSE"):
    if not (root / required).is_file():
        errors.append(f"Missing {required}")
try:
    manifest = json.loads((root / "art-direction.json").read_text(encoding="utf-8"))
    for name, digest in manifest["sha256"].items():
        p = root / "profile/assets" / name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            errors.append(f"Asset checksum mismatch: {name}; update the source record deliberately")
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        if "{{" in text:
            errors.append(f"Unresolved template in {p.name}")
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            if not (p.parent / target.split("#")[0]).exists():
                errors.append(f"Broken local link in {p.name}: {target}")
except (OSError, ValueError, KeyError) as exc:
    errors.append(str(exc))
print(json.dumps({"status": "failed" if errors else "passed", "errors": errors,
                  "scope": "Profile files, local links and image provenance; not a science review."}, ensure_ascii=False, indent=2))
sys.exit(bool(errors))
