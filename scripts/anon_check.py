"""Run Licita's anonymity gate over this repo: no buyer, region or tribunal named in tracked files.

Uses Licita's keyed denylist (anon/denylist.sha256) and private key, so the plain list never lands here.
  uv run --project ~/Projects/licita python scripts/anon_check.py
"""
import os
import sys
from pathlib import Path

from licita import anon

LICITA = Path(os.environ.get("LICITA_HOME", Path.home() / "Projects/licita"))
ROOT = Path(__file__).resolve().parent.parent

key = anon.load_key(LICITA / "private" / "anon.key")
hashes = anon.load_hashes(LICITA / "anon" / "denylist.sha256")
findings = anon.check(root=ROOT, hashes=hashes, key=key)
for f in findings:
    print(f)
print(f"{len(findings)} finding(s) in {len(anon.tracked_files(ROOT))} files")
sys.exit(1 if findings else 0)
