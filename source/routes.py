import flet as ft
from Interfaces.Login_interface import Login
from Interfaces.cadastro import Cadastro

class Router:
    """SISTEMA DE ROTAS E ENDEREÇAMENTO DE ABAS.\n-
    - route_change:\n 
        Gerenciamento de rotas chamado atráves do evento de troca de pagina.\n
        
    - require_login:\n
        Verificação do login, verifica se o usuário ja se logou e se está permitido o acesso.\n
        
    - <Nome da aba>_view:\n
        Geração das paginas.\n
    
    - Go:\n
        Função de troca unica de paginas.

    """
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes = {
            "/": self.login_view,
            "/login": self.login_view,
            "/home": self.require_login(self.main_interface_view),
            "/contabilidade": self.require_login(self.contabilidade_view),
            "/documentos": self.require_login(self.documentos_view),
            "/empresas": self.require_login(self.empresas_view),
            "/gerardoc": self.require_login(self.gerardoc_view),
            "/cadastro": self.cadastro_view,
        }
        self.page.on_route_change = self.route_change
        self.page.on_connect = self.page.go("/")

    def require_login(self, view_func):
        """ Verifica se o usuario está logado. """
        def wrapper():
            if not self.page.session.get("logado"):
                self.page.go("/login")
                return
            view_func()
        return wrapper
    
    def route_change(self, route):
        """ Função de troca de paginas, recebe o chamado do capturador de evento ao trocar de pagina. """
        self.page.views.clear()
        rota = route.route
        rotas_protegidas = ["/home", "/contabilidade", "/documentos", "/empresas", "/gerardoc"]
        if rota in rotas_protegidas and not self.page.session.get("logado"):
            self.page.go("/login")
            return

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
        contab_view = ContabilidadePage(self.page)
        if self.page.session.get("perm") == "all":
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
        gerardoc_view = Gerardoc(self.page)
        self.page.views.append(
            ft.View(
                "/gerardoc",
                [
                    gerardoc_view.build_view()
                ]
            )
        )
    
    def cadastro_view(self):
        cadastro = Cadastro(self.page)
        self.page.views.append(
            ft.View(
                "/cadastro",
                [
                    cadastro.build_view()
                ] 
            )
        )
    
    def go(self, route):
        self.page.go(route)