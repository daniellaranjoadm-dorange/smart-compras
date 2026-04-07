from pathlib import Path
import re

file = Path("app/web/smart-comparacao.js")
text = file.read_text(encoding="utf-8")

# 1) inserir estado global da aba
if 'let currentComparacaoTab = "cidade";' not in text:
    text = text.replace(
        '  const API_BASE = `${window.location.origin}/api`;',
        '  const API_BASE = `${window.location.origin}/api`;\n  let currentComparacaoTab = "cidade";'
    )

# 2) atualizar setActiveTab para guardar aba atual
text = text.replace(
    '  function setActiveTab(tab) {\n    const map = {',
    '  function setActiveTab(tab) {\n    currentComparacaoTab = tab;\n\n    const map = {'
)

# 3) adicionar funcao para executar aba atual
helper = '''
  async function runActiveComparacao() {
    if (currentComparacaoTab === "otimizada") {
      await onCompararOtimizada();
      return;
    }

    if (currentComparacaoTab === "resumo") {
      await onCompararResumo();
      return;
    }

    await onCompararCidade();
  }

'''.strip("\n")

if "async function runActiveComparacao()" not in text:
    marker = '  function getFiltros() {'
    text = text.replace(marker, helper + "\n\n" + marker, 1)

# 4) bind de change nos filtros para auto comparar
pattern = r'''  async function initComparacao\(\) \{
.*?
  \}'''
match = re.search(pattern, text, flags=re.S)
if not match:
    print("ERRO: initComparacao nao encontrado")
    raise SystemExit(1)

block = match.group(0)

if 'addEventListener("change"' not in block:
    old = '''  async function initComparacao() {
    ensureComparacaoUI();

    const btnCidade = document.getElementById("btn-comparar-cidade-smart");
    const btnOtimizada = document.getElementById("btn-comparar-otimizada-smart");
    const btnResumo = document.getElementById("btn-comparar-resumo-smart");

    if (btnCidade) btnCidade.addEventListener("click", onCompararCidade);
    if (btnOtimizada) btnOtimizada.addEventListener("click", onCompararOtimizada);
    if (btnResumo) btnResumo.addEventListener("click", onCompararResumo);

    try {
      await carregarListas();
    } catch (e) {
      console.error("Erro ao carregar listas:", e);
    }

    try {
      await carregarCidades();
    } catch (e) {
      console.error("Erro ao carregar cidades:", e);
    }
  }'''

    new = '''  async function initComparacao() {
    ensureComparacaoUI();

    const btnCidade = document.getElementById("btn-comparar-cidade-smart");
    const btnOtimizada = document.getElementById("btn-comparar-otimizada-smart");
    const btnResumo = document.getElementById("btn-comparar-resumo-smart");
    const selectLista = document.getElementById("compare-lista-select-smart");
    const selectCidade = document.getElementById("compare-cidade-select-smart");

    if (btnCidade) btnCidade.addEventListener("click", onCompararCidade);
    if (btnOtimizada) btnOtimizada.addEventListener("click", onCompararOtimizada);
    if (btnResumo) btnResumo.addEventListener("click", onCompararResumo);

    try {
      await carregarListas();
    } catch (e) {
      console.error("Erro ao carregar listas:", e);
    }

    try {
      await carregarCidades();
    } catch (e) {
      console.error("Erro ao carregar cidades:", e);
    }

    const autoRun = async () => {
      const listaId = selectLista?.value;
      const cidadeId = selectCidade?.value;
      if (!listaId || !cidadeId) return;

      try {
        await runActiveComparacao();
      } catch (e) {
        console.error("Erro no auto compare:", e);
      }
    };

    if (selectLista) selectLista.addEventListener("change", autoRun);
    if (selectCidade) selectCidade.addEventListener("change", autoRun);
  }'''

    text = text.replace(old, new)

file.write_text(text, encoding="utf-8")
print("OK: auto comparacao por filtros adicionada")
