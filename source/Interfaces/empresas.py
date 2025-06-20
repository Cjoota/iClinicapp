import flet as ft
from funcoes import (verempresa, cadasempresa,excluiremp)
class Empresas:
        def __init__(self,page: ft.Page):
            self.page = page
            self.page.clean()
            self.dados = verempresa()
        def limpar(self):
            self.razao.value = None
            self.cnpj.value = None
            self.contato.value = None
            self.endereco.value = None
            self.razao.update()
            self.cnpj.update()
            self.contato.update()
            self.endereco.update()
        def buildtableE(self,linhas):
            empresastb = ft.Column([
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
                        ft.DataColumn(ft.Text("Razão Social",text_align=ft.TextAlign.CENTER)),
                        ft.DataColumn(ft.Text("CNPJ",text_align=ft.TextAlign.CENTER)),
                        ft.DataColumn(ft.Text("Contato",text_align=ft.TextAlign.CENTER)),
                        ft.DataColumn(ft.Text("Endereço",text_align=ft.TextAlign.CENTER)),
                        ft.DataColumn(ft.Text("Ações",text_align=ft.TextAlign.CENTER)),
                    ],
                    rows=linhas
                    )
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,scroll=ft.ScrollMode.AUTO)
            return empresastb
        def gerarlinhas(self,data):
            return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(linhas[0])),
                    ft.DataCell(ft.Text(linhas[1])),
                    ft.DataCell(ft.Text(linhas[2])),
                    ft.DataCell(ft.Text(linhas[3])),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.RED,on_click=lambda e, idx=i: self.apagaremp(idx)))
                ]
            ) for i, linhas in enumerate(data)
            ]
        def cadastro(self):
            cadasempresa(self.razao.value,self.cnpj.value,self.contato.value, self.endereco.value)
            self.dados = verempresa()
            self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
            self.tabempresas.update()
            self.razao.value = None
            self.cnpj.value = None
            self.contato.value= None
            self.endereco.value = None
        def apagaremp(self,index):
            try:
                ex = self.dados[index]
                excluiremp(ex[1])
                self.dados = verempresa()
                self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
                self.tabempresas.update()
            except Exception as e:
                print(e)
        def atualizar_tabela(self,e):
            termo_busca = str(self.caixadebusca.value).lower()
            if termo_busca == "" or termo_busca == None:
                self.dados = verempresa()
                self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
                self.tabempresas.update()
            else:
                self.dados = verempresa()
                linhas_filtradas = []
                for linha in self.dados:
                    if (
                        (termo_busca or "") in (linha[0] or "").lower() or
                        (termo_busca or "") in (linha[1] or "").lower() or
                        (termo_busca or "") in (linha[2] or "").lower() or
                        (termo_busca or "") in (linha[3] or "").lower()
                    ):
                        linhas_filtradas.append(linha)
                self.tabempresas.content = self.buildtableE(self.gerarlinhas(linhas_filtradas))
                self.tabempresas.update()
        def build_view(self):
            from Interfaces.main_interface import Main_interface
            from Interfaces.sidebar import Sidebar
            self.main = Main_interface(self.page)
            self.sidebar = Sidebar(self.page)
            self.razao = ft.TextField(label="Razão Social",border_radius=10,)
            self.cnpj = ft.TextField(label="CNPJ",border_radius=10)
            self.contato = ft.TextField(label="Contato",border_radius=10,width=300)
            self.endereco = ft.TextField(label="Endereço",border_radius=10,width=300)
            self.tabempresas = ft.Container(
                content=self.buildtableE(self.gerarlinhas(self.dados)),
                border=ft.Border(top=ft.BorderSide(width=1)),
                border_radius=16,
                )
            self.caixadebusca = ft.TextField(
                label="Buscar",
                prefix_icon=ft.Icons.SEARCH,
                on_change=self.atualizar_tabela,
                border_radius=16,
                width=300
            )
            # INTERFACE
            self.cadinterface = ft.Column([
                ft.Row([
                    ft.Text("Insira os dados da empresa")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
                ),
                ft.Row([
                    self.razao, self.cnpj,
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=30,
                expand=True
                ),
                ft.Row([
                    self.endereco,self.contato
                ],alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=30,
                expand=True
                ),
                ft.Row([
                    ft.TextButton(text="Cadastrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=10,bgcolor=ft.Colors.LIGHT_GREEN_ACCENT)
                                ,icon=ft.Icons.SEND_AND_ARCHIVE,on_click=lambda _: self.cadastro(),width=120),
                    ft.TextButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.BLACK,style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=10,bgcolor=ft.Colors.RED_ACCENT)
                                ,text="Limpar",width=120,on_click=lambda _: self.limpar())           
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=30,)
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.empresascontent = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.BUSINESS, color=ft.Colors.GREY_700),
                        ft.Text("Empresas", size=30)
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row([
                        self.main.cardmain("Cadastro de Empresas",None,None,self.cadinterface,False)
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,adaptive=True
                    ),
                    ft.Row([
                        ft.Text("Procure pela Empresa desejada: "),
                        self.caixadebusca  
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row([
                        self.main.cardmain("Empresas Cadastradas",self.page.width*0.80,None,self.tabempresas,False)
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                ],scroll=ft.ScrollMode.ADAPTIVE),
            )
            # PAGE CONSTRUCT
            return ft.Row(
                [
                    self.sidebar.build(),
                    ft.Column([ft.Container(content=self.empresascontent,padding=10,width=self.page.width*0.88,)],scroll=ft.ScrollMode.ADAPTIVE,
                            width=self.page.width*0.88,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                width=self.page.width,
                height=self.page.height,
            )