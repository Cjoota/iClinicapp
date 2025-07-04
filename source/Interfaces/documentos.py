import win32com
import os
import flet as ft
from pathlib import Path
from Interfaces.main_interface import Main_interface
from Interfaces.sidebar import Sidebar
from Interfaces.telaresize import Responsive
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

        def on_resize(self,e):
            if self.page.route == "/documentos":
                self.responsive = Responsive(self.page)
                self.responsive.atualizar_widgets(self.build_view())
        def build_view(self) -> None:
            if self.responsive.is_desktop():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.printbutton = ft.TextButton(icon=ft.Icons.PRINT, text="Imprimir selecionados", on_click=lambda e: self.imprimir(e),width=150,style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE))
                self.deletebutton = ft.TextButton(icon=ft.Icons.DELETE, text="Excluir selecionados", on_click=lambda e: self.delete(e),width=150,
                                                icon_color=ft.Colors.RED,style=ft.ButtonStyle(text_style=ft.TextStyle(color=ft.Colors.RED),color=ft.Colors.with_opacity(0.4, ft.Colors.RED),bgcolor=ft.Colors.WHITE))
                self.opendoc = ft.TextButton(icon=ft.Icons.OPEN_IN_FULL, text="Abrir selecionados", on_click=lambda e: self.abrirdoc(e),width=150,
                                                icon_color=ft.Colors.GREEN,style=ft.ButtonStyle(text_style=ft.TextStyle(color=ft.Colors.GREEN),color=ft.Colors.with_opacity(0.4, ft.Colors.GREEN),bgcolor=ft.Colors.WHITE))
                self.docwidgets = ft.Column([
                    ft.Row([ft.Text("Exames gerados", size=30,color=ft.Colors.GREY_800,weight=ft.FontWeight.W_400)],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Row([
                        self.printbutton,self.deletebutton,self.opendoc
                     ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        self.main.cardmain("Exames",None,None,self.docinterface,True)
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START,expand=True)
                self.doccontent = ft.Container(
                    content=ft.Column(
                        [
                            self.docwidgets
                        ]
                        ,alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START,expand=True),expand=True
                )
                self.atualizar_lista()
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
                documents.append(ft.ListTile(ft.Text("A Pasta de saída não existe!")))
                return documents
            else:
                for doc in documentosdir.glob("*.xlsx"):
                    documents.append(doc.name.replace(".xlsx",""))
                return documents
        def atualizar_lista(self)-> None:
            self.docinterface.controls.clear()
            self.docinterface.controls.append(ft.Text("Exames prontos: ",text_align=ft.TextAlign.START))
            for docu in self.documentosprontos:
                    self.docinterface.controls.append(
                        ft.ListTile(
                            title=ft.Text(docu),
                            enable_feedback=True,
                            selected_color="#26BD00",
                            on_click=self.selecionar_modelo,
                            title_alignment=ft.ListTileTitleAlignment.CENTER,
                            bgcolor=ft.Colors.GREY_100,
                        )
                    )
            if not self.documentosprontos:
                    self.docinterface.controls.append(
                        ft.ListTile(
                            title=ft.Text("Nenhum exame encontrado."),
                            subtitle=ft.Text("Gere documentos na aba GERAR EXAMES!")
                        )
                    )
        def imprimir(self,e)-> None:
            try:
                for docs in self.documentosselecionados:
                    excel = win32com.client.Dispatch("Excel.Application")
                    excel.Visible = False  
                    excel.DisplayAlerts = False
                    wb = excel.Workbooks.Open(rf"documentos_gerados\{docs}.xlsx")
                    wb.Worksheets[0].PrintOut()  
                    wb.Close(False)
                    excel.Quit()
            except Exception as e:
                print(str(e))
        def delete(self,e)-> None:
            def excluir(e):
                for doc in self.documentosselecionados:
                    if os.path.exists(rf"documentos_gerados\{doc}.xlsx"):
                        os.remove(rf"documentos_gerados\{doc}.xlsx")
                    if os.path.exists(rf"temp\{doc}.pdf"):
                        os.remove(rf"temp\{doc}.pdf")
                    else:
                        pass
                self.documentosprontos = self.documentosgerados()
                self.atualizar_lista()
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
        async def selecionar_modelo(self, e) -> None:
            e.control.selected = not getattr(e.control, 'selected', False)
            self.documentosselecionados = [
                control.title.value #type: ignore
                for control in self.docinterface.controls 
                if isinstance(control, ft.ListTile) and getattr(control, "selected", False)]
            self.page.update()  
        async def selecionartodos(self,e) -> None:
            selecionar_todos = e.control.value
            # Aplica a seleção a todos os ListTiles
            for control in self.docinterface.controls:
                if isinstance(control, ft.ListTile):
                    control.selected = selecionar_todos
        def abrirdoc(self,e)-> None:
            if self.documentosselecionados != None:
                for doc in self.documentosselecionados:
                        if os.path.exists(rf"documentos_gerados\{doc}.xlsx"):
                            os.makedirs(rf"temp", exist_ok=True)
                            self.page.launch_url(rf"http://192.168.3.24:8001/pdf/{doc}.pdf")
                        else:
                            pass