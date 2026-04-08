from app.main import app

for route in app.routes:
    path = getattr(route, "path", None)
    methods = getattr(route, "methods", None)
    if path and ("lista" in path.lower() or "listas" in path.lower()):
        print(path, methods)
