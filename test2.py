import json
from pathlib import Path

caminho_json = Path("src/pages/goingPage/Jsons/ANAMNESE.json")

with open(caminho_json, "r", encoding="utf-8") as f:
    opcoes_anamnese = json.load(f)

print(opcoes_anamnese)
print(list(opcoes_anamnese.items()))