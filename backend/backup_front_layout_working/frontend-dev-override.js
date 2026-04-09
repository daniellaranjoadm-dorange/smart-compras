(function () {
  let tentativas = 0;

  function txt(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function showById(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove("hidden");
    el.style.display = "";
    el.style.visibility = "visible";
    el.style.opacity = "1";
  }

  function hideById(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add("hidden");
    el.style.display = "none";
  }

  async function forcarModoDev() {
    tentativas += 1;
    console.log("forcarModoDev tentativa", tentativas);

    hideById("authBox");
    hideById("userBox");
    showById("appContent");

    txt("topStatusMsg", "Modo desenvolvimento");
    txt("statusMsg", "Sistema pronto");

    const statusEls = document.querySelectorAll("*");
    statusEls.forEach(function (el) {
      if (el && typeof el.textContent === "string") {
        if (el.textContent.includes("Verificando sessao") || el.textContent.includes("Carregando sessao")) {
          el.textContent = el.textContent
            .replaceAll("Verificando sessao...", "Modo desenvolvimento")
            .replaceAll("Verificando sessao..", "Modo desenvolvimento")
            .replaceAll("Verificando sessao", "Modo desenvolvimento")
            .replaceAll("Carregando sessao...", "Modo desenvolvimento")
            .replaceAll("Carregando sessao..", "Modo desenvolvimento")
            .replaceAll("Carregando sessao", "Modo desenvolvimento")
            .replaceAll("Carregando...", "Sistema pronto");
        }
      }
    });

    if (typeof carregarListas === "function") {
      try { await carregarListas(); } catch (e) { console.error("carregarListas", e); }
    }

    if (typeof carregarItens === "function") {
      try { await carregarItens(); } catch (e) { console.error("carregarItens", e); }
    }

    if (typeof carregarProdutos === "function") {
      try { await carregarProdutos(); } catch (e) { console.error("carregarProdutos", e); }
    }

    const btn = document.getElementById("carregarListasBtn");
    if (btn && tentativas < 6) {
      setTimeout(forcarModoDev, 700);
    }
  }

  window.addEventListener("load", function () {
    setTimeout(forcarModoDev, 100);
    setTimeout(forcarModoDev, 600);
    setTimeout(forcarModoDev, 1400);
    setTimeout(forcarModoDev, 2500);
  });
})();
