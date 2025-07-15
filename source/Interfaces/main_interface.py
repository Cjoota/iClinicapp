import flet as ft 
import asyncio
import datetime as dt
import locale
import asyncio
from pathlib import Path
from Interfaces.sidebar import Sidebar
from Interfaces.telaresize import Resize, Responsive

class Main_interface:
    def __init__(self, page: ft.Page):
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.page = page
        self.page.on_resized = self.on_resize
        self.resize = Resize(self.page)
        self.responsive = Responsive(self.page)
        self.sidebar = Sidebar(self.page)
        self.parar_evento = asyncio.Event()
        self.gerados = self.get_gerados()
        self.documentospr = self.documentosgerados()
        self.saud = ft.Text(size=self.responsive.font_size(), color=ft.Colors.GREY_800, weight=ft.FontWeight.BOLD, font_family="Inter")
        self.icone = ft.Icon(ft.Icons.SUNNY if self.saudacao() == 1 or self.saudacao() == 2 else ft.Icons.DARK_MODE, color=ft.Colors.YELLOW,size=self.responsive.font_size()+20)
        self.tabct = ft.Container(content=self.buildtableE(self.gerarlinhas(self.documentospr)),border_radius=10
                                  ,border=ft.Border(left=ft.BorderSide(2,ft.Colors.GREY_200),top=ft.BorderSide(2,ft.Colors.GREY_200),right=ft.BorderSide(2,ft.Colors.GREY_200),bottom=ft.BorderSide(2,ft.Colors.GREY_200)))
        self.cardcontainer = ft.Container(content=self.buildcards(self.gerados[0], self.gerados[0], self.gerados[0])
                                          ,margin=ft.Margin(left=0,top=-150,right=0,bottom=0) if self.responsive.is_desktop() else None , padding=0
                                          )
        self.page.run_task(self.clock)
    
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
    
    def get_gerados(self):
        documentosdir = Path("documentos_gerados")
        try:
            if not documentosdir.exists():
                return [0]
            gerados = len([doc.name for doc in documentosdir.glob("*.xlsx")])
            
            return [gerados]
        except Exception as e:
            print(f"Erro ao listar documentos gerados: {e}")
            return [0]

    def on_resize(self,e):
        if self.responsive.is_desktop():
            self.responsive = Responsive(self.page)
            if self.page.route == "/home":
                self.page.views.clear()
                self.page.views.append(
                    ft.View(
                        self.page.route,
                        [self.build_view()]
                    )
                )
                self.page.go(self.page.route)
    
    def documentosgerados(self) -> list:
        documents = []
        documentosdir = Path(r"documentos_gerados")
        if not documentosdir.exists():
            documents.append(ft.ListTile(ft.Text("A Pasta de saída não existe!")))
            return documents
        else:
            for doc in documentosdir.glob("*.xlsx"):
                documents.append(doc.name.replace(".xlsx", ""))
            if documents == []:
                documents.append("""Nenhum Documento encontrado.\nGere os exames na aba Gerar Documento!""")
            return documents
   
    def barra_aviso(self,mensagem:str ,cor:str):
        snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=cor
        )
        self.page.open(snack_bar)
   
    def buildtableE(self, linhas):
        self.empresastb = ft.Column([
            ft.Row([
                ft.DataTable(
                    heading_row_color="#A1FB8B",
                    horizontal_lines=ft.BorderSide(1),
                    data_row_color=ft.Colors.WHITE,
                    divider_thickness=1,
                    expand=True,
                    heading_text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                    border_radius=25,
                    columns=[
                        ft.DataColumn(ft.Text("Exames Gerados", text_align=ft.TextAlign.CENTER), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    rows=linhas,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return self.empresastb

    def gerarlinhas(self, data):
        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(linhas)),
                ]
            ) for linhas in data
        ]

    def buildcards(self, gerados, agendados, prontos):
        self.card_diario_home = self.cardfloat(icon=ft.Icons.DOMAIN_VERIFICATION_OUTLINED, title="Exames", value=gerados,
                                  barra="Gerados Hoje", iconbarra=ft.Icons.DOMAIN_VERIFICATION, corbarra=ft.Colors.GREEN, larg=None, color=ft.Colors.BLACK)
        self.card_mensal_home = self.cardfloat(icon=ft.Icons.PERM_CONTACT_CALENDAR_OUTLINED, title="Agendados", value=agendados,
                                  barra="Agendados Hoje", iconbarra=ft.Icons.CALENDAR_MONTH_ROUNDED, corbarra=ft.Colors.GREEN, larg=None, color=ft.Colors.BLACK)
        self.card_contas_home = self.cardfloat(icon=ft.Icons.VERIFIED_OUTLINED, title="Exames Prontos", value=prontos,
                                  barra="Prontos Hoje", iconbarra=ft.Icons.VERIFIED, corbarra=ft.Colors.GREEN, larg=None, color=ft.Colors.BLACK)
        for card in [self.card_diario_home, self.card_mensal_home, self.card_contas_home]:
            card.col = {"xs": 4, "md": 2 if self.responsive.is_mobile() else 2.3, "sm": 3}

        return ft.ResponsiveRow(
            [
                self.card_diario_home,
                self.card_contas_home,
                self.card_mensal_home,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            run_spacing=0,
            spacing=self.responsive.spacing()
            
        )

    def cardfloat(self, icon, title, value, barra, iconbarra, corbarra, larg, color):
        text_widget = ft.Text(value, size=25 if self.responsive.is_desktop() or self.responsive.is_tablet() else 20, weight=ft.FontWeight.BOLD, color=color)
        card = ft.Container(
            scale=self.responsive.size_widget(),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text(title, color=ft.Colors.BLACK54),
                            ft.Icon(icon, color="#3D3D3D"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        text_widget,
                        ft.Row(
                            [
                                ft.Text(barra),
                                ft.Icon(iconbarra, color=corbarra),
                            ],
                            alignment=ft.MainAxisAlignment.END,spacing=2
                        ),
                    ],
                    tight=True,
                    spacing=0 
                ),
                width=larg,
                padding=self.responsive.padding(),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.Border(right=ft.BorderSide(2, '#B9F4A9')),
                
                
                
            ),padding=0
        )
        return card

    def cardmain(self, title, larg, alt, value, expand):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(title, color=ft.Colors.BLACK54, weight=ft.FontWeight.BOLD, size=19,text_align=ft.TextAlign.CENTER),
                    ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    value
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10,
                width=larg,
                height=alt,
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                expand=expand,
                border=ft.Border(right=ft.BorderSide(2, '#B9F4A9'))
            ),
            elevation=5,
        )
    
    async def clock(self):
        if self.page.route == "/home":
            self.data = dt.datetime.now().strftime("%d/%m/%Y")
            while True:
                self.horario = dt.datetime.now().strftime("%H:%M:%S")
                self.clock_text = f"{self.horario}\n{self.data}"
                self.relogio.value = self.clock_text
                if self.relogio.page is not None:     
                    self.relogio.update()
                await asyncio.sleep(1)
            
    def build_view(self):
        self.relogio = ft.Text("", text_align=ft.TextAlign.CENTER)
        if self.responsive.is_mobile():
            self.homecontent = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row(
                            [
                                self.icone,
                                self.saud
                            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=0
                        ),
                    ),
                    self.cardcontainer,
                    ft.Container(
                        content=ft.ResponsiveRow([
                            self.cardmain("Documentos Gerados", None ,None, self.tabct, True),
                        ], alignment=ft.MainAxisAlignment.CENTER , vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=0)
                    ),
                ]),padding=0
            )
        elif self.responsive.is_tablet():
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
                        content=ft.ResponsiveRow([
                            self.cardmain("Documentos Gerados", None ,None, self.tabct, True),
                        ], alignment=ft.MainAxisAlignment.CENTER , vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
                ])
            )
        elif self.responsive.is_desktop():
            self.homecontent = ft.Column([
                    ft.Container(
                        content=ft.Column(
                            [
                                self.icone,
                                self.saud,
                                self.relogio

                            ],alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0
                        ),margin=ft.Margin(left=80,top=40,right=0,bottom=0)
                    ),
                    self.cardcontainer,
                    ft.Container(
                        content=self.cardmain("Documentos Gerados", None ,None, self.tabct,True)
                    ),
                ],alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.START)
        self.page.run_task(self.clock)
        if self.responsive.is_mobile():
            return ft.Column(
                [
                    ft.Row([self.sidebar.build()],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,width=self.responsive.content_width()),
                    ft.Column([ft.Container(content=self.homecontent,padding=0)],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=0)
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=0
            )
        if self.responsive.is_tablet():
            return ft.Column(
                [
                    ft.Row([self.sidebar.build()],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([self.homecontent],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            return ft.Row(
                [
                    ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START),
                    ft.Container(content=self.homecontent,expand=True)
                ],
                width=self.page.width,
                height=self.page.height,
                alignment=ft.MainAxisAlignment.START
            )

    
        
        
