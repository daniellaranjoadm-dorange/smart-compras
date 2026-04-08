from pathlib import Path

path = Path(r".\app\web\index.html")
text = path.read_text(encoding="utf-8")

# forçar token fake
text = text.replace(
    "function getToken() {",
    """function getToken() {
      return "dev-token";
"""
)

# remover validação de token vazio
text = text.replace(
    "if (!token) {",
    "if (false) {"
)

path.write_text(text, encoding="utf-8")
print("Frontend ajustado para modo DEV (sem login obrigatório).")
