from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

guard = '''
<script>
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form").forEach(function(form) {
    form.addEventListener("submit", function(e) {
      if (!window.SMART_AUTH.requireAuth()) {
        const hasLogin = form.querySelector('input[type="password"]') && form.querySelector('input[type="email"]');
        const title = form.closest("div") ? form.closest("div").innerText : "";
        if (title.includes("Entrar") || title.includes("Login") || title.includes("Cadastrar")) {
          return;
        }
        e.preventDefault();
      }
    });
  });
});
</script>
'''

if "document.querySelectorAll(\"form\")" not in html:
    html = html.replace("</body>", guard + "\n</body>")

file.write_text(html, encoding="utf-8")
print("OK: guard de autenticacao aplicado")
