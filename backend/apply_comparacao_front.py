from pathlib import Path

ROOT = Path(".").resolve()

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".mypy_cache", ".pytest_cache", ".idea", ".vscode"
}

def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)

html_files = []
for p in ROOT.rglob("*.html"):
    if should_ignore(p):
        continue
    html_files.append(p)

if not html_files:
    print("ERRO: nenhum arquivo HTML encontrado no projeto.")
    raise SystemExit(1)

css_content = r"""
#comparacao-section-smart {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

#comparacao-section-smart h2 {
  margin-top: 0;
  margin-bottom: 16px;
}

.smart-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.smart-field {
  display: flex;
  flex-direction: column;
  min-width: 220px;
  flex: 1;
}

.smart-field label {
  margin-bottom: 6px;
  font-weight: 600;
}

.smart-field select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.smart-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 8px;
  margin-bottom: 12px;
}

.smart-actions button {
  padding: 10px 14px;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
}

#comparacao-loading-smart {
  display: none;
  margin-top: 12px;
}

#comparacao-erro-smart {
  display: none;
  color: #c62828;
  margin-top: 12px;
}

#comparacao-resultado-smart {
  margin-top: 20px;
}

.smart-result-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 12px;
  background: #fafafa;
}

.smart-result-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.smart-result-subtitle {
  font-size: 14px;
  color: #555;
  margin-bottom: 10px;
}

.smart-result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.smart-result-item {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 10px;
}

.smart-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: #e8f5e9;
  color: #2e7d32;
  margin-bottom: 8px;
}

.smart-badge.warn {
  background: #fff3e0;
  color: #ef6c00;
}
""".strip() + "\n"

