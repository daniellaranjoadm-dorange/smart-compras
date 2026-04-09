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
  listaSelecionadaId = Number(id);
  renderListas();
  carregarItensDaLista();
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
renderResumoLista(itens);

if (!itens.length) {
  container.innerHTML = "Essa lista ainda não tem itens.";
  return;
}

container.innerHTML = itens.map(item => `
  <div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:10px;
    border-bottom:1px solid #eee;
  ">
    <div>
      <div style="font-weight:600;">
        ${mapProdutos[item.produto_id] || 'Produto #' + item.produto_id}
      </div>
      <div style="font-size:12px; color:#666;">
        Qtd: ${item.quantidade} | ID: ${item.id}
      </div>
    </div>

    <button onclick="removerItem(${item.id})" style="
      background:#7f1d1d;
      color:#fff;
      border:none;
      padding:6px 10px;
      border-radius:6px;
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

function renderResumoLista(itens) {
  const container = document.getElementById("resumoLista");
  if (!container) return;

  const totalItens = itens.length;
  const totalQtd = itens.reduce((acc, i) => acc + Number(i.quantidade || 0), 0);

  container.innerHTML = `
    <div style="
      display:grid;
      grid-template-columns: repeat(3, 1fr);
      gap:12px;
      margin-bottom:16px;
    ">
      <div style="padding:12px; background:#f8fafc; border-radius:10px;">
        <div style="font-size:12px; color:#64748b;">Itens</div>
        <div style="font-size:20px; font-weight:800;">${totalItens}</div>
      </div>

      <div style="padding:12px; background:#f8fafc; border-radius:10px;">
        <div style="font-size:12px; color:#64748b;">Quantidade total</div>
        <div style="font-size:20px; font-weight:800;">${totalQtd}</div>
      </div>

      <div style="padding:12px; background:#f8fafc; border-radius:10px;">
        <div style="font-size:12px; color:#64748b;">Custo estimado</div>
        <div style="font-size:20px; font-weight:800;">--</div>
      </div>
    </div>
  `;
}
