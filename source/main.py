import flet as ft
from api import iniciar_servidor_fastapi
from database.databasecache import inicializar_db
from routes import Router
from funcoes import Verificacoes
import logging
import atexit
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("CORE")
initialize = False
class Main():
	def __init__(self, page: ft.Page) -> None:
		self.page = page
		self.router = Router(page)
		self.verfy = Verificacoes()
		self.VerificacoesIniciais()
		self.page.bgcolor = ft.Colors.WHITE
		self.page.title = "Clinica São Lucas"
		self.page.theme_mode = ft.ThemeMode.LIGHT
		self.page.on_route_change = self.router.route_change
		self.page.on_disconnect = lambda _: self.Disconnect()
		self.page.go("/login")

	def Disconnect(self):
		self.page.session.clear()
		logger.info("Sessão Limpa")

	def VerificacoesIniciais(self):
		global initialize
		if not initialize:
			iniciar_servidor_fastapi()
			self.page.run_task(inicializar_db)
			self.page.run_task(self.verfy.uptable)
			self.page.run_task(self.verfy.verify)
			initialize = True
			
@atexit.register
def limpar_todos_pycache():
	print("Limpando Cache")
	verify = Verificacoes()
	verify.close()
	import shutil
	from pathlib import Path
	for d in Path(".").rglob("__pycache__"):
		shutil.rmtree(d)	
	for doc in Path("pdf_temp").glob("*.pdf"):
		doc.unlink()
	
ft.app(target=Main,view=ft.AppView.WEB_BROWSER, host="192.168.0.245",port=53712,assets_dir="assets",)








                                     

