import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://gbmixonline.com.br/categorias/mercearia"
print("Abrindo:", url)
driver.get(url)

time.sleep(10)

# salvar evidências
Path("tmp_gbmix_debug").mkdir(exist_ok=True)
Path("tmp_gbmix_debug/gbmix_source.html").write_text(driver.page_source, encoding="utf-8", errors="ignore")
driver.save_screenshot("tmp_gbmix_debug/gbmix_screen.png")
print("OK: page_source e screenshot salvos em tmp_gbmix_debug")

# logs de rede
logs = driver.get_log("performance")

urls = []
for entry in logs:
    try:
        msg = json.loads(entry["message"])["message"]
        method = msg.get("method", "")
        params = msg.get("params", {})
        if method == "Network.requestWillBeSent":
            req = params.get("request", {})
            req_url = req.get("url", "")
            if any(x in req_url.lower() for x in ["api", "graphql", "products", "produto", "search", "catalog", "category", "categorias"]):
                urls.append(req_url)
    except Exception:
        pass

# deduplicar preservando ordem
seen = set()
final_urls = []
for u in urls:
    if u not in seen:
        seen.add(u)
        final_urls.append(u)

print("\n===== POSSIVEIS ENDPOINTS =====")
for u in final_urls[:80]:
    print(u)

print("\n===== TEXTOS VISIVEIS IMPORTANTES =====")
elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'solicitação') or contains(text(), 'Internet') or contains(text(), 'Mercearia')]")
for el in elements[:20]:
    try:
        txt = el.text.strip()
        if txt:
            print(txt)
    except:
        pass

driver.quit()
print("\nOK: debug de rede finalizado")
