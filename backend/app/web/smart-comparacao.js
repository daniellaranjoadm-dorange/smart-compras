let listaSelecionadaId = null;
let listasCache = [];

function getEl(id) {
  return document.getElementById(id);
}

function atualizarTituloLista(nome, id) {
  const titulo = getEl("listaSelecionadaTitulo");
  if (!titulo) return;

  if (!nome || !id) {
    titulo.textContent = "Nenhuma lista selecionada";
    return;
  }

  titulo.textContent = `Lista selecionada: ${nome} (ID ${id})`;
}

function renderListas() {
  const container = getEl("listasContainer");
  if (!container) return;

  if (!Array.isArray(listasCache) || !listasCache.length) {
    container.innerHTML = '<div class="muted">Nenhuma lista criada</div>';
    atualizarTituloLista(null, null);
    return;
  }

  const atual = listasCache.find(x => Number(x.id) === Number(listaSelecionadaId)) || listasCache[0];
  listaSelecionadaId = Number(atual.id);
  atualizarTituloLista(atual.nome, atual.id);

  container.innerHTML = listasCache.map(l => `
    <div style="
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:10px;
      padding:10px 12px;
      margin-bottom:8px;
      border-radius:10px;
      border:1px solid #e5e7eb;
      ${Number(listaSelecionadaId) === Number(l.id) ? 'background:#dbeafe;' : 'background:#ffffff;'}
    ">
      <div onclick="selecionarLista(${l.id})" style="flex:1; cursor:pointer;">
        <div style="font-weight:700; color:#111827;">${l.nome}</div>
        <div style="font-size:12px; color:#6b7280;">ID: ${l.id}</div>
      </div>

      <div style="display:flex; gap:8px;">
        <button type="button" onclick="editarLista(${l.id}, ${JSON.stringify(l.nome)})" style="
          width:auto;
          padding:8px 10px;
          border-radius:8px;
          background:#0f172a;
          color:#fff;
          border:none;
          cursor:pointer;
        ">Editar</button>

        <button type="button" onclick="excluirLista(${l.id})" style="
          width:auto;
          padding:8px 10px;
          border-radius:8px;
          background:#7f1d1d;
          color:#fff;
          border:none;
          cursor:pointer;
        ">Excluir</button>
      </div>
    </div>
  `).join("");
}

async function carregarListas() {
  const container = getEl("listasContainer");
  if (!container) return;

  container.innerHTML = '<div class="muted">Carregando listas...</div>';

  try {
    const resp = await apiFetch("/api/listas");
    const data = await resp.json();

    if (!resp.ok) {
      container.innerHTML = '<div class="erro">Erro ao carregar listas</div>';
      return;
    }

    listasCache = Array.isArray(data) ? data : [];

    if (!listaSelecionadaId && listasCache.length) {
      listaSelecionadaId = Number(listasCache[0].id);
    }

    renderListas();
    await carregarItensDaLista();
  } catch (err) {
    container.innerHTML = `<div class="erro">Erro ao carregar listas: ${err}</div>`;
  }
}

function selecionarLista(id) {
  carregarResumoLista(id);
  listaSelecionadaId = Number(id);
  renderListas();
carregarItensDaLista();
carregarComparacaoLista(listaSelecionadaId);
}

async function criarLista() {
  const input = getEl("novaListaNome");
  if (!input) return;

  const nome = String(input.value || "").trim();
  if (!nome) {
    alert("Digite um nome");
    return;
  }

  try {
    const resp = await apiFetch("/api/listas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome })
    });

    const raw = await resp.text();

    if (!resp.ok) {
      alert("Erro ao criar lista: " + raw);
      return;
    }

    let data = null;
    try { data = raw ? JSON.parse(raw) : null; } catch (_) {}

    input.value = "";
    await carregarListas();

    if (data && data.id) {
      selecionarLista(Number(data.id));
    }
  } catch (err) {
    alert("Erro ao criar lista: " + err);
  }
}

