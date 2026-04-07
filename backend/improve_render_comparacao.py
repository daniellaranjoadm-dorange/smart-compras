from pathlib import Path
import re

file = Path("app/web/smart-comparacao.js")
text = file.read_text(encoding="utf-8")

novo_render_cidade = r'''
  function renderComparacaoCidade(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    const unidade = data.melhor_unidade_nome || "Nenhuma unidade encontrada";
    const rede = data.melhor_rede_nome || "Rede não informada";
    const total = Number(data.melhor_total || data.total_melhor_unidade || 0);
    const itens = Array.isArray(data.itens) ? data.itens : [];
    const disponiveis = itens.filter(i => i.disponivel);
    const indisponiveis = itens.filter(i => !i.disponivel);

    container.innerHTML = `
      <div class="smart-result-card">
        <div class="smart-badge">Melhor mercado da cidade</div>
        <div class="smart-result-title">${escapeHtml(unidade)}</div>
        <div class="smart-result-subtitle">Rede: <strong>${escapeHtml(rede)}</strong></div>
      </div>

      <div class="smart-result-summary">
        <div class="smart-kpi">
          <div class="smart-kpi-label">Total estimado</div>
          <div class="smart-kpi-value">${moeda(total)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Itens disponíveis</div>
          <div class="smart-kpi-value">${disponiveis.length}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Itens indisponíveis</div>
          <div class="smart-kpi-value">${indisponiveis.length}</div>
        </div>
      </div>

      <div class="smart-result-card">
        <div class="smart-section-title">Itens da comparação</div>
        <div class="smart-result-grid">
          ${
            itens.length
              ? itens.map((item) => {
                  const nome = item.produto_nome || "Produto";
                  const qtd = item.quantidade || 1;
                  const preco = Number(item.preco_unitario || 0);
                  const subtotal = Number(item.subtotal || 0);
                  const redeNome = item.rede_nome || rede;
                  const status = item.disponivel
                    ? '<span class="smart-ok">Disponível</span>'
                    : '<span class="smart-warn-text">Indisponível</span>';

                  return `
                    <div class="smart-result-item">
                      <strong>${escapeHtml(nome)}</strong><br>
                      Quantidade: ${escapeHtml(qtd)}<br>
                      Rede: ${escapeHtml(redeNome || "Não informada")}<br>
                      Preço unitário: ${moeda(preco)}<br>
                      Subtotal: ${moeda(subtotal)}<br>
                      Status: ${status}
                    </div>
                  `;
                }).join("")
              : `<div class="smart-empty">Nenhum item retornado pela comparação.</div>`
          }
        </div>
      </div>
    `;
  }
'''.strip()

novo_render_otimizada = r'''
  function renderComparacaoOtimizada(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    const total = Number(data.total_otimizado || data.total || 0);
    const itens = Array.isArray(data.itens) ? data.itens : [];
    const mercados = new Set(
      itens
        .map(i => i.unidade_nome || i.mercado_nome || i.rede_nome)
        .filter(Boolean)
    );

    container.innerHTML = `
      <div class="smart-result-card">
        <div class="smart-badge warn">Melhor por item</div>
        <div class="smart-result-title">Compra otimizada</div>
      </div>

      <div class="smart-result-summary">
        <div class="smart-kpi">
          <div class="smart-kpi-label">Total otimizado</div>
          <div class="smart-kpi-value">${moeda(total)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Mercados usados</div>
          <div class="smart-kpi-value">${mercados.size}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Itens otimizados</div>
          <div class="smart-kpi-value">${itens.length}</div>
        </div>
      </div>

      <div class="smart-result-card">
        <div class="smart-section-title">Melhor opção por produto</div>
        <div class="smart-result-grid">
          ${
            itens.length
              ? itens.map((item) => {
                  const produto = item.produto_nome || item.nome || "Produto";
                  const unidade = item.unidade_nome || item.mercado_nome || "Mercado não informado";
                  const rede = item.rede_nome || "Rede não informada";
                  const preco = Number(item.preco_unitario || item.preco || 0);
                  const quantidade = item.quantidade || 1;
                  const subtotal = Number(item.subtotal || 0);

                  return `
                    <div class="smart-result-item">
                      <strong>${escapeHtml(produto)}</strong><br>
                      Unidade: ${escapeHtml(unidade)}<br>
                      Rede: ${escapeHtml(rede)}<br>
                      Quantidade: ${escapeHtml(quantidade)}<br>
                      Preço: ${moeda(preco)}<br>
                      Subtotal: ${moeda(subtotal)}
                    </div>
                  `;
                }).join("")
              : `<div class="smart-empty">Nenhum item otimizado retornado.</div>`
          }
        </div>
      </div>
    `;
  }
'''.strip()

novo_render_resumo = r'''
  function renderComparacaoResumo(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    const unidade = data.melhor_unidade_nome || "Não informado";
    const rede = data.melhor_rede_nome || "Não informada";
    const totalMelhor = Number(data.total_melhor_unidade || data.melhor_total || 0);
    const totalOtimizado = Number(data.total_otimizado || 0);
    const economia = Number(data.economia_valor || data.economia || 0);
    const percentual = Number(data.economia_percentual || 0);
    const recomendacao =
      data.recomendacao ||
      data.resumo ||
      "Resumo gerado com base na comparação da sua lista.";

    container.innerHTML = `
      <div class="smart-result-card">
        <div class="smart-badge">Resumo inteligente</div>
        <div class="smart-result-title">Análise da compra</div>
        <div class="smart-result-subtitle">${escapeHtml(recomendacao)}</div>
      </div>

      <div class="smart-result-summary">
        <div class="smart-kpi">
          <div class="smart-kpi-label">Melhor unidade</div>
          <div class="smart-kpi-value">${escapeHtml(unidade)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Rede</div>
          <div class="smart-kpi-value">${escapeHtml(rede)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Total em um mercado</div>
          <div class="smart-kpi-value">${moeda(totalMelhor)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Total otimizado</div>
          <div class="smart-kpi-value">${moeda(totalOtimizado)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Economia</div>
          <div class="smart-kpi-value">${moeda(economia)}</div>
        </div>
        <div class="smart-kpi">
          <div class="smart-kpi-label">Economia %</div>
          <div class="smart-kpi-value">${percentual.toFixed(2)}%</div>
        </div>
      </div>
    `;
  }
'''.strip()

patterns = [
    (r'function renderComparacaoCidade\(data\) \{.*?\n  \}', novo_render_cidade),
    (r'function renderComparacaoOtimizada\(data\) \{.*?\n  \}', novo_render_otimizada),
    (r'function renderComparacaoResumo\(data\) \{.*?\n  \}', novo_render_resumo),
]

changes = 0
for pattern, replacement in patterns:
    text_new, count = re.subn(pattern, replacement, text, flags=re.S)
    if count:
        text = text_new
        changes += count

file.write_text(text, encoding="utf-8")
print(f"OK: renders da comparacao atualizados. Alteracoes: {changes}")
