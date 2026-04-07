from pathlib import Path
import re

file = Path("app/web/smart-comparacao.js")
text = file.read_text(encoding="utf-8")

old_actions = """
      <div class="smart-actions">
        <button id="btn-comparar-cidade-smart" type="button">Comparar cidade</button>
        <button id="btn-comparar-otimizada-smart" type="button">Comparação otimizada</button>
        <button id="btn-comparar-resumo-smart" type="button">Ver resumo</button>
      </div>
""".strip()

new_actions = """
      <div class="smart-tabs">
        <button id="btn-comparar-cidade-smart" class="smart-tab-btn active" type="button">Cidade</button>
        <button id="btn-comparar-otimizada-smart" class="smart-tab-btn" type="button">Otimizada</button>
        <button id="btn-comparar-resumo-smart" class="smart-tab-btn" type="button">Resumo</button>
      </div>

      <div id="comparacao-view-hint-smart" class="smart-view-hint">
        Veja o melhor mercado único para sua lista nesta cidade.
      </div>
""".strip()

if old_actions not in text:
    print("ERRO: bloco antigo de botoes nao encontrado")
    raise SystemExit(1)

text = text.replace(old_actions, new_actions)

helper_code = r'''
  function setActiveTab(tab) {
    const map = {
      cidade: "Veja o melhor mercado único para sua lista nesta cidade.",
      otimizada: "Veja a melhor combinação por item, mesmo dividindo a compra.",
      resumo: "Veja a recomendação inteligente com economia estimada."
    };

    const btnCidade = document.getElementById("btn-comparar-cidade-smart");
    const btnOtimizada = document.getElementById("btn-comparar-otimizada-smart");
    const btnResumo = document.getElementById("btn-comparar-resumo-smart");
    const hint = document.getElementById("comparacao-view-hint-smart");

    [btnCidade, btnOtimizada, btnResumo].forEach((btn) => {
      if (btn) btn.classList.remove("active");
    });

    if (tab === "cidade" && btnCidade) btnCidade.classList.add("active");
    if (tab === "otimizada" && btnOtimizada) btnOtimizada.classList.add("active");
    if (tab === "resumo" && btnResumo) btnResumo.classList.add("active");

    if (hint) {
      hint.textContent = map[tab] || "";
    }
  }
'''.strip()

if "function setActiveTab(tab)" not in text:
    insert_after = "function setErro(message = \"\") {"
    idx = text.find(insert_after)
    if idx == -1:
        print("ERRO: ponto de insercao nao encontrado")
        raise SystemExit(1)

    end_idx = text.find("}", idx)
    end_idx = text.find("\n", end_idx)
    text = text[:end_idx] + "\n\n" + helper_code + "\n" + text[end_idx:]

text = text.replace(
    '      const data = await buscarComparacaoCidade(listaId, cidadeId);',
    '      setActiveTab("cidade");\n      const data = await buscarComparacaoCidade(listaId, cidadeId);'
)

text = text.replace(
    '      const data = await buscarComparacaoOtimizada(listaId, cidadeId);',
    '      setActiveTab("otimizada");\n      const data = await buscarComparacaoOtimizada(listaId, cidadeId);'
)

text = text.replace(
    '      const data = await buscarComparacaoResumo(listaId, cidadeId);',
    '      setActiveTab("resumo");\n      const data = await buscarComparacaoResumo(listaId, cidadeId);'
)

file.write_text(text, encoding="utf-8")
print("OK: comparacao convertida para navegacao por abas")
