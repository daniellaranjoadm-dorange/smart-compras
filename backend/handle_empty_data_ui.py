from pathlib import Path
import re

file = Path("app/web/smart-comparacao.js")
text = file.read_text(encoding="utf-8")

# adicionar helper
helper = '''
  function isSemDadosComparacao(data) {
    if (!data) return true;

    const total =
      Number(data.total_otimizado || 0) +
      Number(data.total_melhor_unidade || 0) +
      Number(data.melhor_total || 0);

    const itens = data.itens || [];

    return total === 0 && (!itens || itens.length === 0);
  }

'''.strip()

if "isSemDadosComparacao" not in text:
    text = text.replace(
        "function renderComparacaoCidade(data) {",
        helper + "\n\n  function renderComparacaoCidade(data) {"
    )

# aplicar nos 3 renders
text = re.sub(
    r'function renderComparacaoCidade\(data\) \{',
    '''function renderComparacaoCidade(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    if (isSemDadosComparacao(data)) {
      container.innerHTML = `
        <div class="smart-empty">
          ⚠️ Ainda não temos dados de preços para essa cidade.<br>
          Tente outra cidade ou aguarde atualização dos dados.
        </div>
      `;
      return;
    }
''',
    text
)

text = re.sub(
    r'function renderComparacaoOtimizada\(data\) \{',
    '''function renderComparacaoOtimizada(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    if (isSemDadosComparacao(data)) {
      container.innerHTML = `
        <div class="smart-empty">
          ⚠️ Não há dados suficientes para otimização nesta cidade.
        </div>
      `;
      return;
    }
''',
    text
)

text = re.sub(
    r'function renderComparacaoResumo\(data\) \{',
    '''function renderComparacaoResumo(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    if (isSemDadosComparacao(data)) {
      container.innerHTML = `
        <div class="smart-empty">
          ⚠️ Não foi possível gerar resumo sem dados de preços.
        </div>
      `;
      return;
    }
''',
    text
)

file.write_text(text, encoding="utf-8")
print("OK: tratamento de cidade sem dados implementado")