js_content = r"""
(function () {
  if (window.__SMART_COMPARACAO_INIT__) return;
  window.__SMART_COMPARACAO_INIT__ = true;

  const API_BASE =
    (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost")
      ? "http://127.0.0.1:8000/api"
      : "https://smart-compras.onrender.com/api";

  function getToken() {
    return localStorage.getItem("token");
  }

  async function apiFetch(path, options = {}) {
    const token = getToken();

    const headers = {
      ...(options.headers || {})
    };

    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    const contentType = response.headers.get("content-type") || "";
    let data;

    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const message =
        typeof data === "object" && data && data.detail
          ? data.detail
          : typeof data === "string" && data
          ? data
          : `Erro HTTP ${response.status}`;
      throw new Error(message);
    }

    return data;
  }

  function moeda(valor) {
    const numero = Number(valor || 0);
    return numero.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  function escapeHtml(texto) {
    return String(texto ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function ensureComparacaoUI() {
    if (document.getElementById("comparacao-section-smart")) return;

    const section = document.createElement("section");
    section.id = "comparacao-section-smart";
    section.innerHTML = `
      <h2>Comparação de preços</h2>

      <div class="smart-row">
        <div class="smart-field">
          <label for="compare-lista-select-smart">Lista</label>
          <select id="compare-lista-select-smart">
            <option value="">Selecione uma lista</option>
          </select>
        </div>

        <div class="smart-field">
          <label for="compare-cidade-select-smart">Cidade</label>
          <select id="compare-cidade-select-smart">
            <option value="">Selecione uma cidade</option>
          </select>
        </div>
      </div>

      <div class="smart-actions">
        <button id="btn-comparar-cidade-smart" type="button">Comparar cidade</button>
        <button id="btn-comparar-otimizada-smart" type="button">Comparação otimizada</button>
        <button id="btn-comparar-resumo-smart" type="button">Ver resumo</button>
      </div>

      <div id="comparacao-loading-smart">Carregando comparação...</div>
      <div id="comparacao-erro-smart"></div>
      <div id="comparacao-resultado-smart"></div>
    `;

    document.body.appendChild(section);
  }

  function setLoading(isLoading) {
    const el = document.getElementById("comparacao-loading-smart");
    if (el) el.style.display = isLoading ? "block" : "none";
  }

  function setErro(message = "") {
    const el = document.getElementById("comparacao-erro-smart");
    if (!el) return;
    if (message) {
      el.textContent = message;
      el.style.display = "block";
    } else {
      el.textContent = "";
      el.style.display = "none";
    }
  }

  function getFiltros() {
    const listaId = document.getElementById("compare-lista-select-smart")?.value;
    const cidadeId = document.getElementById("compare-cidade-select-smart")?.value;

    if (!listaId) throw new Error("Selecione uma lista para comparar.");
    if (!cidadeId) throw new Error("Selecione uma cidade para comparar.");

    return {
      listaId: Number(listaId),
      cidadeId: Number(cidadeId),
    };
  }

  async function carregarListas() {
    const select = document.getElementById("compare-lista-select-smart");
    if (!select) return;

    const listas = await apiFetch("/listas");
    select.innerHTML = `<option value="">Selecione uma lista</option>`;

    listas.forEach((lista) => {
      const option = document.createElement("option");
      option.value = lista.id;
      option.textContent = lista.nome || `Lista ${lista.id}`;
      select.appendChild(option);
    });
  }

  async function carregarCidades() {
    const select = document.getElementById("compare-cidade-select-smart");
    if (!select) return;

    const cidades = await apiFetch("/cidades");
    select.innerHTML = `<option value="">Selecione uma cidade</option>`;

    cidades.forEach((cidade) => {
      const option = document.createElement("option");
      option.value = cidade.id;
      option.textContent = cidade.nome || cidade.nome_cidade || `Cidade ${cidade.id}`;
      select.appendChild(option);
    });
  }

  async function buscarComparacaoCidade(listaId, cidadeId) {
    return await apiFetch(`/comparacao/cidade?lista_id=${listaId}&cidade_id=${cidadeId}`);
  }

  async function buscarComparacaoOtimizada(listaId, cidadeId) {
    return await apiFetch(`/comparacao/otimizada?lista_id=${listaId}&cidade_id=${cidadeId}`);
  }

  async function buscarComparacaoResumo(listaId, cidadeId) {
    return await apiFetch(`/comparacao/resumo?lista_id=${listaId}&cidade_id=${cidadeId}`);
  }

  function renderComparacaoCidade(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    const melhorMercado =
      data.melhor_mercado ||
      data.supermercado ||
      data.mercado ||
      data.resultado ||
      {};

    const nomeMercado =
      melhorMercado.nome ||
      melhorMercado.mercado_nome ||
      data.melhor_mercado_nome ||
      "Mercado não informado";

    const total =
      melhorMercado.total ||
      data.total ||
      data.valor_total ||
      data.melhor_total ||
      0;

    const economia =
      data.economia ||
      data.economia_total ||
      data.valor_economizado ||
      0;

    const itens =
      Array.isArray(data)
        ? data
        : data.itens ||
          melhorMercado.itens ||
          data.detalhes ||
          [];

    container.innerHTML = `
      <div class="smart-result-card">
        <div class="smart-badge">Melhor mercado da cidade</div>
        <div class="smart-result-title">${escapeHtml(nomeMercado)}</div>
        <div class="smart-result-subtitle">Total estimado: <strong>${moeda(total)}</strong></div>
        ${economia ? `<div class="smart-result-subtitle">Economia estimada: <strong>${moeda(economia)}</strong></div>` : ""}
      </div>

      <div class="smart-result-card">
        <div class="smart-result-title">Itens encontrados</div>
        <div class="smart-result-grid">
          ${
            itens.length
              ? itens.map((item) => {
                  const nome = item.produto_nome || item.nome || "Produto";
                  const qtd = item.quantidade || 1;
                  const preco = item.preco || item.preco_unitario || item.valor || 0;
                  return `
                    <div class="smart-result-item">
                      <strong>${escapeHtml(nome)}</strong><br>
                      Quantidade: ${escapeHtml(qtd)}<br>
                      Preço: ${moeda(preco)}
                    </div>
                  `;
                }).join("")
              : `<div class="smart-result-item">Nenhum detalhe de item retornado pelo backend.</div>`
          }
        </div>
      </div>
    `;
  }

  function renderComparacaoOtimizada(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    const itens =
      Array.isArray(data)
        ? data
        : data.itens ||
          data.resultado ||
          data.melhores_opcoes ||
          [];

    const total =
      data.total ||
      data.valor_total ||
      data.total_otimizado ||
      0;

    container.innerHTML = `
      <div class="smart-result-card">
        <div class="smart-badge warn">Melhor por item</div>
        <div class="smart-result-title">Compra otimizada</div>
        <div class="smart-result-subtitle">Total estimado da estratégia otimizada: <strong>${moeda(total)}</strong></div>
      </div>

      <div class="smart-result-card">
        <div class="smart-result-title">Melhor opção por produto</div>
        <div class="smart-result-grid">
          ${
            itens.length
              ? itens.map((item) => {
                  const produto = item.produto_nome || item.nome || item.produto || "Produto";
                  const mercado = item.mercado_nome || item.supermercado_nome || item.mercado || "Mercado não informado";
                  const preco = item.preco || item.preco_unitario || item.valor || 0;
                  const quantidade = item.quantidade || 1;

                  return `
                    <div class="smart-result-item">
                      <strong>${escapeHtml(produto)}</strong><br>
                      Mercado: ${escapeHtml(mercado)}<br>
                      Quantidade: ${escapeHtml(quantidade)}<br>
                      Preço: ${moeda(preco)}
                    </div>
                  `;
                }).join("")
              : `<div class="smart-result-item">Nenhum item otimizado retornado.</div>`
          }
        </div>
      </div>
    `;
  }

  function renderComparacaoResumo(data) {
    const container = document.getElementById("comparacao-resultado-smart");
    if (!container) return;

    const melhorMercado =
      data.melhor_mercado_nome ||
      data.mercado_nome ||
      data.melhor_mercado ||
      "Não informado";

    const totalMelhor =
      data.melhor_total ||
      data.total_melhor_mercado ||
      data.total ||
      0;

    const totalOtimizado =
      data.total_otimizado ||
      data.melhor_total_otimizado ||
      0;

    const economia =
      data.economia ||
      data.economia_estimada ||
      data.valor_economizado ||
      Math.max(Number(totalMelhor || 0) - Number(totalOtimizado || 0), 0);

    const mensagem =
      data.resumo ||
      data.mensagem ||
      data.insight ||
      "Resumo gerado com base na comparação da sua lista.";

    container.innerHTML = `
      <div class="smart-result-card">
        <div class="smart-badge">Resumo inteligente</div>
        <div class="smart-result-title">Análise da compra</div>
        <div class="smart-result-subtitle">${escapeHtml(mensagem)}</div>
      </div>

      <div class="smart-result-grid">
        <div class="smart-result-item">
          <strong>Melhor mercado único</strong><br>
          ${escapeHtml(melhorMercado)}
        </div>

        <div class="smart-result-item">
          <strong>Total em um mercado</strong><br>
          ${moeda(totalMelhor)}
        </div>

        <div class="smart-result-item">
          <strong>Total otimizado</strong><br>
          ${moeda(totalOtimizado)}
        </div>

        <div class="smart-result-item">
          <strong>Economia possível</strong><br>
          ${moeda(economia)}
        </div>
      </div>
    `;
  }

  async function onCompararCidade() {
    try {
      setErro("");
      setLoading(true);
      const { listaId, cidadeId } = getFiltros();
      const data = await buscarComparacaoCidade(listaId, cidadeId);
      console.log("Comparação cidade:", data);
      renderComparacaoCidade(data);
    } catch (error) {
      console.error(error);
      setErro(error.message || "Erro ao comparar preços por cidade.");
    } finally {
      setLoading(false);
    }
  }

  async function onCompararOtimizada() {
    try {
      setErro("");
      setLoading(true);
      const { listaId, cidadeId } = getFiltros();
      const data = await buscarComparacaoOtimizada(listaId, cidadeId);
      console.log("Comparação otimizada:", data);
      renderComparacaoOtimizada(data);
    } catch (error) {
      console.error(error);
      setErro(error.message || "Erro ao gerar comparação otimizada.");
    } finally {
      setLoading(false);
    }
  }

  async function onCompararResumo() {
    try {
      setErro("");
      setLoading(true);
      const { listaId, cidadeId } = getFiltros();
      const data = await buscarComparacaoResumo(listaId, cidadeId);
      console.log("Resumo comparação:", data);
      renderComparacaoResumo(data);
    } catch (error) {
      console.error(error);
      setErro(error.message || "Erro ao gerar resumo.");
    } finally {
      setLoading(false);
    }
  }

  async function initComparacao() {
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
  }

  function boot() {
    initComparacao().catch((e) => {
      console.error("Falha ao iniciar comparação:", e);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
""".strip() + "\n"

