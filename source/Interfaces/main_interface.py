import flet as ft 
import asyncio
import datetime as dt
from database.databasecache import diccreate
import locale
from pathlib import Path
from Interfaces.sidebar import Sidebar

class Main_interface:
    def __init__(self, page: ft.Page):
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.page = page
        self.parar_evento = asyncio.Event()
        self.diario = 0.0
        self.mensal = 0.0
        self.contas = 0.0
        self.documentospr = self.documentosgerados()
        self.saud = ft.Text(size=15, color=ft.Colors.GREY_800, weight=ft.FontWeight.W_700)
        self.icone = ft.Icon(ft.Icons.SUNNY if self.saudacao() == 1 or self.saudacao() == 2 else ft.Icons.DARK_MODE, color=ft.Colors.YELLOW)
        self.tabct = self.buildtableE(self.gerarlinhas(self.documentospr))
        self.cardcontainer = ft.Container(content=self.buildcards(self.diario, self.mensal, self.contas))

    def saudacao(self):
        if 6 <= int(dt.datetime.now().strftime("%H")) < 12:
            self.saud.value = "BOM DIA"
            return 1
        elif 12 <= int(dt.datetime.now().strftime("%H")) < 16:
            self.saud.value = "BOA TARDE"
            return 2
        else:
            self.saud.value = "BOA NOITE"
            return 3

    def documentosgerados(self) -> list:
        documents = []
        documentosdir = Path(r"C:\Users\claud\OneDrive\Desktop\iClinica\documentos_gerados")
        if not documentosdir.exists():
            documents.append(ft.ListTile(ft.Text("A Pasta de saída não existe!")))
            return documents
        else:
            for doc in documentosdir.glob("*.xlsx"):
                documents.append(doc.name.replace(".xlsx", ""))
            return documents

    def buildtableE(self, linhas):
        self.empresastb = ft.Column([
            ft.Row([
                ft.DataTable(
                    heading_row_color="#A1FB8B",
                    horizontal_lines=ft.BorderSide(1),
                    data_row_color=ft.Colors.WHITE,
                    divider_thickness=2,
                    expand=True,
                    heading_text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                    border_radius=25,
                    columns=[
                        ft.DataColumn(ft.Text("Exames", text_align=ft.TextAlign.CENTER), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    rows=linhas,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        return self.empresastb

    def gerarlinhas(self, data):
        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(linhas)),
                ]
            ) for linhas in data
        ]

    def buildcards(self, diario, mensal, contas):
        self.card_diario_home = self.cardfloat(icon=ft.Icons.MONETIZATION_ON_OUTLINED, title="Entrada", value=locale.currency(diario, grouping=True),
                                  barra="Entrada de hoje", iconbarra=ft.Icons.ARROW_UPWARD, corbarra=ft.Colors.GREEN, larg=300, color=ft.Colors.BLACK)
        self.card_mensal_home = self.cardfloat(icon=ft.Icons.MONEY, title="Mensal", value=locale.currency(mensal, grouping=True),
                                  barra="Receita do mês anterior", iconbarra=ft.Icons.ARROW_UPWARD, corbarra=ft.Colors.GREEN, larg=300, color=ft.Colors.BLACK)
        self.card_contas_home = self.cardfloat(icon=ft.Icons.MONEY_OFF, title="A Pagar", value=locale.currency(contas, grouping=True),
                                  barra="Saida de caixa", iconbarra=ft.Icons.ARROW_DOWNWARD, corbarra=ft.Colors.RED, larg=300, color=ft.Colors.RED)
        return ft.Row(
            [
                self.card_diario_home,
                self.card_contas_home,
                self.card_mensal_home,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    async def diccreate_force(self):
        return await diccreate(force_update=True)

    def on_diccreate_done(self, future):
        dadosapi = future.result()
        self.diario = dadosapi['diario'] if dadosapi else 0.0
        self.mensal = dadosapi['mensal'] if dadosapi else 0.0
        self.contas = dadosapi['contas'] if dadosapi else 0.0
        self.cardcontainer.content = self.buildcards(self.diario, self.mensal, self.contas)
        self.cardcontainer.update()
        self.page.update()

    def cardfloat(self, icon, title, value, barra, iconbarra, corbarra, larg, color):
        text_widget = ft.Text(value, size=25, weight=ft.FontWeight.BOLD, color=color)
        card = ft.Card(
            elevation=10,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text(title, color=ft.Colors.BLACK54),
                            ft.Icon(icon, color=ft.Colors.PURPLE),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        text_widget,
                        ft.Row(
                            [
                                ft.Text(barra),
                                ft.Icon(iconbarra, color=corbarra),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    tight=True,
                ),
                width=larg,
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                border=ft.Border(right=ft.BorderSide(2, ft.Colors.LIGHT_GREEN_ACCENT_100))
            ),
        )
        return card

    def cardmain(self, title, larg, alt, value, expand):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(title, color=ft.Colors.BLACK54, weight=ft.FontWeight.BOLD, size=19),
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    value
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
                padding=20,
                width=larg,
                height=alt,
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                expand=expand,
                border=ft.Border(right=ft.BorderSide(2, ft.Colors.LIGHT_GREEN_ACCENT_100))
            ),
            elevation=5,
        )

    def build_view(self):
        
        sidebar_instance = Sidebar(self.page)
        self.homecontent = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row(
                        [
                            self.icone,
                            self.saud
                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                ),
                self.cardcontainer,
                ft.Container(
                    content=ft.Row([
                        self.cardmain("Documentos Gerados", self.page.width * 0.55, None, self.tabct, True),
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ),
            ])
        )
        self.future = self.page.run_task(self.diccreate_force)
        self.future.add_done_callback(self.on_diccreate_done)
        return ft.Row(
            [
                sidebar_instance.build(),
                ft.Column([ft.Container(content=self.homecontent, padding=10, width=self.page.width * 0.88, )],
                          scroll=ft.ScrollMode.ADAPTIVE,
                          width=self.page.width * 0.88, expand=True, adaptive=True, alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            width=self.page.width,
            height=self.page.height,
        )
        