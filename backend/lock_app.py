from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

inserir = """
if (!token) {
  document.getElementById("authBox").classList.remove("hidden");
  document.getElementById("userBox").classList.add("hidden");
  topStatus.textContent = "Nao autenticado";
  setStatus("Nao autenticado");

  // BLOQUEAR RESTO DO APP
  document.querySelectorAll(".card").forEach(c => {
    if (!c.innerText.includes("Cadastrar") && !c.innerText.includes("Entrar")) {
      c.style.opacity = "0.4";
      c.style.pointerEvents = "none";
    }
  });

  return null;
}
"""

html = html.replace(
"if (!token) {",
inserir
)

file.write_text(html, encoding="utf-8")
print("OK: app bloqueado sem login")