async function editarLista(id, nomeAtual) {
  const novoNome = prompt("Novo nome da lista:", nomeAtual);
  if (!novoNome) return;

  try {
    const resp = await apiFetch(`/api/listas/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome: String(novoNome).trim() })
    });

    const raw = await resp.text();

    if (!resp.ok) {
      alert("Erro ao editar lista: " + raw);
      return;
    }

    await carregarListas();
    selecionarLista(id);
  } catch (e) {
    alert("Erro ao editar lista: " + e);
  }
}

async function excluirLista(id) {
  const confirmar = confirm("Excluir essa lista?");
  if (!confirmar) return;

  try {
    const resp = await apiFetch(`/api/listas/${id}`, {
      method: "DELETE"
    });

    const raw = await resp.text();

    if (!resp.ok) {
      alert("Erro ao excluir lista: " + raw);
      return;
    }

    if (Number(listaSelecionadaId) === Number(id)) {
      listaSelecionadaId = null;
    }

    await carregarListas();
  } catch (e) {
    alert("Erro ao excluir lista: " + e);
  }
}

async function carregarItensDaLista() {
  const status = getEl("itensListaStatus");
  const container = getEl("itensListaContainer");

  if (!status || !container) return;

  if (!listaSelecionadaId) {
    status.textContent = "Selecione uma lista";
    container.innerHTML = "Nenhum item carregado.";
    return;
  }

  status.textContent = "Carregando itens...";

  try {
    const resp = await apiFetch("/api/itens");
    const data = await resp.json();

    if (!resp.ok) {
      status.textContent = "Erro ao carregar itens";
      container.innerHTML = "";
      return;
    }

    const itens = (Array.isArray(data) ? data : []).filter(i => Number(i.lista_id) === Number(listaSelecionadaId));

// buscar produtos
const respProd = await apiFetch("/api/produtos");
const produtos = await respProd.json();
const mapProdutos = {};
(produtos || []).forEach(p => mapProdutos[p.id] = p.nome);

status.textContent = `Total de itens: ${itens.length}`;
await carregarComparacao();
carregarResumoLista(listaSelecionadaId);

if (!itens.length) {
  container.innerHTML = "Essa lista ainda não tem itens.";
  return;
}

container.innerHTML = itens.map(item => `
  <div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:12px;
    margin-bottom:8px;
    border-radius:10px;
    border:1px solid #e5e7eb;
    background:#ffffff;
  ">
    <div>
      <div style="font-weight:700; font-size:15px;">
        ${mapProdutos[item.produto_id] || 'Produto'}
      </div>
      <div style="font-size:13px; color:#64748b;">
        Quantidade: ${item.quantidade}
      </div>
    </div>

    <button onclick="removerItem(${item.id})" style="
      background:#dc2626;
      color:#fff;
      border:none;
      padding:8px 12px;
      border-radius:8px;
      cursor:pointer;
    ">
      Remover
    </button>
  </div>
`).join("");
  } catch (err) {
    status.textContent = "Erro ao carregar itens";
    container.innerHTML = String(err);
  }
}

async function adicionarItemNaLista() {
  if (!listaSelecionadaId) {
    alert("Selecione uma lista primeiro.");
    return;
  }

  const produtoId = Number(getEl("itemProdutoId")?.value);
  const quantidade = Number(getEl("itemQuantidade")?.value || 1);

  if (!produtoId || produtoId <= 0) {
    alert("Informe um produto_id válido.");
    return;
  }

  if (!quantidade || quantidade <= 0) {
    alert("Informe uma quantidade válida.");
    return;
  }

  try {
    const resp = await apiFetch("/api/itens", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lista_id: listaSelecionadaId,
        produto_id: produtoId,
        quantidade: quantidade
      })
    });

    const raw = await resp.text();

    if (!resp.ok) {
      alert("Erro ao adicionar item: " + raw);
      return;
    }

    getEl("itemProdutoId").value = "";
    getEl("itemQuantidade").value = "1";
    await carregarItensDaLista();
  } catch (err) {
    alert("Erro ao adicionar item: " + err);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  setTimeout(() => {
    const token = localStorage.getItem("smartcompras_token");
    if (token) {
      carregarListas();
    }
  }, 500);
});

async function removerItem(id) {
  if (!confirm("Remover item?")) return;

  try {
    const resp = await apiFetch(`/api/itens/${id}`, {
      method: "DELETE"
    });

    if (!resp.ok) {
      const txt = await resp.text();
      alert("Erro ao remover: " + txt);
      return;
    }

    await carregarItensDaLista();
  } catch (e) {
    alert("Erro ao remover: " + e);
  }
}

async function carregarResumoLista(listaId) {
  try {
    const resp = await apiFetch(`/api/listas/${listaId}/resumo`);
    if (!resp.ok) {
      console.log("erro resumo status", resp.status);
      return;
    }

    const data = await resp.json();

    const el = document.getElementById("resumoLista");
    if (!el) return;

    el.innerHTML = `
  <div style="
    display:grid;
    grid-template-columns: repeat(4, 1fr);
    gap:12px;
    margin-bottom:16px;
  ">

    <div style="padding:14px; background:#f8fafc; border-radius:12px; border:1px solid #e2e8f0;">
      <div style="font-size:12px; color:#64748b;">Itens</div>
      <div style="font-size:22px; font-weight:800;">${data.total_itens}</div>
    </div>

    <div style="padding:14px; background:#f8fafc; border-radius:12px; border:1px solid #e2e8f0;">
      <div style="font-size:12px; color:#64748b;">Quantidade</div>
      <div style="font-size:22px; font-weight:800;">${data.total_quantidade}</div>
    </div>

    <div style="padding:14px; background:#ecfdf5; border-radius:12px; border:1px solid #bbf7d0;">
      <div style="font-size:12px; color:#166534;">Custo estimado</div>
      <div style="font-size:24px; font-weight:900; color:#166534;">
        R$ ${Number(data.custo_estimado || 0).toFixed(2)}
      </div>
    </div>

    <div style="padding:14px; background:#fef2f2; border-radius:12px; border:1px solid #fecaca;">
      <div style="font-size:12px; color:#991b1b;">Status</div>
      <div style="font-size:20px; font-weight:800; color:#991b1b;">
        ${(() => {
  if (data.custo_estimado > 300) return "Muito caro";
  if (data.custo_estimado > 200) return "Caro";
  if (data.custo_estimado > 100) return "Médio";
  return "Econômico";
})()}
      </div>
    </div>

  </div>

  <div style="
    padding:14px;
    border-radius:12px;
    background:#f1f5f9;
    border:1px solid #e2e8f0;
    font-size:14px;
  ">
    💡 Dica: monitore variações de preço para economizar mais.
  </div>
`;
  } catch (e) {
    console.log("erro ao carregar resumo", e);
  }
}




async function carregarComparacao() {
  if (!listaSelecionadaId) return;

  try {
    const cidadeId = 1; // ajustar depois dinamico

    const resp = await apiFetch(`/api/comparacao/cidade/${cidadeId}/lista/${listaSelecionadaId}/otimizada`);
    const data = await resp.json();

    renderComparacao(data);
  } catch (e) {
    scDebug("erro comparacao: " + e);
  }
}

function renderComparacao(data) {
  const el = document.getElementById("comparacaoBox");
  if (!el) return;

  if (!data || !data.melhor_opcao) {
    el.innerHTML = "Sem comparação disponível";
    return;
  }

  const melhor = data.melhor_opcao;

  el.innerHTML = `
    <div style="
      border:1px solid #bbf7d0;
      background:#ecfdf5;
      padding:12px;
      border-radius:10px;
    ">
      <div style="font-weight:700; margin-bottom:4px;">
        🏆 Melhor opção
      </div>

      <div style="font-size:14px;">
        ${melhor.mercado}
      </div>

      <div style="margin-top:6px; font-weight:600;">
        Total: R$ ${melhor.total.toFixed(2)}
      </div>

      <div style="color:#16a34a; font-size:13px;">
        Economia: R$ ${melhor.economia.toFixed(2)}
      </div>
    </div>
  `;
}


let debounceBusca;

document.addEventListener("input", async (e) => {
  if (e.target.id !== "produtoBusca") return;

  const termo = e.target.value;
  clearTimeout(debounceBusca);

  if (!termo || termo.length < 2) {
    document.getElementById("sugestoesProdutos").innerHTML = "";
    return;
  }

  debounceBusca = setTimeout(async () => {
    try {
      const resp = await apiFetch(`/api/produtos?search=${encodeURIComponent(termo)}`);
      const produtos = await resp.json();

      const box = document.getElementById("sugestoesProdutos");

      if (!produtos || !produtos.length) {
  box.innerHTML = "<div style='padding:8px; color:#666;'>Nenhum produto encontrado</div>";
  return;
}

box.innerHTML = produtos.slice(0, 5).map(p => `
  <div onclick="selecionarProduto(${p.id}, '${p.nome.replace(/'/g, "")}')"
    style="
      padding:10px;
      border:1px solid #eee;
      cursor:pointer;
      background:#fff;
      border-radius:6px;
      margin-bottom:4px;
    ">
    <div style="font-weight:600;">${p.nome}</div>
  </div>
`).join("");
    } catch (e) {
      console.error(e);
    }
  }, 300);
});

function selecionarProduto(id, nome) {
  document.getElementById("produtoId").value = id;
  document.getElementById("produtoBusca").value = nome;
  document.getElementById("sugestoesProdutos").innerHTML = "";
}


async function carregarComparacaoLista(listaId) {
  if (!listaId) return;

  const cidadeId = 1;
  const box = document.getElementById("comparacaoListaBox");
  if (!box) return;

  box.innerHTML = `
    <div style="
      padding:14px;
      border:1px solid #e5e7eb;
      border-radius:12px;
      background:#fff;
      margin-bottom:16px;
    ">
      Carregando comparação...
    </div>
  `;

  try {
    const resp = await apiFetch(`/api/comparacao/cidade/${cidadeId}/lista/${listaId}/otimizada`);
    if (!resp.ok) {
      box.innerHTML = `
        <div style="
          padding:14px;
          border:1px solid #fecaca;
          border-radius:12px;
          background:#fff1f2;
          color:#991b1b;
          margin-bottom:16px;
        ">
          Não foi possível carregar a comparação da lista.
        </div>
      `;
      return;
    }

    const data = await resp.json();
    renderComparacaoLista(data);
  } catch (e) {
    box.innerHTML = `
      <div style="
        padding:14px;
        border:1px solid #fecaca;
        border-radius:12px;
        background:#fff1f2;
        color:#991b1b;
        margin-bottom:16px;
      ">
        Erro ao carregar comparação.
      </div>
    `;
    console.log("erro comparacao lista", e);
  }
}

function moeda(v) {
  const n = Number(v || 0);
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function pct(v) {
  const n = Number(v || 0);
  return n.toFixed(2) + "%";
}

function renderComparacaoLista(data) {
  const box = document.getElementById("comparacaoListaBox");
  if (!box) return;

  const unidades = Array.isArray(data.unidades) ? data.unidades : [];
  const itens = Array.isArray(data.itens) ? data.itens : [];

  if (!unidades.length) {
    box.innerHTML = `
      <div style="
        padding:14px;
        border:1px solid #e5e7eb;
        border-radius:12px;
        background:#fff;
        margin-bottom:16px;
      ">
        Ainda não há comparação suficiente para essa lista.
      </div>
    `;
    return;
  }

  const ranking = [...unidades].sort((a, b) => Number(a.total || 0) - Number(b.total || 0));
  const melhor = ranking[0];
  const pior = ranking[ranking.length - 1];

  const economia = Number((pior.total || 0) - (melhor.total || 0));
  const economiaPct = pior.total ? (economia / Number(pior.total)) * 100 : 0;

  const maxTotal = Math.max(...ranking.map(x => Number(x.total || 0)), 1);

  box.innerHTML = `
    <div style="
      border:1px solid #dbeafe;
      background:#f8fbff;
      border-radius:16px;
      padding:16px;
      margin-bottom:16px;
    ">
      <div style="font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#64748b; font-weight:700;">
        Comparação inteligente
      </div>

      <div style="display:grid; grid-template-columns: 1.3fr 1fr 1fr; gap:12px; margin-top:12px;">
        <div style="padding:14px; background:#ecfdf5; border:1px solid #bbf7d0; border-radius:12px;">
          <div style="font-size:12px; color:#166534;">Melhor mercado</div>
          <div style="font-size:20px; font-weight:900; color:#166534; margin-top:4px;">${melhor.nome}</div>
          <div style="font-size:14px; margin-top:6px;">Total: ${moeda(melhor.total)}</div>
        </div>

        <div style="padding:14px; background:#fff; border:1px solid #e5e7eb; border-radius:12px;">
          <div style="font-size:12px; color:#64748b;">Economia</div>
          <div style="font-size:22px; font-weight:900; color:#2563eb; margin-top:4px;">${moeda(economia)}</div>
          <div style="font-size:13px; color:#64748b; margin-top:4px;">${pct(economiaPct)} vs mais caro</div>
        </div>

        <div style="padding:14px; background:#fff; border:1px solid #e5e7eb; border-radius:12px;">
          <div style="font-size:12px; color:#64748b;">Mercados comparados</div>
          <div style="font-size:22px; font-weight:900; margin-top:4px;">${ranking.length}</div>
          <div style="font-size:13px; color:#64748b; margin-top:4px;">Ranking por total da lista</div>
        </div>
      </div>
    </div>

    <div style="
      border:1px solid #e5e7eb;
      background:#fff;
      border-radius:16px;
      padding:16px;
      margin-bottom:16px;
    ">
      <div style="font-size:18px; font-weight:800; margin-bottom:12px;">Ranking de mercados</div>
      ${ranking.map((u, idx) => `
        <div style="margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <div style="font-weight:700;">#${idx + 1} ${u.nome}</div>
            <div style="font-weight:700;">${moeda(u.total)}</div>
          </div>
          <div style="height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden;">
            <div style="
              width:${Math.max(8, (Number(u.total || 0) / maxTotal) * 100)}%;
              height:100%;
              background:${idx === 0 ? '#16a34a' : '#0f172a'};
              border-radius:999px;
            "></div>
          </div>
        </div>
      `).join("")}
    </div>

    <div style="
      border:1px solid #e5e7eb;
      background:#fff;
      border-radius:16px;
      padding:16px;
      margin-bottom:16px;
    ">
      <div style="font-size:18px; font-weight:800; margin-bottom:12px;">Melhor mercado por item</div>
      <div style="display:flex; flex-direction:column; gap:10px;">
        ${itens.map(item => `
          <div style="
            display:grid;
            grid-template-columns: 1.5fr 1fr 1fr;
            gap:12px;
            padding:12px;
            border:1px solid #eef2f7;
            border-radius:12px;
            background:#fafcff;
          ">
            <div>
              <div style="font-weight:700;">${item.produto_nome || "Produto"}</div>
              <div style="font-size:12px; color:#64748b;">Quantidade: ${item.quantidade || 1}</div>
            </div>
            <div>
              <div style="font-size:12px; color:#64748b;">Melhor mercado</div>
              <div style="font-weight:700;">${item.melhor_unidade_nome || "-"}</div>
            </div>
            <div>
              <div style="font-size:12px; color:#64748b;">Melhor preço</div>
              <div style="font-weight:800; color:#166534;">${moeda(item.melhor_preco || 0)}</div>
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}
