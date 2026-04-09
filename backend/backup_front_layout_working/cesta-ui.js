(function () {
  function formatMoney(value) {
    const n = Number(value || 0);
    return n.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  function escapeHtml(text) {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderListaItens(itens) {
    if (!itens || !itens.length) {
      return "<div class='muted'>Nenhum item encontrado.</div>";
    }

    return itens.map(function (item) {
      return 
        <div class="cesta-item-linha">
          <div>
            <div><strong></strong></div>
            <div></div>
            <div class="muted"> -  / </div>
          </div>
          <div><strong></strong></div>
        </div>
      ;
    }).join("");
  }

  function renderMercados(mercados) {
    if (!mercados || !mercados.length) {
      return "<div class='muted'>Nenhum mercado analisado.</div>";
    }

    return mercados.map(function (mercado, idx) {
      const badge = idx === 0 ? "<span class='cesta-badge'>melhor</span>" : "";
      const faltando = (mercado.faltando || []).length
        ? <div class="muted">Faltando: </div>
        : "<div class='muted'>Cobriu todos os itens</div>";

      return 
        <div class="cesta-mercado-card">
          <div class="cesta-mercado-topo">
            <div>
              <div><strong></strong> </div>
              <div class="muted"> / </div>
            </div>
            <div><strong></strong></div>
          </div>
          <div class="muted">Itens cobertos: </div>
          
        </div>
      ;
    }).join("");
  }

  async function calcularCesta() {
    const itensInput = document.getElementById("cestaItensInput");
    const categoriaSelect = document.getElementById("cestaCategoriaSelect");
    const resultado = document.getElementById("cestaResultado");

    if (!itensInput || !categoriaSelect || !resultado) {
      return;
    }

    const itens = (itensInput.value || "").trim();
    const categoria = categoriaSelect.value || "mercearia";

    if (!itens) {
      resultado.innerHTML = "<div class='erro'>Informe os itens separados por virgula. Ex: arroz, feijao, acucar</div>";
      return;
    }

    resultado.innerHTML = "<div class='muted'>Calculando cesta...</div>";

    try {
      const url = /api/catalogo/cesta?itens=&categoria=;
      const resp = await fetch(url);

      if (!resp.ok) {
        throw new Error("Falha ao consultar a cesta");
      }

      const data = await resp.json();

      const totalMelhor = formatMoney(data.total_cesta_melhor_por_item || 0);
      const economiaAbs = data.economia_absoluta == null ? "-" : formatMoney(data.economia_absoluta);
      const economiaPct = data.economia_percentual == null ? "-" : ${data.economia_percentual}%;

      const melhorMercado = data.melhor_mercado_cesta
        ? 
          <div class="cesta-resumo-card">
            <h3>Melhor mercado da cesta</h3>
            <div><strong></strong></div>
            <div class="muted"> / </div>
            <div>Total no mercado: <strong></strong></div>
            <div>Itens cobertos: <strong></strong></div>
          </div>
        
        : "<div class='cesta-resumo-card'><h3>Melhor mercado da cesta</h3><div class='muted'>Nenhum mercado suficiente encontrado.</div></div>";

      const naoEncontrados = (data.itens_nao_encontrados || []).length
        ? <div class="erro">Nao encontrados: </div>
        : "";

      resultado.innerHTML = 
        <div class="cesta-grid">
          <div class="cesta-resumo-card">
            <h3>Resumo</h3>
            <div>Total melhor por item: <strong></strong></div>
            <div>Itens encontrados: <strong></strong></div>
            <div>Itens nao encontrados: <strong></strong></div>
            <div>Economia absoluta: <strong></strong></div>
            <div>Economia percentual: <strong></strong></div>
          </div>
          
        </div>

        

        <div class="cesta-bloco">
          <h3>Itens da cesta</h3>
          
        </div>

        <div class="cesta-bloco">
          <h3>Mercados analisados</h3>
          
        </div>
      ;
    } catch (error) {
      resultado.innerHTML = <div class='erro'></div>;
    }
  }

  function bindCestaUI() {
    const btn = document.getElementById("calcularCestaBtn");
    const itensInput = document.getElementById("cestaItensInput");

    if (!btn || !itensInput) {
      return;
    }

    btn.addEventListener("click", calcularCesta);

    itensInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        calcularCesta();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindCestaUI);
  } else {
    bindCestaUI();
  }
})();
