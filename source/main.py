import flet as ft
from api import iniciar_servidor_fastapi
from database.databasecache import inicializar_db,contabilidade_db
from routes import Router
from funcoes import Verificacoes
import logging
import atexit
#Habilida o sistema de log.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("CORE")
# Flag para identificar se as verificações iniciais aconteceram
initialize = False

class Main():
	"""SISTEMA PRINCIPAL\n - 
	- Função responsável pelo orquestramento do sistema e controle central do sistema.
	"""
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
		self.page.on_connect = self.page.go("/login")

	def Disconnect(self):
		""" Limpa os dados salvos durante a sessão do usuário ao sair do sistema. """
		self.page.session.clear()
		self.page.client_storage.clear()
		logger.info("Sessão Limpa")

	async def init_cache(self):
		""" Inicia o cache inteligente e preenche com as informações do DB """
		await contabilidade_db.buscar_dados(force_update=True)

	def VerificacoesIniciais(self):
		""" Inicializa todas os sistemas principais (BANCO DE DADOS, VERIFICAÇÕS DE CAIXA, E CACHE) """
		global initialize
		if not initialize:
			iniciar_servidor_fastapi()
			self.page.run_task(inicializar_db)
			self.page.run_task(self.verfy.uptable)
			self.page.run_task(self.verfy.verify)
			self.page.run_task(self.init_cache)
			initialize = True
			
@atexit.register
def limpar_cache():
	""" Limpa o cache do banco de dados e o que o sistema gerou. """
	print("Limpando Cache")
	verify = Verificacoes()
	verify.close()
	import shutil
	from pathlib import Path
	for d in Path(".").rglob("__pycache__"):
		shutil.rmtree(d)	
	for doc in Path("pdf_temp").glob("*.pdf"):
		doc.unlink()
	
ft.app(target=Main,view=ft.AppView.WEB_BROWSER, host="192.168.0.245",port=53712,assets_dir="assets")








                                     

