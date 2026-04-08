from pathlib import Path
import re

path = Path(r".\app\web\index.html")
text = path.read_text(encoding="utf-8")

pattern = r'async function apiFetch\(url, options\) \{[\s\S]*?return fetch\(url, Object\.assign\([\s\S]*?\)\);\s*\}'
replacement = '''async function apiFetch(url, options) {
  return fetch(url, options || {});
}'''

text, count = re.subn(pattern, replacement, text)
print("apiFetch substituido:", count)

path.write_text(text, encoding="utf-8")
