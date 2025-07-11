import win32com
import os
import flet as ft
from pathlib import Path
from Interfaces.main_interface import Main_interface
from Interfaces.sidebar import Sidebar
from Interfaces.telaresize import Responsive
from funcoes import converter_xlsx_para_pdf

class Documentos:
        def __init__(self,page:ft.Page) -> None:
            page.clean()
            self.page = page
            self.responsive = Responsive(self.page)
            self.servidor_rodando = False
            self.documentosprontos = self.documentosgerados()
            self.docinterface = ft.ListView(expand=True,divider_thickness=1)
            self.documentosselecionados = None
            self.page.on_resized = self.on_resize
        
        def buildtable(self,linhas) -> ft.Column:
            return ft.Column([
                ft.Row([
                    ft.DataTable(
                        column_spacing=20,
                        heading_row_color="#A1FB8B",
                        border_radius=25,
                        expand=True,
                        columns=[
                            ft.DataColumn(ft.Text("Exame",weight=ft.FontWeight.BOLD),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                            ft.DataColumn(ft.Text("Empresa",weight=ft.FontWeight.BOLD),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                            ft.DataColumn(ft.Text("Colaborador",weight=ft.FontWeight.BOLD),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                            ft.DataColumn(ft.Text("Data de criação",weight=ft.FontWeight.BOLD),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                            ft.DataColumn(ft.Text("Ações",weight=ft.FontWeight.BOLD),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                        ],
                        rows=linhas
                    )
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    
            ])
            
        def gerar_linhas(self, dataatt):
            return [
                ft.DataRow(
                    cells=
                    [
                        ft.DataCell(ft.Container(content=ft.Text(exame[0]), alignment=ft.alignment.center)),
                        ft.DataCell(ft.Container(content=ft.Text(exame[1]), alignment=ft.alignment.center)),
                        ft.DataCell(ft.Container(content=ft.Text(exame[2]), alignment=ft.alignment.center)),
                        ft.DataCell(ft.Container(content=ft.Text(exame[3]), alignment=ft.alignment.center)),
                        ft.DataCell(ft.Row(
                            [
                                ft.IconButton(icon=ft.Icons.OPEN_IN_BROWSER, icon_color=ft.Colors.BLACK, bgcolor=ft.Colors.GREEN_100,tooltip=ft.Tooltip("Abrir exame"),on_click=lambda e,idx=i: self.abrirdoc(idx)),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.BLACK, bgcolor=ft.Colors.RED_100,tooltip=ft.Tooltip("Excluir exame"),on_click=lambda e,idx=i: self.delete(idx))
                            ],alignment=ft.MainAxisAlignment.CENTER
                        )),
                    ]
                ) for i, exame in enumerate(dataatt)
            ]
    
        def on_resize(self,e):
            if self.page.route == "/documentos":
                self.responsive = Responsive(self.page)
                self.responsive.atualizar_widgets(self.build_view())
        
        def loading_(self,on:bool):
            if on is True:
                self.page.overlay.append(self.loading)
                self.loading.visible = True
                self.page.update()

            elif on is False:
                self.page.overlay.remove(self.loading)
                self.loading.visible = False
                self.page.update()

        def build_view(self) -> None:
            if self.responsive.is_desktop():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.tabela_exames = ft.Container(
                    content=self.buildtable(self.gerar_linhas(self.documentosprontos)),border_radius=10,expand=True
                )
                self.search_exam = ft.TextField(label="Buscar",width=300,on_change=self.atualizar_tabela,prefix_icon=ft.Icons.SEARCH)
                self.exames_interface = ft.Container(
                    content=ft.Column(
                        [
                            ft.Column([ft.Text("Buscar exame:"),self.search_exam],alignment=ft.MainAxisAlignment.START,expand=True),
                            ft.Row([self.tabela_exames],expand=True)
                        ],expand=True),expand=True
                )
                self.doccontent = ft.Container(
                    content=ft.Column(
                        [
                            self.main.cardmain("Exames gerados",None,None,self.exames_interface,True)
                        ]
                        ,alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START,expand=True,scroll=ft.ScrollMode.ADAPTIVE),expand=True,border_radius=10,adaptive=True
                )
                self.loading = ft.Container(content=ft.ProgressRing(width=60 , height=60 , stroke_width=6, color="#26f553"),visible=False,bgcolor=ft.Colors.with_opacity(0.4,ft.Colors.BLACK),expand=True,width=self.page.width,height=self.page.height,alignment=ft.alignment.center)
                return ft.Row(
                [
                    ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Column([self.doccontent],scroll=ft.ScrollMode.ADAPTIVE,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                width=self.page.width,
                height=self.page.height,
                vertical_alignment=ft.CrossAxisAlignment.START
                )
            elif self.responsive.is_tablet():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.printbutton = ft.TextButton(icon=ft.Icons.PRINT, text="Imprimir selecionados", on_click=lambda e: self.imprimir(e),width=150,style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE))
                self.deletebutton = ft.TextButton(icon=ft.Icons.DELETE, text="Excluir selecionados", on_click=lambda e: self.delete(e),width=150,
                                                icon_color=ft.Colors.RED,style=ft.ButtonStyle(text_style=ft.TextStyle(color=ft.Colors.RED),color=ft.Colors.with_opacity(0.4, ft.Colors.RED),bgcolor=ft.Colors.WHITE))
                self.opendoc = ft.TextButton(icon=ft.Icons.OPEN_IN_FULL, text="Abrir selecionados", on_click=lambda e: self.abrirdoc(e),width=150,
                                                icon_color=ft.Colors.GREEN,style=ft.ButtonStyle(text_style=ft.TextStyle(color=ft.Colors.GREEN),color=ft.Colors.with_opacity(0.4, ft.Colors.GREEN),bgcolor=ft.Colors.WHITE))
                self.docwidgets = ft.Column([
                    ft.Row([ft.Text("Exames gerados", size=30,color=ft.Colors.GREY_800,weight=ft.FontWeight.W_400)],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        self.printbutton,self.deletebutton,self.opendoc
                     ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        self.main.cardmain("Exames",None,None,self.docinterface,True)
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ])
                self.doccontent = ft.Container(
                    content=ft.Column(
                        [
                            self.docwidgets
                        ]
                        ,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,expand=True)
                )
                self.atualizar_lista()
                return ft.Column(
                [
                    ft.Row([self.sidebar.build()],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([self.doccontent],scroll=ft.ScrollMode.ADAPTIVE,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                width=self.page.width,
                height=self.page.height,
                )
            elif self.responsive.is_mobile():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.printbutton = ft.TextButton(icon=ft.Icons.PRINT, text="Imprimir selecionados", on_click=lambda e: self.imprimir(e),width=130,style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE))
                self.deletebutton = ft.TextButton(icon=ft.Icons.DELETE, text="Excluir selecionados", on_click=lambda e: self.delete(e),width=130,
                                                icon_color=ft.Colors.RED,style=ft.ButtonStyle(text_style=ft.TextStyle(color=ft.Colors.RED),color=ft.Colors.with_opacity(0.4, ft.Colors.RED),bgcolor=ft.Colors.WHITE))
                self.opendoc = ft.TextButton(icon=ft.Icons.OPEN_IN_FULL, text="Abrir selecionados", on_click=lambda e: self.abrirdoc(e),width=130,
                                                icon_color=ft.Colors.GREEN,style=ft.ButtonStyle(text_style=ft.TextStyle(color=ft.Colors.GREEN),color=ft.Colors.with_opacity(0.4, ft.Colors.GREEN),bgcolor=ft.Colors.WHITE))
                self.docwidgets = ft.Column([
                    ft.Row([ft.Text("Exames gerados", size=30,color=ft.Colors.GREY_800,weight=ft.FontWeight.W_400)],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        self.printbutton,self.deletebutton,self.opendoc
                     ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        self.main.cardmain("Exames",None,None,self.docinterface,True)
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ])
                self.doccontent = ft.Container(
                    content=ft.Column(
                        [
                            self.docwidgets
                        ]
                        ,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,expand=True)
                )
                self.atualizar_lista()
                return ft.Column(
                [
                    ft.Row([self.sidebar.build()],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([self.doccontent],scroll=ft.ScrollMode.ADAPTIVE,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                width=self.page.width,
                height=self.page.height,
                )
                 
        def documentosgerados(self)-> list:
            documents = []
            documentosdir = Path(r"documentos_gerados")
            if not documentosdir.exists():
                documents.append("A Pasta de saída não existe!")
                return documents
            for doc in documentosdir.glob("*.xlsx"):
                exame,empresa,colab,data,hora = doc.name.replace(".xlsx","").split()
                documents.append([exame,empresa.replace("-"," "),colab.replace("-"," "),data.replace("-","/"),hora.replace("-",":")])
            return documents
        
        def atualizar_tabela(self,e):
            termo_busca = str(self.search_exam.value).upper()
            if termo_busca == "" or termo_busca == None:
                self.documentosprontos = self.documentosgerados()
                self.tabela_exames.content = self.buildtable(self.gerar_linhas(self.documentosprontos))
                self.tabela_exames.update()
            else:
                self.documentosprontos = self.documentosgerados()
                linhas_filtradas = []
                for linha in self.documentosprontos:
                    if (
                        (termo_busca or "") in (linha[0] or "").upper() or
                        (termo_busca or "") in (linha[1] or "").upper() or
                        (termo_busca or "") in (linha[2] or "").upper() or
                        (termo_busca or "") in (linha[3] or "").upper()
                    ):
                        linhas_filtradas.append(linha)
                self.tabela_exames.content = self.buildtable(self.gerar_linhas(linhas_filtradas))
                self.tabela_exames.update()
        
        def delete(self,idx)-> None:
            def excluir(e):
                documentosdir = Path(r"documentos_gerados")
                documento = documentosdir.glob("*.xlsx")
                for i,doc in enumerate(documento):
                    if idx == i:
                        doc.unlink()
                self.documentosprontos = self.documentosgerados()
                self.tabela_exames.content = self.buildtable(self.gerar_linhas(self.documentosprontos))
                alert_dialog.open = False
                self.page.update()
            def close(e):
                alert_dialog.open = False
                self.page.update()
            alert_dialog = ft.AlertDialog(
                modal=True,
                title="Confirmação",
                content=ft.Text("Realmente deseja excluir esses arquivos?"),
                elevation=5,
                actions=[
                     ft.TextButton("Yes", on_click=excluir),
                     ft.TextButton("No", on_click=close),
                ]
            )
            self.page.overlay.append(alert_dialog)
            alert_dialog.open = True
            self.page.update()
        
        def abrirdoc(self,idx)-> None:
            try:
                documentosdir = Path(r"documentos_gerados")
                documento = documentosdir.glob("*.xlsx")
                for i,doc in enumerate(documento):
                    if idx == i:
                        os.makedirs(rf"pdf_temp", exist_ok=True)
                        if not os.path.exists(rf"pdf_temp\{doc.name.replace(".xlsx",".pdf")}"):
                            self.loading_(True)
                            converter_xlsx_para_pdf(f"{doc.absolute()}",f"pdf_temp/{doc.name.replace(".xlsx",".pdf")}")
                            self.loading_(False)
                        self.page.launch_url(rf"http://192.168.3.24:8001/pdf/{doc.name.replace(".xlsx",".pdf")}")
            except Exception as e:
                self.main.barra_aviso(f"Erro ao gerar visualização: {str(e)}",ft.Colors.RED)
                