import asyncio
import flet as ft
import datetime as dt

class Sidebar:
    def __init__(self, page: ft.Page):
        self.page = page
        self.parar_evento = asyncio.Event()
        self.txt_relogio = ft.Text(
            size=15,
            color=ft.Colors.GREY_700,
            weight=ft.FontWeight.W_400,
            text_align=ft.TextAlign.CENTER)
        self.relogio_task = self.page.run_task(self.start_relogio)
        self.page.on_window_event = self.fechar_app

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

    async def atualizar_relogio(self):
        while not self.parar_evento.is_set():
            agora = dt.datetime.now()
            self.txt_relogio.value = agora.strftime("%H:%M:%S\n%d/%m/%Y")
            self.page.update()
            await asyncio.sleep(1)

    async def start_relogio(self):
        await self.atualizar_relogio()

    def build(self):
        self.sidebar_items = [
            ft.Container(
                content=ft.Text("iClinica Software", weight=ft.FontWeight.W_400, size=20),
                padding=10,
                bgcolor=ft.Colors.WHITE,
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.HOME_OUTLINED, color=ft.Colors.GREY_600), ft.Text("Home")]),
                padding=7,
                on_click=lambda _: self.page.go("/home"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                expand=True,
                width=200
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREY_600), ft.Text("Trocar Usuário")]),
                padding=7,
                on_click=lambda _: self.page.go("/login"), # Assuming a login route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.GREY_600), ft.Text("Contabilidade")]),
                padding=7,
                on_click=lambda _: self.page.go("/contabilidade"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200,
            ),
            ft.Container(
                content=ft.Text("Empresarial", weight=ft.FontWeight.BOLD, size=16),
                padding=1,
                margin=ft.Margin(bottom=0, top=10, left=0, right=0),
                width=200,
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.BUSINESS, color=ft.Colors.GREY_600), ft.Text("Empresas")]),
                padding=7,
                on_click=lambda _: self.page.go("/empresas"), # Assuming an empresas route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.CREATE_ROUNDED, color=ft.Colors.GREY_600), ft.Text("Gerar Documento")]),
                padding=7,
                on_click=lambda _: self.page.go("/gerardoc"), # Assuming a gerardoc route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.GREY_600), ft.Text("Documentos")]),
                padding=7,
                on_click=lambda _: self.page.go("/documentos"), # Assuming a documentos route
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200,
            ),
            ft.Container(
                content=ft.Text("Ferramentas", weight=ft.FontWeight.BOLD, size=16),
                padding=1,
                margin=ft.Margin(bottom=0, top=10, left=0, right=0),
                width=200,
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.FILE_UPLOAD, color=ft.Colors.GREY_600), ft.Text("Converter Arquivo")]),
                padding=7,
                on_click=lambda _: print("Converter Arquivo clicked"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200,
                disabled=True
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.SCANNER, color=ft.Colors.GREY_600), ft.Text("Digitalizar")]),
                padding=7,
                on_click=lambda _: print("Digitalizar clicked"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200,
                disabled=True
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.GREY_600), ft.Text("Agendamento")]),
                padding=7,
                on_click=lambda _: print("Agendamento clicked"),
                margin=ft.Margin(bottom=5, top=0, right=0, left=0),
                ink=True,
                width=200,
                disabled=True
            ),
            ft.Container(
                content=ft.Row([
                    self.txt_relogio
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ),
        ]
        return ft.Container(
            content=ft.Column(self.sidebar_items, scroll=ft.ScrollMode.ADAPTIVE, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#ffffff" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1a1a1a",
            border=ft.Border(right=ft.BorderSide(2, '#26BD00'), bottom=ft.BorderSide(0.5, '#26BD00')),
            border_radius=8,
            adaptive=True,
        )
