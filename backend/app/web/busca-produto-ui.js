(function () {
  let debounceBuscaProduto;

  function formatMoney(v) {
    const n = Number(v || 0);
    return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  function ensureBuscaUI() {
    const input = document.getElementById("itemProdutoId");
    if (!input) return null;

    input.placeholder = "🔍 Buscar produto por nome...";
    input.autocomplete = "off";

    let box = document.getElementById("sugestoesProdutos");
    if (!box) {
      box = document.createElement("div");
      box.id = "sugestoesProdutos";
      box.style.marginTop = "8px";
      box.style.marginBottom = "8px";
      input.insertAdjacentElement("afterend", box);
    }

    return { input, box };
  }

  async function buscarSugestoes(termo) {
    const resp = await fetch(`/api/produtos/busca-com-precos?termo=${encodeURIComponent(termo)}`, {
      headers: { "Accept": "application/json" }
    });

    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }

    return await resp.json();
  }

  function renderSugestoes(produtos) {
    const box = document.getElementById("sugestoesProdutos");
    const input = document.getElementById("itemProdutoId");
    if (!box || !input) return;

    if (!produtos || !produtos.length) {
      box.innerHTML = `
        <div style="
          padding:10px;
          border:1px solid #e5e7eb;
          border-radius:10px;
          background:#fff;
          color:#64748b;
        ">
          Nenhum produto encontrado
        </div>
      `;
      return;
    }

    box.innerHTML = produtos.map(p => `
      <div
        data-id="${p.id}"
        data-nome="${String(p.nome).replace(/"/g, '&quot;')}"
        style="
          padding:10px 12px;
          border:1px solid #e5e7eb;
          border-radius:10px;
          background:#fff;
          margin-bottom:6px;
          cursor:pointer;
        "
      >
        <div style="font-weight:700; color:#0f172a;">${p.nome}</div>
        <div style="font-size:12px; color:#475569; margin-top:4px;">
          ${p.preco != null ? formatMoney(p.preco) : "Sem preço"}${p.mercado ? " • " + p.mercado : ""}
        </div>
      </div>
    `).join("");

    Array.from(box.children).forEach(el => {
      el.addEventListener("click", function () {
        input.dataset.produtoId = this.dataset.id;
        input.value = this.dataset.nome;
        box.innerHTML = "";
      });
    });
  }

  function hookAdicionarItem() {
    if (!window.adicionarItemNaLista || window.__buscaProdutoHooked) return;

    const original = window.adicionarItemNaLista;

    window.adicionarItemNaLista = async function () {
      const input = document.getElementById("itemProdutoId");

      if (input && input.dataset.produtoId) {
        input.value = input.dataset.produtoId;
      }

      try {
        await original();
      } finally {
        if (input) {
          input.value = "";
          input.dataset.produtoId = "";
        }
        const box = document.getElementById("sugestoesProdutos");
        if (box) box.innerHTML = "";
      }
    };

    window.__buscaProdutoHooked = true;
  }

  function initBuscaProduto() {
    const ui = ensureBuscaUI();
    if (!ui) return;

    hookAdicionarItem();

    ui.input.addEventListener("input", function () {
      const termo = this.value.trim();

      if (this.dataset.produtoId) {
        this.dataset.produtoId = "";
      }

      clearTimeout(debounceBuscaProduto);

      if (termo.length < 2) {
        ui.box.innerHTML = "";
        return;
      }

      debounceBuscaProduto = setTimeout(async () => {
        try {
          const produtos = await buscarSugestoes(termo);
          renderSugestoes(produtos);
        } catch (e) {
          ui.box.innerHTML = `
            <div style="
              padding:10px;
              border:1px solid #fecaca;
              border-radius:10px;
              background:#fff1f2;
              color:#991b1b;
            ">
              Erro ao buscar produtos
            </div>
          `;
        }
      }, 250);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBuscaProduto);
  } else {
    initBuscaProduto();
  }

  setTimeout(initBuscaProduto, 900);
})();
