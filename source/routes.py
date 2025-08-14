import flet as ft
import asyncio

from Interfaces.Login_interface import Login
from Interfaces.cadastro import Cadastro
from Interfaces.agendamento import Agendamento
from Interfaces.layout import MainLayout
from Interfaces.main_interface import Main_interface
from Interfaces.exames_prontos import ExamesProntos
from Interfaces.contab import ContabilidadePage
from Interfaces.empresas import Empresas

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.main_layout = None

        self.no_AuthRoutes = {
            "/": self.contentRouteBuilder(Login, "/"),
            "/login": self.contentRouteBuilder(Login, "/login"),
            "/cadastro": self.contentRouteBuilder(Cadastro, "/cadastro"),
        }
        self.AuthRoutesRequired = {
            "/home": self.main_interface_content,
            "/contabilidade": self.require_login(self.contabilidade_content),
            "/documentos": self.documentos_content,
            "/empresas": self.empresas_content,
            "/gerardoc": self.require_login(self.gerardoc_content),
            "/agendamento": self.require_login(self.agendamentos_content),
        }

        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.on_connect = self.page.go("/")

    def require_login(self, content_func):
        def wrapper():
            if not self.page.session.get("logado"):
                self.page.go("/")
                return
            return content_func()
        return wrapper

    def route_change(self, route):
        async def trocar_view():
            try:
                route_called = route.route

                if route_called in self.no_AuthRoutes:
                    self.main_layout = None
                    view = await self.no_AuthRoutes[route_called]()
                    self.page.views.clear()
                    self.page.views.append(view)
                    self.page.update()
                    return

                if route_called in self.AuthRoutesRequired:
                    if self.main_layout is None or not self.page.views or self.page.views[-1].route != "main":
                        self.main_layout = MainLayout(self.page)
                        self.page.views.clear()
                        self.page.views.append(self.main_layout.get_view("main"))
                        self.page.update()
                        await asyncio.sleep(0.05)  
                    
                    content_builder = self.AuthRoutesRequired[route_called]
                    await self.main_layout.navigate_to(route_called, content_builder)
                    return

                view = ft.View("/404", [ft.Text("Página não encontrada")])
                self.page.views.clear()
                self.page.views.append(view)
                self.page.update()
            except Exception as e:
                print(f"Erro em trocar_view: {e}")
                import traceback
                traceback.print_exc()

        self.page.run_task(trocar_view)

    def view_pop(self, view):
        self.page.views.pop()
        if self.page.views:
            top_view = self.page.views[-1]
            self.page.go(top_view.route)


    def contentRouteBuilder(self, pageclass, route,requireLogin=False):
        async def handler():
            return await self.viewContentCaller(pageclass=pageclass, route=route,requireLogin=requireLogin)
        return handler


    async def viewContentCaller(self, pageclass,requireLogin=False,route=None):
        instancePage = pageclass(self.page)
        if requireLogin:
            return self.require_login(instancePage.build_content())
        build = await instancePage.build_view()
        return ft.View(route, [build])

    # Métodos de conteúdo (retornam apenas o conteúdo, não a view completa)
    async def main_interface_content(self):
        from Interfaces.main_interface import Main_interface
        main_view = Main_interface(self.page)
        return await main_view.build_content()

    async def documentos_content(self):
        from Interfaces.exames_prontos import ExamesProntos
        documentos_view = ExamesProntos(self.page)
        controle = await documentos_view.build_content()
        return controle

    def contabilidade_content(self):
        from Interfaces.contab import ContabilidadePage
        contab_view = ContabilidadePage(self.page)
        if self.page.session.get("perm") == "all":
            return contab_view.build_content()
        else:
            return ft.Container(
                content=ft.Text("Sem Permissões para acessar!", scale=1.8),
                alignment=ft.alignment.center
            )

    async def empresas_content(self):
        from Interfaces.empresas import Empresas
        empresas_view = Empresas(self.page)
        controle = await empresas_view.build_content()
        return controle

    def gerardoc_content(self):
        from Interfaces.gerarDoc import Gerardoc
        gerardoc_view = Gerardoc(self.page)
        controle = gerardoc_view.build_content()
        return controle

    def agendamentos_content(self):
        agendament_view = Agendamento(self.page)
        return agendament_view.build_content()

    async def login_view(self):
        login_view = Login(self.page)
        controle = await login_view.build_view()
        return ft.View("/login", [controle])

    def cadastro_view(self):
        cadastro = Cadastro(self.page)
        return ft.View("/cadastro", [cadastro.build_view()])