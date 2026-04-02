from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

script = '''
<script>
window.SMART_AUTH = {
  TOKEN_KEY: "smartcompras_token",

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  saveToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
  },

  clearToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  },

  async apiFetch(url, options = {}) {
    const token = this.getToken();
    const headers = new Headers(options.headers || {});
    if (token) {
      headers.set("Authorization", "Bearer " + token);
    }
    return fetch(url, { ...options, headers });
  },

  requireAuth() {
    const token = this.getToken();
    if (!token) {
      alert("Voce precisa estar logado.");
      return false;
    }
    return true;
  },

  async loadCurrentUser() {
    const token = this.getToken();
    if (!token) return null;

    try {
      const response = await this.apiFetch("/api/auth/me");
      if (!response.ok) {
        this.clearToken();
        return null;
      }
      return await response.json();
    } catch (e) {
      return null;
    }
  },

  logout() {
    this.clearToken();
    location.reload();
  }
};
</script>
'''

if "window.SMART_AUTH" not in html:
    html = html.replace("</body>", script + "\n</body>")

file.write_text(html, encoding="utf-8")
print("OK: helpers de auth injetados no index.html")