patched = []

for html_file in html_files:
    html_text = html_file.read_text(encoding="utf-8", errors="ignore")

    css_path = html_file.with_name("smart-comparacao.css")
    js_path = html_file.with_name("smart-comparacao.js")

    css_path.write_text(css_content, encoding="utf-8")
    js_path.write_text(js_content, encoding="utf-8")

    changed = False

    if "smart-comparacao.css" not in html_text:
        inject_css = '\n<link rel="stylesheet" href="smart-comparacao.css">\n'
        if "</head>" in html_text:
            html_text = html_text.replace("</head>", inject_css + "</head>")
        else:
            html_text = inject_css + html_text
        changed = True

    if "smart-comparacao.js" not in html_text:
        inject_js = '\n<script src="smart-comparacao.js"></script>\n'
        if "</body>" in html_text:
            html_text = html_text.replace("</body>", inject_js + "</body>")
        else:
            html_text = html_text + inject_js
        changed = True

    if changed:
        backup = html_file.with_suffix(html_file.suffix + ".bak")
        if not backup.exists():
            backup.write_text(html_file.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        html_file.write_text(html_text, encoding="utf-8")
        patched.append(html_file)

print("OK: arquivos HTML encontrados:")
for f in html_files:
    print(" -", f.relative_to(ROOT))

print("")
print("OK: HTMLs alterados:")
for f in patched:
    print(" -", f.relative_to(ROOT))

if not patched:
    print("AVISO: os arquivos smart-comparacao.* foram criados, mas nenhum HTML precisou ser alterado.")
else:
    print("")
    print("OK: frontend de comparação injetado com sucesso.")
