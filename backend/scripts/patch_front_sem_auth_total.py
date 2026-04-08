from pathlib import Path
import re

path = Path(r".\app\web\index.html")
text = path.read_text(encoding="utf-8")

# 1) getToken sempre retorna token fake em modo dev
text = re.sub(
    r'function getToken\(\)\s*\{[\s\S]*?\}',
    '''function getToken() {
      return "dev-token";
    }''',
    text,
    count=1
)

# 2) apiFetch sem Authorization
text = re.sub(
    r'async function apiFetch\(url, options\)\s*\{[\s\S]*?return fetch\(url, Object\.assign\(\{\}, options \|\| \{\}, \{ headers: headers \}\)\);\s*\}',
    '''async function apiFetch(url, options) {
      return fetch(url, options || {});
    }''',
    text,
    count=1
)

# 3) desarma verificação auth/me
text = text.replace('const response = await apiFetch(API_BASE + "/auth/me");', 'return;')

# 4) remove bloqueio por falta de token
text = text.replace('if (!token) {', 'if (false) {')

path.write_text(text, encoding="utf-8")
print("index.html ajustado para modo dev sem auth.")
