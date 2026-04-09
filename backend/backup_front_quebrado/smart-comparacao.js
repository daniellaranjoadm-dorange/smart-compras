
/* SMART_FIX_STATUS_SESSION_V1 */
function atualizarStatusSessao() {
  const authStatus = document.getElementById("smart-auth-status");
  const statusMsg = document.getElementById("statusMsg");
  const userInfo = document.getElementById("userInfo");

  const token = localStorage.getItem("smartcompras_token");

  if (authStatus) {
    authStatus.textContent = token ? "Sess?o autenticada" : "N?o autenticado";
  }

  if (statusMsg) {
    statusMsg.textContent = token ? "Autenticado" : "Fa?a login";
  }

  if (userInfo && token && !userInfo.textContent.trim()) {
    userInfo.textContent = "Usu?rio autenticado";
  }
}



/* FORCE_BIND_BUSCA_PRODUTO_V4 */
document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("buscarProdutoInput");
  const select = document.getElementById("itemProdutoSelect");

  if (!input || !select) {
    console.warn("Busca produto: elementos n?o encontrados");
    return;
  }

  let timeout = null;

  async function buscar(q) {
    const token = localStorage.getItem("smartcompras_token");
    if (!token) return;

    try {
      const resp = await fetch(`/api/produtos/busca?q=${encodeURIComponent(q)}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      const data = await resp.json();

      select.innerHTML = '<option value="">Selecione um produto</option>';

      if (!Array.isArray(data)) return;

      data.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.nome;
        select.appendChild(opt);
      });

    } catch (e) {
      console.error("Erro busca produto:", e);
    }
  }

  input.addEventListener("input", function () {
    clearTimeout(timeout);
    timeout = setTimeout(() => buscar(input.value), 300);
  });

  // carga inicial
  buscar("");
});


(function () {
  if (window.__SMART_COMPARACAO_INIT__) return;
  window.__SMART_COMPARACAO_INIT__ = true;

  const API_BASE = `${window.location.origin}/api`;
  const TOKEN_KEY = "smartcompras_token";
  const COMPARACAO_STORAGE_KEY = "smartcompras_comparacao_state";

  let currentComparacaoTab = "cidade";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
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

  function saveComparacaoState() {
    const listaId = document.getElementById("compare-lista-select-smart")?.value || "";
    const cidadeId = document.getElementById("compare-cidade-select-smart")?.value || "";

    localStorage.setItem(
      COMPARACAO_STORAGE_KEY,
      JSON.stringify({
        listaId,
        cidadeId,
        tab: currentComparacaoTab,
      })
    );
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

      <div class="smart-tabs">
        <button id="btn-comparar-cidade-smart" class="smart-tab-btn active" type="button">Cidade</button>
        <button id="btn-comparar-otimizada-smart" class="smart-tab-btn" type="button">Otimizada</button>
        <button id="btn-comparar-resumo-smart" class="smart-tab-btn" type="button">Resumo</button>
      </div>

      <div id="comparacao-view-hint-smart" class="smart-view-hint">
        Veja o melhor mercado único para sua lista nesta cidade.
      </div>

      <div id="comparacao-loading-smart">Carregando comparação...</div>
      <div id="comparacao-erro-smart"></div>
      <div id="comparacao-resultado-smart"></div>
    `;

    const appContent = document.getElementById("appContent");
      if (appContent) {
        appContent.appendChild(section);
      } else {
        document.body.appendChild(section);
      }
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

  function setActiveTab(tab) {
    currentComparacaoTab = tab;
    saveComparacaoState();

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

  function isSemDadosComparacao(data) {
    if (!data) return true;

    const total =
      Number(data.total_otimizado || 0) +
      Number(data.total_melhor_unidade || 0) +
      Number(data.melhor_total || 0);

    const itens = Array.isArray(data.itens) ? data.itens : [];
    const unidades = Array.isArray(data.unidades) ? data.unidades : [];

    return total === 0 && itens.length === 0 && unidades.length === 0;
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
      option.textContent = cidade.nome || `Cidade ${cidade.id}`;
      select.appendChild(option);
    });
  }

  async function buscarComparacaoCidade(listaId, cidadeId) {
    return await apiFetch(`/comparacao/cidade/${cidadeId}/lista/${listaId}`);
  }

  async function buscarComparacaoOtimizada(listaId, cidadeId) {
    return await apiFetch(`/comparacao/cidade/${cidadeId}/lista/${listaId}/otimizada`);
  }

  async function buscarComparacaoResumo(listaId, cidadeId) {
    return await apiFetch(`/resumo/cidade/${cidadeId}/lista/${listaId}`);
  }

  function renderComparacaoCidade(data) {
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

    const unidade = data.melhor_unidade_nome || "Nenhuma unidade encontrada";
    const rede = data.melhor_rede_nome || "Rede não informada";
    const total = Number(data.melhor_total || data.total_melhor_unidade || 0);
    const unidades = Array.isArray(data.unidades) ? data.unidades : [];
    const melhorId = data.melhor_unidade_id || null;

    const rankingOrdenado = [...unidades].sort((a, b) => Number(a.total || 0) - Number(b.total || 0));
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

  function renderComparacaoOtimizada(data) {
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

    const total = Number(data.total_otimizado || data.total || 0);
    const itens = Array.isArray(data.itens) ? data.itens : [];
    const mercados = new Set(
      itens.map(i => i.unidade_nome || i.mercado_nome || i.rede_nome).filter(Boolean)
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

  function renderComparacaoResumo(data) {
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

  async function onCompararCidade() {
    try {
      setErro("");
      setLoading(true);
      setActiveTab("cidade");
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
      setActiveTab("otimizada");
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
      setActiveTab("resumo");
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

  async function initComparacao() {
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

    const saved = loadComparacaoState();
    if (saved) {
      if (selectLista && saved.listaId) selectLista.value = saved.listaId;
      if (selectCidade && saved.cidadeId) selectCidade.value = saved.cidadeId;
      if (saved.tab) setActiveTab(saved.tab);
    } else {
      setActiveTab("cidade");
    }

    const autoRun = async () => {
      saveComparacaoState();

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

    if (selectLista?.value && selectCidade?.value) {
      try {
        await runActiveComparacao();
      } catch (e) {
        console.error("Erro ao restaurar comparacao:", e);
      }
    }
  }

  
/* SMART_SHOW_APPCONTENT_V1 */
function mostrarAppContent() {
  const appContent = document.getElementById("appContent");
  if (appContent) {
    appContent.classList.remove("hidden");
    appContent.style.display = "block";
    appContent.style.visibility = "visible";
    appContent.style.opacity = "1";
  }

  const userBox = document.getElementById("userBox");
  if (userBox) {
    userBox.classList.remove("hidden");
  }
}


function boot() {
  atualizarStatusSessao();
  mostrarAppContent();
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
