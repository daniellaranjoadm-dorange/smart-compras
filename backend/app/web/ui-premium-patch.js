(function () {
  function injectStyle() {
    if (document.getElementById("ui-premium-style")) return;

    const style = document.createElement("style");
    style.id = "ui-premium-style";
    style.textContent = `
      :root{
        --bg:#eef2f7;
        --surface:#ffffff;
        --surface-2:#f8fafc;
        --text:#0f172a;
        --muted:#64748b;
        --line:#e2e8f0;
        --primary:#0f172a;
        --primary-2:#1e293b;
        --accent:#2563eb;
        --danger:#991b1b;
        --danger-2:#b91c1c;
        --success:#15803d;
        --shadow:0 12px 32px rgba(15,23,42,.08);
        --radius:18px;
      }

      body{
        background:
          radial-gradient(circle at top left, #f8fafc 0%, #eef2f7 45%, #e9eef5 100%) !important;
        color:var(--text) !important;
        max-width:1320px !important;
        padding:24px !important;
      }

      .sc-hero{
        border-radius:24px !important;
        padding:26px 30px !important;
        box-shadow:0 22px 50px rgba(15,23,42,.22) !important;
      }

      .sc-hero h1{
        font-size:48px !important;
        letter-spacing:-0.03em !important;
      }

      .sc-hero p{
        font-size:15px !important;
        color:#cbd5e1 !important;
      }

      .card{
        background:rgba(255,255,255,.94) !important;
        backdrop-filter: blur(8px);
        border:1px solid rgba(226,232,240,.95) !important;
        border-radius:var(--radius) !important;
        padding:22px !important;
        box-shadow:var(--shadow) !important;
      }

      #sc-shell-auth{
        display:grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap:18px !important;
        margin-bottom:22px !important;
      }

      #sc-shell-app{
        display:grid !important;
        grid-template-columns: 340px 1fr !important;
        gap:24px !important;
        align-items:start !important;
      }

      #sc-shell-left,
      #sc-shell-right{
        display:flex !important;
        flex-direction:column !important;
        gap:20px !important;
      }

      #sc-shell-left .card,
      #sc-shell-right .card{
        margin:0 !important;
      }

      #sc-card-listas{
        position:sticky;
        top:20px;
      }

      #sc-card-listas h2,
      #card-itens-lista h2{
        margin:0 0 16px 0 !important;
        font-size:20px !important;
        font-weight:800 !important;
        letter-spacing:-0.02em !important;
      }

      #listaSelecionadaTitulo{
        font-size:22px !important;
        margin:0 !important;
        letter-spacing:-0.02em !important;
      }

      input, select{
        width:100% !important;
        border:1px solid #cbd5e1 !important;
        border-radius:12px !important;
        padding:12px 14px !important;
        background:#fff !important;
        transition:all .18s ease !important;
      }

      input:focus, select:focus{
        outline:none !important;
        border-color:#60a5fa !important;
        box-shadow:0 0 0 4px rgba(96,165,250,.18) !important;
      }

      button{
        border:none !important;
        border-radius:12px !important;
        font-weight:800 !important;
        letter-spacing:-0.01em !important;
        transition:all .18s ease !important;
      }

      button:hover{
        transform:translateY(-1px);
        filter:brightness(1.02);
      }

      #userBox button,
      #card-itens-lista > button,
      #sc-card-listas > button{
        background:linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%) !important;
        color:#fff !important;
      }

      #listasContainer > div{
        border:1px solid var(--line) !important;
        border-radius:14px !important;
        padding:12px 12px !important;
        margin-bottom:10px !important;
        background:#fff !important;
        box-shadow:0 2px 8px rgba(15,23,42,.03);
      }

      #listasContainer > div:hover{
        transform:translateY(-1px);
        box-shadow:0 10px 18px rgba(15,23,42,.06);
      }

      #listasContainer button{
        padding:7px 10px !important;
        font-size:12px !important;
        border-radius:10px !important;
        min-width:68px !important;
      }

      #listasContainer button:first-of-type{
        background:#0f172a !important;
        color:#fff !important;
      }

      #listasContainer button:last-of-type{
        background:linear-gradient(135deg, #991b1b 0%, #b91c1c 100%) !important;
        color:#fff !important;
      }

      #itensListaStatus{
        font-size:13px !important;
        color:var(--muted) !important;
        margin-bottom:10px !important;
      }

      #itensListaContainer{
        margin-top:14px !important;
      }

      #itensListaContainer > div{
        display:flex !important;
        justify-content:space-between !important;
        align-items:center !important;
        gap:14px !important;
        padding:14px !important;
        margin-bottom:10px !important;
        border:1px solid var(--line) !important;
        border-radius:14px !important;
        background:linear-gradient(180deg, #fff 0%, #fafcff 100%) !important;
      }

      #itensListaContainer button{
        background:linear-gradient(135deg, #991b1b 0%, #b91c1c 100%) !important;
        color:#fff !important;
        min-width:120px !important;
        padding:10px 14px !important;
      }

      #statusMsg.ok{
        color:var(--success) !important;
        font-weight:800 !important;
      }

      #statusMsg.erro{
        color:#b91c1c !important;
        font-weight:800 !important;
      }

      .muted{
        color:var(--muted) !important;
      }

      /* compacta cards técnicos */
      #sc-shell-auth .card{
        min-height: 118px !important;
      }

      #userBox{
        display:flex !important;
        flex-direction:column !important;
        justify-content:space-between !important;
      }

      #userInfo{
        line-height:1.45 !important;
      }

      /* embeleza título da lista selecionada */
      #listaSelecionadaTitulo::before{
        content:"Lista ativa";
        display:block;
        font-size:12px;
        text-transform:uppercase;
        letter-spacing:.08em;
        color:var(--muted);
        margin-bottom:6px;
        font-weight:700;
      }

      /* reduz aparência vazia */
      #card-itens-lista{
        min-height:420px;
      }

      @media (max-width: 980px){
        body{
          padding:14px !important;
        }

        .sc-hero h1{
          font-size:38px !important;
        }

        #sc-shell-auth,
        #sc-shell-app{
          grid-template-columns:1fr !important;
        }

        #sc-card-listas{
          position:static !important;
        }

        #itensListaContainer > div{
          flex-direction:column !important;
          align-items:flex-start !important;
        }

        #itensListaContainer button{
          width:100% !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function improveTexts() {
    const itensTitle = document.querySelector("#card-itens-lista h2");
    if (itensTitle) itensTitle.textContent = "Itens da lista";

    const listasTitle = document.querySelector("#sc-card-listas h2");
    if (listasTitle) listasTitle.textContent = "Listas";

    const status = document.getElementById("statusMsg");
    if (status && status.textContent.includes("Autenticado")) {
      status.classList.add("ok");
    }
  }

  function cleanupNoise() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) {
      const n = walker.currentNode;
      const v = (n.nodeValue || "").trim();
      if (v === "`r`n" || v === "'r`n" || v === "r`n" || v === "`n" || v === "`r") {
        nodes.push(n);
      }
    }
    nodes.forEach(n => n.nodeValue = "");
  }

  function run() {
    cleanupNoise();
    injectStyle();
    improveTexts();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setTimeout(run, 700);
})();
