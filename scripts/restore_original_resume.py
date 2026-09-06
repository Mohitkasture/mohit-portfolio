"""Restore original Enhancv resume from git, then the site will show the previous design."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "home" / "static" / "home" / "files" / "Mohit-Kasture-resume.pdf"
DOWNLOADS = Path.home() / "Downloads"
MK = DOWNLOADS / "Mohit-Kasture-resume mk.pdf"
BACKUP = DOWNLOADS / "Mohit-Kasture-resume mk.original-backup.pdf"


def main() -> None:
    tmp = ROOT / "scripts" / "_original-resume.pdf"
    subprocess.check_call(
        ["git", "show", "8f4344c:home/static/home/files/Mohit-Kasture-resume.pdf"],
        cwd=ROOT,
        stdout=tmp.open("wb"),
    )
    size = tmp.stat().st_size
    print("restored bytes", size)
    if size < 100000:
        raise SystemExit("git object is not the original Enhancv PDF")
    if not BACKUP.exists():
        shutil.copy2(tmp, BACKUP)
        print("backup", BACKUP)
    shutil.copy2(tmp, DEST)
    shutil.copy2(tmp, MK)
    print("wrote", DEST)
    print("wrote", MK)


if __name__ == "__main__":
    main()
