from openpyxl import load_workbook
from funcoes import (verempresa,puxardados,converter_xlsx_para_pdf)
import flet as ft
import datetime as dt
from pathlib import Path
class Gerardoc:
        def __init__(self,page:ft.Page) -> None:
            self.page = page
            self.page.clean()
            self.modelos_excel = self.carregar_modelos_excel()
            self.empresas = verempresa()

        def build_view(self):
            from Interfaces.main_interface import Main_interface
            from Interfaces.sidebar import Sidebar
            self.sidebar = Sidebar(self.page)
            self.main = Main_interface(self.page)
            self.listview = ft.ListView(expand=True)
            self.listviewtypes = ft.ListView(expand=True)
            self.listviewexam = ft.ListView(expand=True)
            self.atualizar_lista_modelos()
            self.drop = ft.Dropdown(label="Empresas",autofocus=True,options=[],width=200)
            self.carregardrop()
            self.nomeclb = ft.TextField(label="Nome Completo",border_radius=16,width=300)
            self.cpfclb = ft.TextField(label="CPF",border_radius=16,width=300)
            self.datanascimentoclb = ft.TextField(label="Data de nascimento",border_radius=16,width=300)
            self.funcaoclb = ft.TextField(label="Função",border_radius=16,width=300)
            self.setorclb = ft.TextField(label="Setor",border_radius=16,width=300)
            self.clbinterface =ft.Column([
                    ft.Row([
                        ft.Text("Insira os dados do colaborador")
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row([
                        self.nomeclb,self.cpfclb
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row([
                        self.datanascimentoclb
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row([
                        self.setorclb,self.funcaoclb
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row([
                        ft.TextButton(text="Gerar documento",icon=ft.Icons.SEND_AND_ARCHIVE,
                                        style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=5,bgcolor=ft.Colors.LIGHT_GREEN_ACCENT,text_style=ft.TextStyle(weight=ft.FontWeight.W_400,color=ft.Colors.WHITE)),
                                        icon_color=ft.Colors.BLACK45,width=150,on_click=self.gerar_documento),
                        ft.TextButton(text="Limpar",icon=ft.Icons.SEND_AND_ARCHIVE,
                                        style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=5,bgcolor=ft.Colors.LIGHT_GREEN_ACCENT,text_style=ft.TextStyle(weight=ft.FontWeight.W_400,color=ft.Colors.WHITE)),
                                        icon_color=ft.Colors.BLACK45,on_click=lambda e: self.limpar(e),width=150)
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.doccontent = ft.Container(
                content=ft.Row([
                    ft.Column([
                        self.main.cardmain("Modelos de Exame",self.page.width*0.19,None,self.listview,False),
                        self.main.cardmain("Tipos do exame",self.page.width*0.19,None,self.listviewtypes,True)
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.EDIT, color=ft.Colors.GREY_700),
                            ft.Text("Gerar documento", size=30),
                        ]
                        ),
                        self.main.cardmain("Contratante".upper(),self.page.width*0.25,None,self.drop,False),
                        self.main.cardmain("Colaborador".upper(),None,None,self.clbinterface,False)
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Column([
                        self.main.cardmain("Exames a elencar",self.page.width*0.20,None,self.listviewexam,False)
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    
                    
                ],alignment=ft.MainAxisAlignment.START,vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=35)
            )
            return ft.Row(
                [
                    self.sidebar.build(),
                    ft.Column([ft.Container(content=self.doccontent,width=self.page.width*0.90)],scroll=ft.ScrollMode.ADAPTIVE,
                                width=self.page.width*0.90,adaptive=True,alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START)
                ],
                width=self.page.width,
                height=self.page.height,
            )
        
        def limpar(self,e):
            self.nomeclb.value = None
            self.datanascimentoclb.value = None
            self.cpfclb.value = None
            self.setorclb.value = None
            self.funcaoclb.value = None
            self.nomeclb.update()
            self.datanascimentoclb.update()
            self.cpfclb.update()
            self.setorclb.update()
            self.funcaoclb.update()
        
        def carregar_modelos_excel(self):
            modelos = []
            modelos_dir = Path(r"C:\Users\claud\OneDrive\Desktop\iClinica\modelos_excel")
                
            if not modelos_dir.exists():
                 modelos_dir.mkdir()
                
            for arquivo in modelos_dir.glob("*.xlsx"):
                modelos.append(arquivo.name.replace(".xlsx",""))
            return modelos           
        
        def atualizar_lista_modelos(self):
            self.types = [
                "ADMISSIONAL",
                "DEMISSIONAL" ,
                "MUDANÇA DE RISCO",
                "PERIÓDICO",
                "RETORNO A FUNÇÃO"
            ]
            self.exams =[
                "ANAMNESE",
                "AUDIOMETRIA",
                "HEMOGRAMA",
                "PARASITOLOGICO",
                "ELETROCARDIOGRAMA",
                "GLICEMIA",
                "PSICOSSOCIAL",
                "V.D.R.L",
                "ESPIROMETRIA",
                "RAIO-X", 
            ]
            self.listview.controls.clear()
            self.checkbox = ft.Checkbox(label=ft.Text("Gerar em todos os modelos"),on_change=self.selecionartodos,
                                        label_position=ft.LabelPosition.LEFT,check_color="#26BD00",active_color="#D3FACA")
            self.listview.controls.append(ft.Text("Modelos disponiveis: ",text_align=ft.TextAlign.START))
            self.listviewtypes.controls.append(ft.Text("Qual tipo do documento: ",text_align=ft.TextAlign.START))
            self.listviewexam.controls.append(ft.Text("Quais exames elencar: ",text_align=ft.TextAlign.START))
            for modelo in self.modelos_excel:
                self.listview.controls.append(
                    ft.ListTile(
                        title=ft.Text(modelo),
                        on_click=self.selecionar_modelo,
                        enable_feedback=True,
                        selected_color="#26BD00",
                        title_alignment=ft.ListTileTitleAlignment.CENTER,
                        bgcolor=ft.Colors.GREY_100,
                        selected_tile_color=ft.Colors.with_opacity(0.2,ft.Colors.LIGHT_GREEN_ACCENT_100)
                            
                    )
                )
            if not self.modelos_excel:
                self.listview.controls.append(
                    ft.ListTile(
                        title=ft.Text("Nenhum modelo encontrado na pasta 'modelos_excel'"),
                        subtitle=ft.Text("Adicione modelos Excel (.xlsx) nesta pasta")
                    )
                )
            for tipo in self.types:
                self.listviewtypes.controls.append(
                    ft.ListTile(
                        title=ft.Text(tipo),
                        enable_feedback=True,
                        on_click=self.selecionar_tipo,
                        selected_color="#26BD00",
                        title_alignment=ft.ListTileTitleAlignment.CENTER,
                        bgcolor=ft.Colors.with_opacity(0.6,ft.Colors.GREY_200),
                        height=40,
                        selected_tile_color=ft.Colors.with_opacity(0.2,ft.Colors.LIGHT_GREEN_ACCENT_100)
                    )
                )
            for exam in self.exams:
                self.listviewexam.controls.append(
                    ft.ListTile(
                        title=ft.Text(exam),
                        enable_feedback=True,
                        on_click=self.selecionar_exames,
                        selected_color="#26BD00",
                        title_alignment=ft.ListTileTitleAlignment.CENTER,
                        bgcolor=ft.Colors.with_opacity(0.6,ft.Colors.GREY_200),
                        height=40,
                        selected_tile_color=ft.Colors.with_opacity(0.2,ft.Colors.LIGHT_GREEN_ACCENT_100)
                    )
                )
            self.listview.controls.append(self.checkbox)            
        
        async def selecionar_modelo(self, e):
            e.control.selected = not getattr(e.control, 'selected', False)
            tiles = [control for control in self.listview.controls if isinstance(control, ft.ListTile)]
            todos_selecionados = all(getattr(tile, 'selected', False) for tile in tiles)
            self.checkbox.value = todos_selecionados
            self.page.update()
        
        async def selecionar_tipo(self, e):
            if getattr(e.control, 'selected', False):
                for control in self.listviewtypes.controls:
                    control.selected = False # type: ignore
            else:
                for control in self.listviewtypes.controls:
                    control.selected = False # type: ignore
                e.control.selected = True
            self.page.update()           
        
        async def selecionartodos(self,e):
            selecionar_todos = e.control.value
                # Aplica a seleção a todos os ListTiles
            for control in self.listview.controls:
                if isinstance(control, ft.ListTile):
                    control.selected = selecionar_todos       
        
        def carregardrop(self):
            self.drop.options.clear() #type: ignore
            if self.empresas:
                for empresa in self.empresas:
                    self.drop.options.append( #type: ignore
                        ft.DropdownOption(
                            text=f"{empresa[0]}",
                        )
                    )    
            else:
                self.drop.options.append( #type: ignore
                    ft.DropdownOption(
                        text=f"{"DB OFF ou Nenhuma Empresa Cadastrada"}",
                        disabled=True
                    )
                )            
        
        def gerar_documento(self, e):
            def converter():
                converter_xlsx_para_pdf(rf"C:\Users\claud\OneDrive\Desktop\iClinica\documentos_gerados\{nome_arquivo}",rf"C:\Users\claud\OneDrive\Desktop\iClinica\temp\{nome_arquivo.replace(".xlsx",".pdf")}")
            nome = self.nomeclb.value or ""
            cpf = self.cpfclb.value or ""
            nascimento = self.datanascimentoclb.value or ""
            funcao = self.funcaoclb.value or ""
            setor = self.setorclb.value or ""
            empresa = self.drop.value or ""
            cnpj = puxardados(empresa)
            modelos_selecionados = [
                control.title.value # type: ignore
                for control in self.listview.controls 
                if isinstance(control, ft.ListTile) and getattr(control, "selected", False)]
            if not modelos_selecionados:
                self.modal = ft.SnackBar(content=ft.Text("Selecione pelo menos um modelo!"),bgcolor=ft.Colors.RED)
                self.page.snack_bar = self.modal
                self.modal.open = True
                self.page.add(self.modal)
                return
            for modelo in modelos_selecionados:
                caminho_modelo = Path(r"C:\Users\claud\OneDrive\Desktop\iClinica\modelos_excel") / f"{modelo}.xlsx"
                print(modelo)
                if not caminho_modelo.exists():
                    continue  
                if modelo == "ANAMNESE":
                    wb = load_workbook(caminho_modelo)
                    ws = wb.active
                    ws["B2"] = nome# type: ignore
                    ws["B3"] = cpf # type: ignore
                    ws["B4"] = nascimento # type: ignore
                    ws["B5"] = funcao # type: ignore
                    ws["B6"] = setor # type: ignore
                    ws["B7"] = empresa # type: ignore
                    ws["B8"] = dt.datetime.now().strftime("%d/%m/%Y") # type: ignore
                    ws["B9"] = cnpj[0][0] # type: ignore
                    saida = Path(r"C:\Users\claud\OneDrive\Desktop\iClinica\documentos_gerados")
                    saida.mkdir(exist_ok=True)
                    nome_arquivo = f"{modelo}--{empresa.replace(' ', '_')}_{nome.replace(' ', '_')}_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
                    wb.save(saida / nome_arquivo)
                    self.show_loading(self.page,True)
                    converter()
                    self.page.overlay.clear()
                elif modelo == "ASO":
                    wb = load_workbook(caminho_modelo)
                    ws = wb.active
                    ws["B2"] = nome# type: ignore
                    ws["B3"] = cpf # type: ignore
                    ws["B4"] = nascimento # type: ignore
                    ws["B5"] = funcao # type: ignore
                    ws["B6"] = setor # type: ignore
                    ws["B7"] = empresa # type: ignore
                    ws["B8"] = dt.datetime.now().strftime("%d/%m/%Y") # type: ignore
                    ws["B9"] = cnpj[0][0] # type: ignore
                    saida = Path(r"C:\Users\claud\OneDrive\Desktop\iClinica\documentos_gerados")
                    saida.mkdir(exist_ok=True)
                    nome_arquivo = f"{modelo}--{empresa.replace(' ', '_')}_{nome.replace(' ', '_')}_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
                    wb.save(saida / nome_arquivo)
                    self.show_loading(self.page,True)
                    converter()
                    self.page.overlay.clear()
                elif modelo == "AUDIOMETRIA":
                    wb = load_workbook(caminho_modelo)
                    ws = wb.active
                    ws["B2"] = nome# type: ignore
                    ws["B3"] = cpf # type: ignore
                    ws["B4"] = nascimento # type: ignore
                    ws["B5"] = funcao # type: ignore
                    ws["B6"] = setor # type: ignore
                    ws["B7"] = empresa # type: ignore
                    ws["B8"] = dt.datetime.now().strftime("%d/%m/%Y") # type: ignore
                    ws["B9"] = cnpj[0][0] # type: ignore
                    saida = Path(r"C:\Users\claud\OneDrive\Desktop\iClinica\documentos_gerados")
                    saida.mkdir(exist_ok=True)
                    nome_arquivo = f"{modelo}--{empresa.replace(' ', '_')}_{nome.replace(' ', '_')}_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
                    wb.save(saida / nome_arquivo)
                    self.show_loading(self.page,True)
                    converter()
                    self.page.overlay.clear()
            self.nomeclb.value = None
            self.cpfclb.value = None
            self.datanascimentoclb.value = None
            self.funcaoclb.value = None
            self.setorclb.value = None
            self.nomeclb.update()
            self.cpfclb.update()
            self.datanascimentoclb.update()
            self.funcaoclb.update()
            self.setorclb.update()
            self.modal = ft.SnackBar(content=ft.Text("Documentos Gerados"),bgcolor=ft.Colors.GREEN)
            self.page.snack_bar = self.modal
            self.modal.open = True
            self.page.add(self.modal)      
        
        def show_loading(self,page, show=True):
            loading = ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(width=50, height=50, color=ft.Colors.LIGHT_GREEN),
                        ft.Text("Carregando...", size=16, color=ft.Colors.BLACK)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.Alignment(x=0,y=0),
                bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.WHITE30),
                expand=True
            )
                
            if show:
                page.overlay.append(loading)
            else:
                if loading in page.overlay:
                    page.overlay.remove(loading)
                    page.overlay.clear()
                    loading.visible = False
                    page.update()
                else:
                    pass    
        
        async def selecionar_exames(self, e):
            e.control.selected = not getattr(e.control, 'selected', False)
            self.page.update()