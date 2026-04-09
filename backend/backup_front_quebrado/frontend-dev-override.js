(function () {
  const API_BASE = "";
  const URL_PROMOCOES = API_BASE + "/api/monitoramento/promocoes";
  const URL_MUDANCAS = API_BASE + "/api/monitoramento/mudancas-preco";

  function formatMoney(v) {
    const n = Number(v || 0);
    return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  function formatPct(v) {
    const n = Number(v || 0);
    return `${n.toFixed(2)}%`;
  }

  function ensurePanel() {
    let panel = document.getElementById("painel-monitoramento-precos");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "painel-monitoramento-precos";
    panel.innerHTML = `
      <div class="scp-header">
        <div>
          <h3>Monitoramento de Preços</h3>
          <small>Promoções e mudanças recentes</small>
        </div>
        <button id="scp-recarregar-monitoramento" type="button">Atualizar</button>
      </div>

      <div class="scp-bloco">
        <h4>Promoções</h4>
        <div id="scp-promocoes-status">Carregando...</div>
        <div id="scp-promocoes-lista"></div>
      </div>

      <div class="scp-bloco">
        <h4>Últimas mudanças</h4>
        <div id="scp-mudancas-status">Carregando...</div>
        <div id="scp-mudancas-lista"></div>
      </div>
    `;

    const style = document.createElement("style");
    style.textContent = `
      #painel-monitoramento-precos {
        position: fixed;
        right: 16px;
        bottom: 16px;
        width: 420px;
        max-height: 80vh;
        overflow: auto;
        background: #ffffff;
        border: 1px solid #d7d7d7;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        z-index: 9999;
        padding: 14px;
        font-family: Arial, sans-serif;
      }
      #painel-monitoramento-precos .scp-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
      }
      #painel-monitoramento-precos .scp-header h3 {
        margin: 0 0 4px 0;
        font-size: 18px;
      }
      #painel-monitoramento-precos .scp-header small {
        color: #666;
      }
      #painel-monitoramento-precos .scp-header button {
        border: 0;
        border-radius: 8px;
        padding: 8px 12px;
        cursor: pointer;
      }
      #painel-monitoramento-precos .scp-bloco {
        margin-top: 14px;
      }
      #painel-monitoramento-precos .scp-bloco h4 {
        margin: 0 0 8px 0;
        font-size: 15px;
      }
      #painel-monitoramento-precos .scp-item {
        border: 1px solid #ececec;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 8px;
        background: #fafafa;
      }
      #painel-monitoramento-precos .scp-item .linha1 {
        font-weight: bold;
        margin-bottom: 4px;
      }
      #painel-monitoramento-precos .scp-item .linha2,
      #painel-monitoramento-precos .scp-item .linha3 {
        font-size: 13px;
        color: #444;
        margin-bottom: 3px;
      }
      #painel-monitoramento-precos .scp-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 12px;
        margin-right: 6px;
      }
      #painel-monitoramento-precos .scp-tag-promocao {
        background: #e8fff0;
      }
      #painel-monitoramento-precos .scp-tag-alta {
        background: #fff1f1;
      }
      #painel-monitoramento-precos .scp-tag-queda {
        background: #eef6ff;
      }
      #painel-monitoramento-precos .scp-vazio,
      #painel-monitoramento-precos .scp-erro {
        font-size: 13px;
        color: #666;
        padding: 8px 0;
      }
    `;
    document.head.appendChild(style);
    document.body.appendChild(panel);

    document
      .getElementById("scp-recarregar-monitoramento")
      .addEventListener("click", carregarMonitoramento);

    return panel;
  }

  function renderPromocoes(data) {
    const status = document.getElementById("scp-promocoes-status");
    const lista = document.getElementById("scp-promocoes-lista");

    if (!data || !Array.isArray(data.itens)) {
      status.textContent = "Resposta inválida.";
      lista.innerHTML = "";
      return;
    }

    status.textContent = `Total: ${data.total || 0}`;

    if (!data.itens.length) {
      lista.innerHTML = `<div class="scp-vazio">Nenhuma promoção detectada no momento.</div>`;
      return;
    }

    lista.innerHTML = data.itens.slice(0, 10).map(item => `
      <div class="scp-item">
        <div class="linha1">
          <span class="scp-tag scp-tag-promocao">Promoção</span>
          ${item.produto || "Produto"}
        </div>
        <div class="linha2">Unidade: ${item.unidade || "-"}</div>
        <div class="linha3">De ${formatMoney(item.preco_anterior)} para ${formatMoney(item.preco_atual)}</div>
        <div class="linha3">Queda: ${formatPct(item.queda_percentual)}</div>
      </div>
    `).join("");
  }

  function renderMudancas(data) {
    const status = document.getElementById("scp-mudancas-status");
    const lista = document.getElementById("scp-mudancas-lista");

    if (!data || !Array.isArray(data.itens)) {
      status.textContent = "Resposta inválida.";
      lista.innerHTML = "";
      return;
    }

    status.textContent = `Total: ${data.total || 0}`;

    if (!data.itens.length) {
      lista.innerHTML = `<div class="scp-vazio">Nenhuma mudança detectada no momento.</div>`;
      return;
    }

    lista.innerHTML = data.itens.slice(0, 10).map(item => `
      <div class="scp-item">
        <div class="linha1">
          <span class="scp-tag ${item.tipo === "alta" ? "scp-tag-alta" : "scp-tag-queda"}">${item.tipo || "mudança"}</span>
          ${item.produto || "Produto"}
        </div>
        <div class="linha2">Unidade: ${item.unidade || "-"}</div>
        <div class="linha3">De ${formatMoney(item.preco_anterior)} para ${formatMoney(item.preco_atual)}</div>
        <div class="linha3">Variação: ${formatPct(item.variacao_percentual)}</div>
      </div>
    `).join("");
  }

  async function carregarJson(url) {
    const resp = await fetch(url, { headers: { "Accept": "application/json" } });
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status} em ${url}`);
    }
    return await resp.json();
  }

  async function carregarMonitoramento() {
    ensurePanel();

    const statusPromocoes = document.getElementById("scp-promocoes-status");
    const statusMudancas = document.getElementById("scp-mudancas-status");
    const listaPromocoes = document.getElementById("scp-promocoes-lista");
    const listaMudancas = document.getElementById("scp-mudancas-lista");

    statusPromocoes.textContent = "Carregando...";
    statusMudancas.textContent = "Carregando...";
    listaPromocoes.innerHTML = "";
    listaMudancas.innerHTML = "";

    try {
      const [promocoes, mudancas] = await Promise.all([
        carregarJson(URL_PROMOCOES),
        carregarJson(URL_MUDANCAS)
      ]);

      renderPromocoes(promocoes);
      renderMudancas(mudancas);
    } catch (err) {
      console.error("Erro ao carregar monitoramento:", err);
      statusPromocoes.textContent = "Erro ao carregar.";
      statusMudancas.textContent = "Erro ao carregar.";
      listaPromocoes.innerHTML = `<div class="scp-erro">${String(err.message || err)}</div>`;
      listaMudancas.innerHTML = `<div class="scp-erro">${String(err.message || err)}</div>`;
    }
  }

  function init() {
    ensurePanel();
    carregarMonitoramento();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
