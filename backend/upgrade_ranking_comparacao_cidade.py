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
    const unidades = Array.isArray(data.unidades) ? data.unidades : [];
    const melhorId = data.melhor_unidade_id || null;

    const rankingOrdenado = [...unidades].sort((a, b) => {
      const totalA = Number(a.total || 0);
      const totalB = Number(b.total || 0);
      return totalA - totalB;
    });

    const melhor = rankingOrdenado.find(u => u.unidade_id === melhorId) || rankingOrdenado[0] || null;
    const itensMelhor = melhor && Array.isArray(melhor.itens) ? melhor.itens : [];
    const disponiveis = itensMelhor.filter(i => i.disponivel);
    const indisponiveis = itensMelhor.filter(i => !i.disponivel);

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
        <div class="smart-section-title">Ranking dos mercados</div>
        <div class="smart-result-grid">
          ${
            rankingOrdenado.length
              ? rankingOrdenado.map((item, idx) => {
                  const nomeUnidade = item.unidade_nome || "Unidade";
                  const nomeRede = item.rede_nome || "Rede não informada";
                  const totalUnidade = Number(item.total || 0);
                  const itens = Array.isArray(item.itens) ? item.itens : [];
                  const qtdDisponiveis = itens.filter(i => i.disponivel).length;
                  const badge = idx === 0
                    ? '<div class="smart-badge">Mais barato</div>'
                    : '<div class="smart-muted">Posição #' + (idx + 1) + '</div>';

                  return `
                    <div class="smart-result-item">
                      ${badge}<br>
                      <strong>${escapeHtml(nomeUnidade)}</strong><br>
                      Rede: ${escapeHtml(nomeRede)}<br>
                      Total: ${moeda(totalUnidade)}<br>
                      Itens disponíveis: ${qtdDisponiveis}/${itens.length}
                    </div>
                  `;
                }).join("")
              : `<div class="smart-empty">Nenhum mercado retornado pela comparação.</div>`
          }
        </div>
      </div>

      <div class="smart-result-card">
        <div class="smart-section-title">Itens do melhor mercado</div>
        <div class="smart-result-grid">
          ${
            itensMelhor.length
              ? itensMelhor.map((item) => {
                  const nome = item.produto_nome || "Produto";
                  const qtd = item.quantidade || 1;
                  const preco = Number(item.preco_unitario || 0);
                  const subtotal = Number(item.subtotal || 0);
                  const status = item.disponivel
                    ? '<span class="smart-ok">Disponível</span>'
                    : '<span class="smart-warn-text">Indisponível</span>';

                  return `
                    <div class="smart-result-item">
                      <strong>${escapeHtml(nome)}</strong><br>
                      Quantidade: ${escapeHtml(qtd)}<br>
                      Preço unitário: ${moeda(preco)}<br>
                      Subtotal: ${moeda(subtotal)}<br>
                      Status: ${status}
                    </div>
                  `;
                }).join("")
              : `<div class="smart-empty">Nenhum item retornado para a melhor unidade.</div>`
          }
        </div>
      </div>
    `;
  }
'''.strip()

pattern = r'function renderComparacaoCidade\(data\) \{.*?\n  \}'
text_new, count = re.subn(pattern, novo_render_cidade, text, flags=re.S)

if not count:
    print("ERRO: renderComparacaoCidade nao encontrado")
    raise SystemExit(1)

file.write_text(text_new, encoding="utf-8")
print("OK: renderComparacaoCidade atualizado com ranking")
