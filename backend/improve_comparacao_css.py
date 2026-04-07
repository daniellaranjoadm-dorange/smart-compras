from pathlib import Path

file = Path("app/web/smart-comparacao.css")
text = file.read_text(encoding="utf-8")

extra = """

.smart-result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.smart-kpi {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px;
}

.smart-kpi-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

.smart-kpi-value {
  font-size: 22px;
  font-weight: 800;
}

.smart-empty {
  padding: 16px;
  border: 1px dashed #ccc;
  border-radius: 10px;
  background: #fff;
}

.smart-ok {
  color: #2e7d32;
  font-weight: 700;
}

.smart-warn-text {
  color: #ef6c00;
  font-weight: 700;
}

.smart-muted {
  color: #666;
}

.smart-section-title {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 12px;
}

.smart-result-item strong {
  font-size: 18px;
}
""".strip()

if extra not in text:
    text += "\n\n" + extra + "\n"

file.write_text(text, encoding="utf-8")
print("OK: CSS da comparacao melhorado")
