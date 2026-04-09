(function () {
  function findCardByTitle(text) {
    const cards = Array.from(document.querySelectorAll(".card"));
    return cards.find(card => {
      const h2 = card.querySelector("h2");
      const h3 = card.querySelector("h3");
      const title = (h2?.textContent || h3?.textContent || "").trim();
      return title === text;
    });
  }

  function applyLayout() {
    if (document.getElementById("sc-layout-grid")) return;

    const listasCard = findCardByTitle("Listas");
    const itensCard = document.getElementById("card-itens-lista");
    const selecionadaCard = Array.from(document.querySelectorAll(".card")).find(card => {
      const h3 = card.querySelector("#listaSelecionadaTitulo");
      return !!h3;
    });

    if (!listasCard || !itensCard || !selecionadaCard) {
      console.log("layout-enhancer: cards nao encontrados");
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      #sc-layout-grid {
        display: grid;
        grid-template-columns: 360px 1fr;
        gap: 20px;
        align-items: start;
        margin-top: 20px;
      }

      #sc-layout-left,
      #sc-layout-right {
        display: flex;
        flex-direction: column;
        gap: 20px;
      }

      #sc-layout-left .card,
      #sc-layout-right .card {
        margin: 0;
      }

      @media (max-width: 900px) {
        #sc-layout-grid {
          grid-template-columns: 1fr;
        }
      }
    `;
    document.head.appendChild(style);

    const grid = document.createElement("div");
    grid.id = "sc-layout-grid";

    const left = document.createElement("div");
    left.id = "sc-layout-left";

    const right = document.createElement("div");
    right.id = "sc-layout-right";

    listasCard.parentNode.insertBefore(grid, listasCard);
    grid.appendChild(left);
    grid.appendChild(right);

    left.appendChild(listasCard);
    right.appendChild(selecionadaCard);
    right.appendChild(itensCard);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyLayout);
  } else {
    applyLayout();
  }
})();
