import flet as ft
from api import iniciar_servidor_fastapi
from database.databasecache import inicializar_db
from routes import Router
import atexit
class Main():
	def __init__(self,page: ft.Page) -> None:
		self.page = page
		self.router = Router(page)
		iniciar_servidor_fastapi()
		page.bgcolor = ft.Colors.WHITE
		page.scroll = ft.ScrollMode.AUTO
		page.title = "Clinica São Lucas"
		page.adaptive= True
		page.theme_mode = ft.ThemeMode.LIGHT
		page.run_task(inicializar_db)
		page.on_route_change = self.router.route_change
		page.on_disconnect = self.disconnect()
		page.go("/login")
	def disconnect(self):
		self.page.client_storage.clear()
@atexit.register
def limpar_todos_pycache():
	print("Limpando Cache")
	import shutil
	from pathlib import Path
	for d in Path(".").rglob("__pycache__"):
		shutil.rmtree(d)	
ft.app(target=Main,view=ft.AppView.WEB_BROWSER, host="192.168.0.245",port=53712,assets_dir="assets")








                                     

