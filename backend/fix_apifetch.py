from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

html = html.replace(
"""const headers = new Headers(options.headers || {});
      if (token) {
        headers.set("Authorization", "Bearer " + token);
      }
      return fetch(url, {
        ...options,
        headers
      });""",
"""const headers = {
        ...(options.headers || {})
      };

      if (token) {
        headers["Authorization"] = "Bearer " + token;
      }

      return fetch(url, {
        ...options,
        headers
      });"""
)

file.write_text(html, encoding="utf-8")
print("OK: apiFetch corrigido")
