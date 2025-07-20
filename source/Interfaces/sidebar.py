import asyncio
import flet as ft
import datetime as dt
from Interfaces.telaresize import Responsive
from Interfaces.Login_interface import Login
from funcoes import Verificacoes,get_cargo,get_apelido
import gender_guesser.detector as gender
class Sidebar:
    def __init__(self, page: ft.Page):
        self.page = page
        self.resize = Responsive(self.page)
        self.login = Login(page)
        self.vr = Verificacoes()
        self.page.on_window_event = self.fechar_app
        self.item_selecionado = self.page.route
        self.avatar = None
        self.usuario = str(self.page.session.get("user"))
        self.genero = gender.Detector()
    async def fechar_app(self, e):
        if e.data == "close":
            print("Janela foi fechada.")
            self.parar_evento.set()
            self.relogio_task.cancel()
            try:
                await self.relogio_task
            except asyncio.CancelledError:
                pass
            self.page.window_destroy()
    def logout(self):
        def sair(e):
            if self.page.session.contains_key("perm"):
                self.page.session.remove("perm")
            self.page.session.remove("logado")
            self.page.session.remove("user")
            self.page.client_storage.remove("nick")
            self.page.go("/login")
        alert = ft.AlertDialog(
            modal=True,
            title="Logout",
            content=ft.Text("Deseja mesmo sair?"),
            actions=[
                ft.TextButton(text="Sim",on_click=lambda e: sair(e),style=ft.ButtonStyle(color='#26BD00')),
                ft.TextButton(text="Não",on_click=lambda _: self.page.close(alert),style=ft.ButtonStyle(color='#26BD00'))
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
            
        )
        self.page.open(alert)
        alert.open = True
    def menu_item(self, icon, rota):
        cor = '#26BD00' if self.item_selecionado == rota else ft.Colors.GREY_600
        bg = ft.Colors.with_opacity(0.2, ft.Colors.LIGHT_GREEN_ACCENT_100) if self.item_selecionado == rota else ft.Colors.WHITE
        return ft.Container(
            content=ft.Row([ft.Icon(icon, color=cor)]),
            padding=5,
            on_click=lambda _: self.page.go(rota),
            margin=ft.Margin(bottom=0,top=0, right=0, left=0),
            ink=True,
            bgcolor=bg,
            border_radius=10
        )   
    def build(self):
        self.sidebar_items = [
            ft.Container(
                content=ft.Row([ft.Image(src="logo.png",height=60,width=60),],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                margin=ft.margin.only(top=5)
            ),
            
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.HOME_OUTLINED, color=ft.Colors.GREY_600), ft.Text("Home")]),
                padding=7,
                on_click=lambda _: self.page.go("/home"),
                margin=ft.Margin(bottom=0, top=10, right=0, left=0),
                ink=True,

            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.GREY_600), ft.Text("Contabilidade")]),
                padding=7,
                on_click=lambda _: self.page.go("/contabilidade"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
            ),
            ft.Container(
                content=ft.Row([ft.Text("Empresarial", weight=ft.FontWeight.BOLD, size=16)],alignment=ft.MainAxisAlignment.START),
                padding=0,
                margin=ft.Margin(bottom=0, top=10, left=5, right=0),
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.BUSINESS, color=ft.Colors.GREY_600), ft.Text("Empresas")]),
                padding=4,
                on_click=lambda _: self.page.go("/empresas"), # Assuming an empresas route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.CREATE_ROUNDED, color=ft.Colors.GREY_600), ft.Text("Gerar exames")]),
                padding=4,
                on_click=lambda _: self.page.go("/gerardoc"), # Assuming a gerardoc route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.GREY_600), ft.Text("Exames gerados")]),
                padding=4,
                on_click=lambda _: self.page.go("/documentos"), # Assuming a documentos route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
            ),
            
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.FILE_UPLOAD, color=ft.Colors.GREY_600), ft.Text("Exames prontos")]),
                padding=4,
                on_click=lambda _: print("Converter Arquivo clicked"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                disabled=True
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.GREY_600), ft.Text("Agendamento")]),
                padding=4,
                on_click=lambda _: print("Agendamento clicked"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                disabled=True
            ),
            
        ]
        
        self.sidebar_items_mobile = [
            ft.Container(
                content=ft.Image(src=r"logo.png",width=35,height=35),
                padding=5,
                bgcolor=ft.Colors.WHITE,
            ),
            self.menu_item(ft.Icons.HOME_OUTLINED,"/home"),
            self.menu_item(ft.Icons.PERSON,"/login"),
            self.menu_item(ft.Icons.MONETIZATION_ON,"/contabilidade"),
            self.menu_item(ft.Icons.BUSINESS,"/empresas"),
            self.menu_item(ft.Icons.CREATE_ROUNDED,"/gerardoc"),
            self.menu_item(ft.Icons.DESCRIPTION,"/documentos"),
            
        ]
        if not self.resize.is_shd():
            self.avatar = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([ft.Divider(thickness=1, color=ft.Colors.with_opacity(0.4, ft.Colors.GREY_400))],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        width=200,
                        margin=ft.Margin(left=0,top=0,right=0,bottom=-10)
                    ),
                    ft.Row([
                        ft.CircleAvatar(foreground_image_src="mano.png" if self.genero.get_gender(get_apelido(self.usuario)) == "male" else "female.png",radius=25,bgcolor="#83ff58"),
                        ft.Text(f"{str(get_apelido(self.usuario)).capitalize()}",color=ft.Colors.BLACK,weight=ft.FontWeight.BOLD,size=16)
                    ],spacing=15),
                    ft.Container(
                        content=ft.Column([ft.Text(f"{str(get_cargo(self.usuario)).capitalize()}",size=12,color='#26BD00')],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        margin=ft.Margin(bottom=0, top=-35, right=0, left=65),
                    ),
                    ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.PERSON, color='#26BD00'), ft.Text("Logout",color='#26BD00')],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=lambda _: self.logout(), # Assuming a login route
                    margin=ft.Margin(bottom=0, top=-10, right=0, left=-10),
                    ink=True,
                    
                ),
                ]),
                margin=ft.Margin(bottom=13, top=0, right=0, left=0)
            )
        else:
            self.avatar = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"{str(get_apelido(self.usuario)).capitalize()}",color=ft.Colors.BLACK,weight=ft.FontWeight.BOLD,size=16)
                    ],spacing=15),
                    ft.Container(
                        content=ft.Column([ft.Text(f"{str(get_cargo(self.usuario)).capitalize()}",size=12,color='#26BD00')],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        margin=ft.Margin(bottom=0, top=-35, right=0, left=65),
                    ),
                    ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.PERSON, color='#26BD00'), ft.Text("Logout",color='#26BD00')],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=lambda _: self.logout(), # Assuming a login route
                    margin=ft.Margin(bottom=0, top=-10, right=0, left=-10),
                    ink=True,
                    
                ),
                ]),
                margin=ft.Margin(bottom=13, top=0, right=0, left=0)
            )
        if self.resize.is_desktop():
            return ft.Container(
                content=ft.Column([ft.Column(self.sidebar_items, expand=True),self.avatar],alignment=ft.MainAxisAlignment.SPACE_BETWEEN, horizontal_alignment=ft.CrossAxisAlignment.START,expand=True),
                bgcolor="#ffffff" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#060606",
                border=ft.Border(right=ft.BorderSide(2, "#B9F4A9")),
                border_radius=8,
                height=self.page.height,
                width=self.page.width * 0.12
            )
        elif self.resize.is_mobile():
            return ft.Container(
                content=ft.Row(self.sidebar_items_mobile, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#ffffff" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1a1a1a",
                border=ft.Border(right=ft.BorderSide(2, "#B9F4A9"),left=ft.BorderSide(2, "#B9F4A9"),bottom=ft.BorderSide(2, "#B9F4A9")),
                border_radius=8,
                adaptive=True,
                expand=True
            )
        elif self.resize.is_tablet():
            return ft.Container(
                content=ft.Row(self.sidebar_items_mobile, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#ffffff" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1a1a1a",
                border=ft.Border(right=ft.BorderSide(2, "#B9F4A9"),left=ft.BorderSide(2, "#B9F4A9"),bottom=ft.BorderSide(2, "#B9F4A9")),
                border_radius=8,
                adaptive=True,
                expand=True
            )