from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import threading
import os
servidor_iniciado = False
os.makedirs("pdf_temp",exist_ok=True)
os.makedirs("documentos_gerados",exist_ok=True)
os.makedirs("documentos_gerados/doc_info",exist_ok=True)
os.makedirs("modelos_excel",exist_ok=True)
def iniciar_servidor_fastapi():
    global servidor_iniciado
    if not servidor_iniciado:
        def rodar_servidor():
            subprocess.run(["uvicorn", "source.api:app", "--port", "8001", "--host", "0.0.0.0"]) 
        thread = threading.Thread(target=rodar_servidor, daemon=True)
        thread.start()
        servidor_iniciado = True
app = FastAPI()
app.mount("/files", StaticFiles(directory=rf"pdf_temp"), name="files")
@app.get("/")
def read_root():
    return {"message": "Servidor FastAPI rodando!"}
@app.get("/pdf/{filename}")
def get_pdf(filename: str):
    """Endpoint para servir arquivos PDF"""
    file_path = rf"pdf_temp\{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf")
    else:
        return {"error": "Arquivo não encontrado"}
