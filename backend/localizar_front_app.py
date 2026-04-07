from pathlib import Path
import re

for p in Path(".").rglob("*.py"):
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except:
        continue

    if "/app" in text or "StaticFiles" in text or "HTMLResponse" in text or "FileResponse" in text:
        print(f"\n=== {p} ===")
        for i, line in enumerate(text.splitlines(), 1):
            if "/app" in line or "StaticFiles" in line or "HTMLResponse" in line or "FileResponse" in line:
                print(f"{i}: {line}")
