from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

barra = '''
<div id="smart-auth-bar" style="background:#111827;color:white;padding:12px 16px;border-radius:10px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
  <div id="smart-auth-status">Verificando sessao...</div>
  <button id="smart-auth-logout" style="width:auto;padding:8px 12px;border:none;border-radius:8px;background:#374151;color:white;cursor:pointer;">Sair</button>
</div>
'''

if 'id="smart-auth-bar"' not in html:
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + barra, 1)

script = '''
<script>
document.addEventListener("DOMContentLoaded", async function () {
  const statusEl = document.getElementById("smart-auth-status");
  const logoutBtn = document.getElementById("smart-auth-logout");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
      window.SMART_AUTH.logout();
    });
  }

  const user = await window.SMART_AUTH.loadCurrentUser();

  if (user) {
    statusEl.textContent = "Logado como " + user.nome + " (" + user.email + ")";
  } else {
    statusEl.textContent = "Nao autenticado";
  }
});
</script>
'''

if 'smart-auth-status' in html and 'Logado como ' not in html:
    html = html.replace("</body>", script + "\n</body>")

file.write_text(html, encoding="utf-8")
print("OK: barra de sessao adicionada")
