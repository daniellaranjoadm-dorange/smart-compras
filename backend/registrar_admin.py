from pathlib import Path

main_file = Path("backend/app/main.py")
content = main_file.read_text(encoding="utf-8")

import_line = "from app.routes import admin"
router_line = "app.include_router(admin.router)"

if import_line not in content:
    lines = content.splitlines()
    insert_at = 0
    while insert_at < len(lines) and (lines[insert_at].startswith("from ") or lines[insert_at].startswith("import ")):
        insert_at += 1
    lines.insert(insert_at, import_line)
    content = "\n".join(lines) + "\n"

if router_line not in content:
    if "app = FastAPI()" in content:
        content = content.replace("app = FastAPI()", "app = FastAPI()\n" + router_line, 1)
    else:
        content += "\n" + router_line + "\n"

main_file.write_text(content, encoding="utf-8")
print("OK: main.py atualizado")
