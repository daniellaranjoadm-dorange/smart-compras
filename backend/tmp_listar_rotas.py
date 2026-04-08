from app.main import app

for route in app.routes:
    methods = ",".join(sorted(m for m in (route.methods or []) if m not in {"HEAD", "OPTIONS"}))
    path = getattr(route, "path", "")
    if methods and path:
        print(f"{methods:10} {path}")
