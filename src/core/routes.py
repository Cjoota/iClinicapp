import flet as ft
import asyncio

from src.pages.LoginPage.interface import LoginPage
from src.pages.RegisterPage.interface import RegisterPage
from src.pages.AppointmentsPage.interface import AppointmentPage
from src.core.layout import MainLayout
from src.pages.HomePage.interface import HomePage
from src.pages.GeneratedExamsPage.interface import GeneratedExamsPage
from src.pages.AccountingPage.interface import AccountingPage
from src.pages.CompaniesPage.interface import CompaniesPage
from src.pages.CreateExamPage.interface import CreateExamPage
from src.pages.Billing.interface import Billings
class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.main_layout = None

        self.no_AuthRoutes = {
            "/": self.contentRouteBuilder(LoginPage, "/"),
            "/login": self.contentRouteBuilder(LoginPage, "/login"),
            "/cadastro": self.contentRouteBuilder(RegisterPage, "/cadastro"),
        }
        self.AuthRoutesRequired = {
            "/home": self.contentRouteBuilder(HomePage,"/home",True),
            "/contabilidade": self.contabilidade_content,
            "/exames_gerados": self.contentRouteBuilder(GeneratedExamsPage,"/exames_gerados",True),
            "/empresas": self.contentRouteBuilder(CompaniesPage,"/empresas",True),
            "/criar_exame": self.contentRouteBuilder(CreateExamPage,"/criar_exame",True),
            "/agendamento": self.contentRouteBuilder(AppointmentPage,"/agendamento",True),
            "/relacoes": self.contentRouteBuilder(Billings,"/relacoes",True),
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
                    if self.logged():
                        if self.main_layout is None or not self.page.views or self.page.views[-1].route != "main":
                            self.main_layout = MainLayout(self.page)
                            self.page.views.clear()
                            self.page.views.append(self.main_layout.get_view("main"))
                            self.page.update()
                            await asyncio.sleep(0.05)  
                        
                        content_builder = self.AuthRoutesRequired[route_called]
                        await self.main_layout.navigate_to(route_called, content_builder)
                        return
                    self.page.go("/login")
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
            content = await self.viewContentCaller(pageclass=pageclass, route=route,requireLogin=requireLogin)
            return content
        return handler


    def logged(self) -> bool:
        if not self.page.session.contains_key("logado"):
            return False
        if self.page.session.contains_key("logado"):
            if self.page.session.get("logado"):
                return True

    async def viewContentCaller(self, pageclass,requireLogin=False,route=None):
        instancePage = pageclass(self.page)
        if requireLogin:
            if self.logged():
                return instancePage.build_content()
            self.page.go("/login")
            return
        build = await instancePage.build_view()
        return ft.View(route, [build])

    # Métodos de conteúdo (retornam apenas o conteúdo, não a view completa)
    def main_interface_content(self):
        main_view = HomePage(self.page)
        return main_view.build_content()

    async def documentos_content(self):
        documentos_view = GeneratedExamsPage(self.page)
        controle = await documentos_view.build_content()
        return controle

    def contabilidade_content(self):
        contab_view = AccountingPage(self.page)
        if self.page.session.get("perm") == "all":
            return contab_view.build_content()
        else:
            return ft.Container(
                content=ft.Text("Sem Permissões para acessar!", scale=1.8),
                alignment=ft.alignment.center
            )

    async def empresas_content(self):
        empresas_view = CompaniesPage(self.page)
        controle = await empresas_view.build_content()
        return controle

    def gerardoc_content(self):
        gerardoc_view = CreateExamPage(self.page)
        controle = gerardoc_view.build_content()
        return controle

    def agendamentos_content(self):
        agendament_view = AppointmentPage(self.page)
        return agendament_view.build_content()

    async def login_view(self):
        login_view = LoginPage(self.page)
        controle = await login_view.build_view()
        return ft.View("/login", [controle])

    def cadastro_view(self):
        cadastro = RegisterPage(self.page)
        return ft.View("/cadastro", [cadastro.build_view()])