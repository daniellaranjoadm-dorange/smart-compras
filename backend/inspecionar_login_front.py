from pathlib import Path

targets = [
    Path("app/web/index.html"),
    Path("app/web/smart-comparacao.js"),
]

patterns = [
    "localStorage",
    "setItem",
    "getItem",
    "login",
    "access_token",
    "token",
    "/auth/login",
    "/api/auth/login",
]

for path in targets:
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    print(f"\n=== {path} ===")
    lines = text.splitlines()

    for i, line in enumerate(lines, 1):
        lower = line.lower()
        if any(p.lower() in lower for p in patterns):
            print(f"{i}: {line}")
