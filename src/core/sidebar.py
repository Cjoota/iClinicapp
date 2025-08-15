from pathlib import Path
import flet as ft
import gender_guesser.detector as gender

from src.utils.telaresize import Responsive
from src.pages.LoginPage.interface import LoginPage
from src.functions.funcs import Verificacoes, get_cargo, get_apelido


class Sidebar:
    def __init__(self, page: ft.Page):
        self.page = page
        self.resize = Responsive(self.page)
        self.login = LoginPage(page)
        self.vr = Verificacoes()
        self.avatar = None
        self.usuario = str(self.page.session.get("user"))
        self.genero = gender.Detector()
        self.menu_items = []

    def logout(self):
        def sair(e):
            if self.page.session.contains_key("perm"):
                self.page.session.remove("perm")
            if self.page.session.contains_key("logado"):
                self.page.session.remove("logado")
            if self.page.session.contains_key("user"):
                self.page.session.remove("user")
            if self.page.client_storage.contains_key("nick"):
                self.page.client_storage.remove("nick")
            self.page.go("/login")

        alert = ft.AlertDialog(
            modal=True,
            title="Logout",
            content=ft.Text("Deseja mesmo sair?"),
            actions=[
                ft.TextButton(text="Sim", on_click=lambda e: sair(e), style=ft.ButtonStyle(color='#26BD00')),
                ft.TextButton(text="Não", on_click=lambda _: self.page.close(alert), style=ft.ButtonStyle(color='#26BD00'))
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.open(alert)
        alert.open = True

    def on_change(self, e, rota):
        self.page.go(rota)
        self.update_selection()
        self.page.update()

    def update_selection(self):
        current_route = self.page.route
        for item in self.menu_items:
            is_selected = item.data == current_route
            item.bgcolor = "#D4FFCA" if is_selected else ft.Colors.WHITE
            item.border = ft.border.only(left=ft.BorderSide(4, '#26BD00')) if is_selected else None
            
            if hasattr(item, 'content') and isinstance(item.content, ft.Row):
                for control in item.content.controls:
                    if isinstance(control, ft.Icon):
                        control.color = '#26BD00' if is_selected else ft.Colors.GREY_600
                    elif isinstance(control, ft.Text):
                        control.color = '#26BD00' if is_selected else ft.Colors.BLACK

    def menu_item(self, icon, text, rota):
        option = ft.Container(
            content=ft.Row([ft.Icon(icon, color=ft.Colors.GREY_600), ft.Text(text, color=ft.Colors.BLACK)]),
            padding=5,
            on_click=lambda e: self.on_change(e,rota=rota),
            margin=ft.Margin(bottom=0, top=0, right=0, left=0),
            ink=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            data=rota,
        )
        self.menu_items.append(option)
        return option

    def build(self):
        if not self.resize.is_shd():
            self.avatar = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([ft.Divider(thickness=1, color=ft.Colors.with_opacity(0.4, ft.Colors.GREY_400))],
                                          alignment=ft.MainAxisAlignment.CENTER,
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        width=200,
                        margin=ft.Margin(left=0, top=0, right=0, bottom=-10)
                    ),
                    ft.Row([
                        ft.CircleAvatar(foreground_image_src="mano.png" if self.genero.get_gender(get_apelido(self.usuario)) == "male" else "female.png",
                                        radius=25, bgcolor="#83ff58"),
                        ft.Text(f"{str(get_apelido(self.usuario)).capitalize()}",
                                color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD, size=16)
                    ], spacing=15),
                    ft.Container(
                        content=ft.Column([ft.Text(f"{str(get_cargo(self.usuario)).capitalize()}", size=12, color='#26BD00')],
                                          alignment=ft.MainAxisAlignment.CENTER,
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        margin=ft.Margin(bottom=0, top=-35, right=0, left=65),
                    ),
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.PERSON, color='#26BD00'), ft.Text("Logout", color='#26BD00')],
                                       alignment=ft.MainAxisAlignment.CENTER,
                                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        on_click=lambda _: self.logout(),
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
                        ft.Text(f"{str(get_apelido(self.usuario)).capitalize()}",
                                color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD, size=16)
                    ], spacing=15),
                    ft.Container(
                        content=ft.Column([ft.Text(f"{str(get_cargo(self.usuario)).capitalize()}", size=12, color='#26BD00')],
                                          alignment=ft.MainAxisAlignment.CENTER,
                                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        margin=ft.Margin(bottom=0, top=-35, right=0, left=65),
                    ),
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.PERSON, color='#26BD00'), ft.Text("Logout", color='#26BD00')],
                                       alignment=ft.MainAxisAlignment.CENTER,
                                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        on_click=lambda _: self.logout(),
                        margin=ft.Margin(bottom=0, top=-10, right=0, left=-10),
                        ink=True,
                    ),
                ]),
                margin=ft.Margin(bottom=13, top=0, right=0, left=0)
            )

        if self.resize.is_desktop():
            self.menu_items = []
            self.sidebar_items = [
                ft.Container(
                    content=ft.Row([ft.Image(src="logo.png", height=60, width=60)],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.margin.only(top=5)
                ),
                self.menu_item(ft.Icons.HOME_OUTLINED, "Home", "/home"),
                self.menu_item(ft.Icons.MONETIZATION_ON, "Contabilidade", "/contabilidade"),
                ft.Container(
                    content=ft.Row([ft.Text("Empresarial", weight=ft.FontWeight.BOLD, size=16)],
                                alignment=ft.MainAxisAlignment.START),
                    padding=0,
                    margin=ft.Margin(bottom=0, top=10, left=5, right=0),
                ),
                self.menu_item(ft.Icons.BUSINESS, "Empresas", "/empresas"),
                self.menu_item(ft.Icons.CREATE_ROUNDED, "Gerar exames", "/criar_exame"),
                self.menu_item(ft.Icons.DESCRIPTION, "Exames gerados", "/exames_gerados"),
                self.menu_item(ft.Icons.CALENDAR_TODAY, "Agendamento", "/agendamento"),
                self.menu_item(ft.Icons.ASSIGNMENT, "Relacoes", "/relacoes"),
            ]
            return ft.Container(
                content=ft.Column([ft.Column(self.sidebar_items, expand=True), self.avatar],
                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                   horizontal_alignment=ft.CrossAxisAlignment.START,
                                   expand=True),
                bgcolor="#ffffff" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#060606",
                border=ft.Border(right=ft.BorderSide(2, "#B9F4A9")),
                border_radius=8,
                height=self.page.height,
                width=self.page.width * 0.12
            )
        elif self.resize.is_mobile() or self.resize.is_tablet():
            self.sidebar_items_mobile = [
                ft.Container(
                    content=ft.Image(src=r"logo.png", width=35, height=35),
                    padding=5,
                    bgcolor=ft.Colors.WHITE,
                ),
                self.menu_item(ft.Icons.HOME_OUTLINED, "Home", "/home"),
                self.menu_item(ft.Icons.PERSON, "Login", "/login"),
                self.menu_item(ft.Icons.MONETIZATION_ON, "Contabilidade", "/contabilidade"),
                self.menu_item(ft.Icons.BUSINESS, "Empresas", "/empresas"),
                self.menu_item(ft.Icons.CREATE_ROUNDED, "Gerar exames", "/gerardoc"),
                self.menu_item(ft.Icons.DESCRIPTION, "Exames gerados", "/documentos"),
                self.menu_item(ft.Icons.ASSIGNMENT, "Relacoes", "/relacoes"),
            ]
            return ft.Container(
                content=ft.Row(self.sidebar_items_mobile, alignment=ft.MainAxisAlignment.CENTER,
                               vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#ffffff" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1a1a1a",
                border=ft.Border(
                    right=ft.BorderSide(2, "#B9F4A9"),
                    left=ft.BorderSide(2, "#B9F4A9"),
                    bottom=ft.BorderSide(2, "#B9F4A9")
                ),
                border_radius=8,
                adaptive=True,
                expand=True
            )