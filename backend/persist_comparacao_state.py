from pathlib import Path

file = Path("app/web/smart-comparacao.js")
text = file.read_text(encoding="utf-8")

if 'const COMPARACAO_STORAGE_KEY =' not in text:
    text = text.replace(
        '  let currentComparacaoTab = "cidade";',
        '  let currentComparacaoTab = "cidade";\n  const COMPARACAO_STORAGE_KEY = "smartcompras_comparacao_state";'
    )

helper_block = '''
  function saveComparacaoState() {
    const listaId = document.getElementById("compare-lista-select-smart")?.value || "";
    const cidadeId = document.getElementById("compare-cidade-select-smart")?.value || "";

    const payload = {
      listaId,
      cidadeId,
      tab: currentComparacaoTab,
    };

    localStorage.setItem(COMPARACAO_STORAGE_KEY, JSON.stringify(payload));
  }

  function loadComparacaoState() {
    try {
      const raw = localStorage.getItem(COMPARACAO_STORAGE_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

'''.strip("\n")

if "function saveComparacaoState()" not in text:
    marker = '  function getFiltros() {'
    text = text.replace(marker, helper_block + "\n\n" + marker, 1)

text = text.replace(
    '    currentComparacaoTab = tab;',
    '    currentComparacaoTab = tab;\n    saveComparacaoState();'
)

old_init = '''    const autoRun = async () => {
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

new_init = '''    const autoRun = async () => {
      const listaId = selectLista?.value;
      const cidadeId = selectCidade?.value;

      saveComparacaoState();

      if (!listaId || !cidadeId) return;

      try {
        await runActiveComparacao();
      } catch (e) {
        console.error("Erro no auto compare:", e);
      }
    };

    if (selectLista) selectLista.addEventListener("change", autoRun);
    if (selectCidade) selectCidade.addEventListener("change", autoRun);

    const saved = loadComparacaoState();
    if (saved) {
      if (selectLista && saved.listaId) selectLista.value = saved.listaId;
      if (selectCidade && saved.cidadeId) selectCidade.value = saved.cidadeId;
      if (saved.tab) setActiveTab(saved.tab);
    }

    const hasSavedLista = selectLista?.value;
    const hasSavedCidade = selectCidade?.value;
    if (hasSavedLista && hasSavedCidade) {
      try {
        await runActiveComparacao();
      } catch (e) {
        console.error("Erro ao restaurar comparacao:", e);
      }
    }
  }'''

if old_init not in text:
    print("ERRO: bloco init esperado nao encontrado")
    raise SystemExit(1)

text = text.replace(old_init, new_init)

file.write_text(text, encoding="utf-8")
print("OK: estado da comparacao persistido no localStorage")
