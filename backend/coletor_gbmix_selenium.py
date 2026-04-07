from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://gbmixonline.com.br/categorias/mercearia"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

print("Abrindo site...")
driver.get(url)

time.sleep(5)

print("Coletando produtos...")

produtos = driver.find_elements(By.XPATH, "//*[contains(text(), 'R$')]")

print(f"Encontrados possíveis preços: {len(produtos)}")

for p in produtos[:20]:
    try:
        texto = p.text.strip()
        if "R$" in texto:
            print("PREÇO:", texto)
    except:
        pass

driver.quit()

print("OK: coleta finalizada")
