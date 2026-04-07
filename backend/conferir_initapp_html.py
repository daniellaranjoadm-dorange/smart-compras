from pathlib import Path

file = Path("app/web/index.html")
lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()

for i, line in enumerate(lines, 1):
    if "initApp" in line or "DOMContentLoaded" in line:
        print(f"{i}: {line}")
