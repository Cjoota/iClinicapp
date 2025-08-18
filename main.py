import flet as ft
import logging
import atexit
import os
import shutil
from pathlib import Path

from src.functions.funcs import excluir_agendamentos_vencidos,Verificacoes
from src.core.api import iniciar_servidor_fastapi
from src.database.databasecache import inicializar_db,contabilidade_db
from src.core.routes import Router

# Flag para identificar se as verificações iniciais aconteceram
initialize = False
log = logging.Logger("MAIN")

class Main():
	"""SISTEMA PRINCIPAL\n - 
	- Função responsável pelo orquestramento do sistema e controle central do sistema.
	"""
	def __init__(self, page: ft.Page) -> None:
		self.page = page
		self.page.title = "Clinica São Lucas"
		self.page.bgcolor = ft.Colors.WHITE
		self.page.theme_mode = ft.ThemeMode.LIGHT
		self.router = Router(page)
		self.verfy = Verificacoes()
		self.VerificacoesIniciais()
		self.page.on_route_change = self.router.route_change
		self.page.on_connect = self.refresh
	
	def refresh(self,e):
		sncbar=ft.SnackBar(content=ft.Text("Sessão Expirada",color=ft.Colors.BLACK),bgcolor=ft.Colors.YELLOW)
		if self.page.session.get_keys() == []:
			self.page.go("/")
			return
		self.page.session.clear()
		self.page.go("/login")
		self.page.open(sncbar)

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
			excluir_agendamentos_vencidos()
			initialize = True
			
@atexit.register
def limpar_cache():
	""" Limpa o cache do banco de dados e o que o sistema gerou. """
	absolute = Path(os.getcwd())
	for dirpath, dirnames, _ in os.walk(absolute):
		if '__pycache__' in dirnames:
			pycache_path = os.path.join(dirpath, '__pycache__')
			shutil.rmtree(pycache_path)
	for doc in Path("pdf_temp").glob("*.pdf"):
		doc.unlink()
	locals().clear()
	log.info("CACHE LIMPO")

ft.app(target=Main,view=ft.AppView.WEB_BROWSER, host="192.168.3.59",port=53712,assets_dir=f"{Path("assets").absolute()}")








                                     

