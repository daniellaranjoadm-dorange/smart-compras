(function () {
  function getCardByTitle(text) {
    const cards = Array.from(document.querySelectorAll(".card"));
    return cards.find(card => {
      const h2 = card.querySelector("h2");
      const h3 = card.querySelector("h3");
      const title = (h2?.textContent || h3?.textContent || "").trim();
      return title === text;
    });
  }

  function cleanupNoiseTextNodes(root = document.body) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const toClean = [];

    while (walker.nextNode()) {
      const node = walker.currentNode;
      const value = (node.nodeValue || "").trim();
      if (value === "`r`n" || value === "'r`n" || value === "r`n" || value === "`n" || value === "`r") {
        toClean.push(node);
      }
    }

    toClean.forEach(n => n.nodeValue = "");
  }

  function injectStyles() {
    if (document.getElementById("ui-max-patch-style")) return;

    const style = document.createElement("style");
    style.id = "ui-max-patch-style";
    style.textContent = `
      :root {
        --bg: #f3f4f6;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --line: #e5e7eb;
        --primary: #0f172a;
        --primary-2: #1e293b;
        --danger: #991b1b;
        --selected: #dbeafe;
        --shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
      }

      body {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%) !important;
        color: var(--text) !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
        padding: 24px !important;
        font-family: Arial, sans-serif !important;
      }

      h1 {
        font-size: 42px !important;
        margin-bottom: 8px !important;
      }

      .card {
        background: var(--card) !important;
        border: 1px solid var(--line) !important;
        border-radius: 18px !important;
        padding: 20px !important;
        box-shadow: var(--shadow) !important;
        margin-bottom: 18px !important;
      }

      input, select {
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
      }

      button {
        border-radius: 10px !important;
        font-weight: 700 !important;
      }

      #sc-shell-auth {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 18px;
        align-items: start;
      }

      #sc-shell-app {
        display: grid;
        grid-template-columns: 360px 1fr;
        gap: 22px;
        align-items: start;
        margin-top: 8px;
      }

      #sc-shell-left,
      #sc-shell-right {
        display: flex;
        flex-direction: column;
        gap: 18px;
      }

      #sc-shell-left .card,
      #sc-shell-right .card {
        margin: 0 !important;
      }

      #listasContainer > div {
        transition: all 0.18s ease;
      }

      #listasContainer > div:hover {
        transform: translateY(-1px);
      }

      #itensListaContainer > div {
        border-radius: 12px;
        background: #fafafa;
        padding: 12px !important;
        margin-bottom: 8px;
        border: 1px solid #edf0f3;
      }

      #listaSelecionadaTitulo {
        font-size: 22px !important;
        margin: 0 !important;
      }

      #card-itens-lista h2,
      #sc-card-listas h2 {
        font-size: 30px !important;
        margin-bottom: 12px !important;
      }

      .sc-section-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 8px;
      }

      .sc-hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #fff;
        border-radius: 22px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
      }

      .sc-hero h1 {
        color: #fff !important;
        margin: 0 0 6px 0 !important;
      }

      .sc-hero p {
        margin: 0 !important;
        color: #cbd5e1 !important;
        font-size: 15px;
      }

      @media (max-width: 980px) {
        #sc-shell-auth,
        #sc-shell-app {
          grid-template-columns: 1fr;
        }

        body {
          padding: 16px !important;
        }

        h1 {
          font-size: 34px !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function buildHero() {
    if (document.getElementById("sc-hero")) return;

    const h1 = document.querySelector("h1");
    const subtitle = document.querySelector("body > p");

    if (!h1) return;

    const hero = document.createElement("div");
    hero.id = "sc-hero";
    hero.className = "sc-hero";
    hero.innerHTML = `
      <h1>${h1.textContent.trim()}</h1>
      <p>Sistema inteligente de listas, itens e monitoramento de preços</p>
    `;

    h1.parentNode.insertBefore(hero, h1);
    h1.remove();
    if (subtitle) subtitle.remove();
  }

  function hideNoiseCards() {
    const teste = getCardByTitle("Teste autenticado");
    if (teste) teste.style.display = "none";

    const app = getCardByTitle("App de Compras");
    if (app) app.style.display = "none";
  }

  function buildLayout() {
    if (document.getElementById("sc-shell-app")) return;

    const statusCard = getCardByTitle("Status");
    const userCard = getCardByTitle("Usuario logado");
    const listasCard = getCardByTitle("Listas");
    const itensCard = document.getElementById("card-itens-lista");
    const selecionadaCard = Array.from(document.querySelectorAll(".card")).find(card => {
      return !!card.querySelector("#listaSelecionadaTitulo");
    });

    if (!statusCard || !userCard || !listasCard || !itensCard || !selecionadaCard) {
      console.log("ui-max-patch: cards principais nao encontrados");
      return;
    }

    listasCard.id = "sc-card-listas";

    const authShell = document.createElement("div");
    authShell.id = "sc-shell-auth";

    statusCard.parentNode.insertBefore(authShell, statusCard);
    authShell.appendChild(statusCard);
    authShell.appendChild(userCard);

    const appShell = document.createElement("div");
    appShell.id = "sc-shell-app";

    const left = document.createElement("div");
    left.id = "sc-shell-left";

    const right = document.createElement("div");
    right.id = "sc-shell-right";

    listasCard.parentNode.insertBefore(appShell, listasCard);
    appShell.appendChild(left);
    appShell.appendChild(right);

    left.appendChild(listasCard);
    right.appendChild(selecionadaCard);
    right.appendChild(itensCard);
  }

  function run() {
    cleanupNoiseTextNodes();
    injectStyles();
    buildHero();
    hideNoiseCards();
    buildLayout();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setTimeout(run, 800);
})();
