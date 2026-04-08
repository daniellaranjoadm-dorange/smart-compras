from pathlib import Path
import re

path = Path(r".\app\api\routes.py")
text = path.read_text(encoding="utf-8")

# remove linha com só vírgula
text = re.sub(r'^\s*,\s*$', '', text, flags=re.MULTILINE)

# remove vírgula antes de fechar parênteses
text = re.sub(r',\s*\)', ')', text)

# remove vírgula dupla
text = re.sub(r',\s*,', ',', text)

path.write_text(text, encoding="utf-8")
print("Limpeza de vírgulas concluída.")
