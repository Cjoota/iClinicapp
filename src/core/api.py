from fastapi import FastAPI
from fastapi.responses import FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import threading
import os
from pathlib import Path
servidor_iniciado = False
""" Gerando as pastas de armazenamento """
os.makedirs("pdf_temp",exist_ok=True)
os.makedirs("documentos_gerados",exist_ok=True)
os.makedirs("modelos_excel",exist_ok=True)

def iniciar_servidor_fastapi():
    """ Inicia o servidor de exames gerados """
    global servidor_iniciado
    if not servidor_iniciado:
        def rodar_servidor():
            subprocess.run(["uvicorn", "src.core.api:app", "--port", "8001", "--host", "0.0.0.0"]) 
        thread = threading.Thread(target=rodar_servidor, daemon=True)
        thread.start()
        servidor_iniciado = True



PDF_DIR = Path().resolve() / "pdf_temp"  # Aponta para a raiz do projeto

app = FastAPI()
app.mount("/files", StaticFiles(directory=PDF_DIR), name="files")

@app.get("/")
def read_root():
    return {"message": "Sem Permissão!"}

@app.get("/pdf/{filename}")
def get_pdf(filename: str):
    file_path = PDF_DIR / filename
    print("Requisição para:", filename)
    print("Buscando:", file_path)

    if file_path.exists():
        return FileResponse(str(file_path), media_type="application/pdf")
    else:
        return JSONResponse(
            status_code=404,
            content={
                "erro": "Arquivo não encontrado",
                "tentado_em": str(file_path),
                "existe": file_path.exists()
            }
        )
