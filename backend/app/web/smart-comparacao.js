let listaSelecionadaId = null;
let listasCache = [];
let scJaInicializado = false;
let scCarregandoListas = false;

function scDebug(msg) {
  if (typeof debugLog === "function") {
    debugLog(msg);
  } else {
    console.log(msg);
  }
}

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
    container.innerHTML = "Nenhuma lista criada";
    atualizarTituloLista(null, null);
    return;
  }

  const atual = listasCache.find(x => Number(x.id) === Number(listaSelecionadaId)) || listasCache[0];
  listaSelecionadaId = Number(atual.id);
  atualizarTituloLista(atual.nome, atual.id);

  container.innerHTML = listasCache.map(l => `
    <div
      data-lista-id="${l.id}"
      onclick="selecionarLista(${l.id})"
      style="
        padding:8px;
        border-bottom:1px solid #eee;
        cursor:pointer;
        ${Number(listaSelecionadaId) === Number(l.id) ? 'background:#eef;' : ''}
      "
    >
      <b>${l.nome}</b> (ID: ${l.id})
    </div>
  `).join("");
}

async function carregarListas() {
  const container = getEl("listasContainer");
  if (!container) {
    scDebug("listasContainer nao encontrado");
    return;
  }

  if (scCarregandoListas) {
    scDebug("carregarListas ignorado: ja em execucao");
    return;
  }

  scCarregandoListas = true;
  container.innerHTML = "Carregando listas...";
  scDebug("carregarListas iniciado");

  try {
    const resp = await apiFetch("/api/listas");
    scDebug("GET /api/listas status=" + resp.status);

    const raw = await resp.text();
    scDebug("GET /api/listas body=" + raw);

    let data = [];
    try {
      data = raw ? JSON.parse(raw) : [];
    } catch (e) {
      container.innerHTML = "Resposta invalida ao carregar listas.";
      scDebug("falha parse listas");
      return;
    }

    if (!resp.ok) {
      container.innerHTML = "Erro ao carregar listas.";
      return;
    }

    listasCache = Array.isArray(data) ? data : [];

    if (!listaSelecionadaId && listasCache.length) {
      listaSelecionadaId = Number(listasCache[0].id);
    }

    renderListas();
    await carregarItensDaLista();
    sincronizarListaComparacao();

    scDebug("listas renderizadas: " + listasCache.length);
  } catch (err) {
    container.innerHTML = "Erro ao carregar listas.";
    scDebug("catch carregarListas=" + (err && err.message ? err.message : String(err)));
  } finally {
    scCarregandoListas = false;
  }
}

function selecionarLista(id) {
  const lista = listasCache.find(x => Number(x.id) === Number(id));
  if (!lista) {
    scDebug("selecionarLista: lista nao encontrada id=" + id);
    return;
  }

  listaSelecionadaId = Number(id);
  scDebug("lista selecionada id=" + id);

  renderListas();
  carregarItensDaLista();
  sincronizarListaComparacao();
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
    scDebug("POST /api/listas status=" + resp.status);
    scDebug("POST /api/listas body=" + raw);

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
  scDebug("carregarItensDaLista lista_id=" + listaSelecionadaId);

  try {
    const resp = await apiFetch("/api/itens");
    scDebug("GET /api/itens status=" + resp.status);

    const raw = await resp.text();
    scDebug("GET /api/itens body=" + raw);

    let data = [];
    try {
      data = raw ? JSON.parse(raw) : [];
    } catch (e) {
      status.textContent = "Resposta invalida ao carregar itens";
      container.innerHTML = "";
      return;
    }

    if (!resp.ok) {
      status.textContent = "Erro ao carregar itens";
      container.innerHTML = "";
      return;
    }

    const itens = (Array.isArray(data) ? data : []).filter(i => Number(i.lista_id) === Number(listaSelecionadaId));
    status.textContent = `Total de itens: ${itens.length}`;

    if (!itens.length) {
      container.innerHTML = "Essa lista ainda não tem itens.";
      return;
    }

    container.innerHTML = itens.map(item => `
      <div style="padding:8px; border-bottom:1px solid #eee;">
        <b>Produto ID:</b> ${item.produto_id}
        <span style="margin-left:12px;"><b>Qtd:</b> ${item.quantidade}</span>
        <span style="margin-left:12px; color:#666;"><b>Item ID:</b> ${item.id}</span>
      </div>
    `).join("");
  } catch (err) {
    status.textContent = "Erro ao carregar itens";
    container.innerHTML = String(err);
    scDebug("catch carregarItensDaLista=" + (err && err.message ? err.message : String(err)));
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
    scDebug("POST /api/itens status=" + resp.status);
    scDebug("POST /api/itens body=" + raw);

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

function sincronizarListaComparacao() {
  const select = getEl("listaSelect");
  if (!select || !listaSelecionadaId) return;

  const existe = Array.from(select.options).some(o => Number(o.value) === Number(listaSelecionadaId));
  if (existe) {
    select.value = String(listaSelecionadaId);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  if (scJaInicializado) {
    scDebug("init ignorado: frontend ja inicializado");
    return;
  }

  scJaInicializado = true;
  scDebug("smart-comparacao.js carregado");

  setTimeout(() => {
    const token = localStorage.getItem("smartcompras_token");
    scDebug("token presente=" + (!!token));

    if (token) {
      carregarListas();
    }
  }, 700);
});
