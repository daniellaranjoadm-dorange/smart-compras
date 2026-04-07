from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://gbmixonline.com.br/categorias/mercearia"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

print("Abrindo site...")
driver.get(url)

time.sleep(6)

print("Procurando elementos com números...")

elements = driver.find_elements(By.XPATH, "//*[contains(text(),'0') or contains(text(),'1') or contains(text(),'2')]")

print(f"Total elementos com números: {len(elements)}")

for el in elements[:40]:
    try:
        text = el.text.strip()
        if text:
            print("TEXTO:", text)
    except:
        pass

print("\nBuscando possíveis cards de produto...")

cards = driver.find_elements(By.XPATH, "//div")

print(f"Total divs: {len(cards)}")

for c in cards[:30]:
    try:
        txt = c.text.strip()
        if len(txt) > 30:
            print("\nCARD:")
            print(txt[:200])
    except:
        pass

driver.quit()
print("OK debug")
