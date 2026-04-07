from pathlib import Path

file = Path("app/web/smart-comparacao.css")
text = file.read_text(encoding="utf-8")

extra = """

.smart-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 12px 0 18px;
}

.smart-tab-btn {
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
  font-weight: 700;
}

.smart-tab-btn.active {
  border-color: #111827;
  background: #111827;
  color: white;
}

.smart-view-hint {
  margin-bottom: 14px;
  color: #666;
  font-size: 14px;
}
""".strip()

if extra not in text:
    text += "\n\n" + extra + "\n"

file.write_text(text, encoding="utf-8")
print("OK: estilos de abas adicionados")
