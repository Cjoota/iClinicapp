import flet as ft
from Interfaces.Login_interface import Login

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes = {
            "/": self.login_view,
            "/login": self.login_view,
            "/home": self.main_interface_view,
            "/contabilidade": self.contabilidade_view,
            "/documentos": self.documentos_view,
            "/empresas": self.empresas_view,
            "/gerardoc": self.gerardoc_view,
        }
        self.page.on_route_change = self.route_change
        self.page.go(self.page.route)
        self.page.on_connect = self.auth()

            

    def auth(self):
        if self.page.client_storage.contains_key("logado"):
            if self.page.client_storage.get("logado") == "sim":
                return
            else:
                self.page.go("/login")
        elif not self.page.client_storage.contains_key("logado"):
            self.go("/login")
                


    def route_change(self, route):
        self.page.views.clear()
        if route.route in self.routes:
            self.routes[route.route]()
        else:
            self.page.views.append(
                ft.View(
                    "/404",
                    [
                        ft.AppBar(title=ft.Text("iCLINICA"), bgcolor=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("404 - Página não encontrada"),
                    ]
                )
            )
        self.page.update()

    def main_interface_view(self):
        from Interfaces.main_interface import Main_interface
        if self.page.client_storage.get("logado") != "sim":
            self.page.go("/login")
            return
        main_view = Main_interface(self.page)
        self.page.views.append(
            ft.View(
                "/home",
                [
                    main_view.build_view()
                    
                ],scroll=ft.ScrollMode.ADAPTIVE
            )
        )

    def login_view(self):
        login_view = Login(self.page)
        self.page.views.append(
            ft.View(
                "/login",
                [
                    login_view.build_view()
                ]
            )
        )

    def contabilidade_view(self):
        from Interfaces.contab import ContabilidadePage
        if self.page.client_storage.get("logado") != "sim":
            self.page.go("/login")
            return
        if self.page.client_storage.get("perm") == "all":
            contab_view = ContabilidadePage(self.page)
            self.page.views.append(
                ft.View(
                    "/contabilidade",
                    [
                        contab_view.build_view()
                    ],scroll=ft.ScrollMode.ADAPTIVE
                )
            )
        else:
            self.page.views.append(
                ft.View(
                    "/contabilidade",
                    [
                        ft.Row([ft.Text("Sem Permissões para acessar!", scale=1.8)], alignment=ft.MainAxisAlignment.CENTER)
                    ]
                )
            )
    def documentos_view(self):
        from Interfaces.exames_prontos import Documentos
        if self.page.client_storage.get("logado") != "sim":
            self.page.go("/login")
            return
        documentos_view = Documentos(self.page)
        self.page.views.append(
            ft.View(
                "/documentos",
                [
                    documentos_view.build_view()
                ]
            )
        )
    def empresas_view(self):
        from Interfaces.empresas import Empresas
        if self.page.client_storage.get("logado") != "sim":
            self.page.go("/login")
            return
        Empresas_view = Empresas(self.page)
        self.page.views.append(
            ft.View(
                "/empresas",
                [
                    Empresas_view.build_view()
                ]
            )
        )
    def gerardoc_view(self):
        from Interfaces.gerarDoc import Gerardoc
        if self.page.client_storage.get("logado") != "sim":
            self.page.go("/login")
            return
        gerardoc_view = Gerardoc(self.page)
        self.page.views.append(
            ft.View(
                "/gerardoc",
                [
                    gerardoc_view.build_view()
                ]
            )
        )
    def go(self, route):
        self.page.go(route)