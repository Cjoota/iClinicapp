import flet as ft
from Interfaces.Login_interface import Login
from database.datacreator import dbcreator
from api import iniciar_servidor_fastapi
from database.databasecache import inicializar_db
from routes import Router
import atexit
class Main():
	def __init__(self,page: ft.Page) -> None:
		page.client_storage.remove("logado")
		iniciar_servidor_fastapi()
		page.padding=0
		page.window.maximized = True
		page.vertical_alignment = ft.MainAxisAlignment.CENTER
		page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
		page.bgcolor = ft.Colors.with_opacity(0.8, ft.Colors.GREY_100)
		page.scroll = ft.ScrollMode.AUTO
		page.title = "iCLINICA"
		page.adaptive= True
		page.theme_mode = ft.ThemeMode.LIGHT
		page.run_task(inicializar_db)
		dbcreator()
		self.router = Router(page)
		page.on_route_change = self.router.route_change
		page.go(page.route)

@atexit.register
def limpar_todos_pycache():
	print("Limpando Cache")
	import shutil
	from pathlib import Path
	for d in Path(".").rglob("__pycache__"):
		shutil.rmtree(d)
ft.app(target=Main,view=ft.AppView.WEB_BROWSER, host="192.168.0.245",port=53712)








                                     

