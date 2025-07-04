import flet as ft
from funcoes import (verempresa, cadasempresa,excluiremp)
from Interfaces.telaresize import Responsive
from Interfaces.main_interface import Main_interface
from Interfaces.sidebar import Sidebar

class Empresas:
        def __init__(self,page: ft.Page):
            self.page = page
            self.responsive = Responsive(self.page)
            self.page.clean()
            self.dados = verempresa()
            self.page.on_resized = self.on_resize

        def on_resize(self,e):
            if self.page.route == "/empresas":
                self.responsive = Responsive(self.page)
                self.responsive.atualizar_widgets(self.build_view())
        
        def limpar(self):
            self.razao.value = ""
            self.cnpj.value = ""
            self.contato.value = ""
            self.endereco.value = ""
            self.razao.update()
            self.cnpj.update()
            self.contato.update()
            self.endereco.update()
        
        def buildtableE(self,linhas):
            if self.responsive.is_mobile():
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
                            ft.DataColumn(ft.Text("Ações",text_align=ft.TextAlign.CENTER)),
                        ],
                        rows=linhas
                        )
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,expand=True
                    )
                    ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,scroll=ft.ScrollMode.AUTO,expand=True
                )
                return empresastb
            else:
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
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,expand=True
                    )
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,scroll=ft.ScrollMode.AUTO,expand=True)
                return empresastb
        
        def gerarlinhas(self,data):
            if self.responsive.is_mobile():
                return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(linhas[0])),
                        ft.DataCell(ft.Text(linhas[1])),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.RED,on_click=lambda e, idx=i: self.apagaremp(idx)))
                    ]
                ) for i, linhas in enumerate(data)
                ]
            else:
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
            self.limpar()
        
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
            if self.responsive.is_desktop():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.razao = ft.TextField(label="Razão Social",border_radius=10,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.cnpj = ft.TextField(label="CNPJ",border_radius=10,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.contato = ft.TextField(label="Contato",border_radius=10,width=300,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.endereco = ft.TextField(label="Endereço",border_radius=10,width=300,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
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
                        ft.TextButton(text="Cadastrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=10,bgcolor="#A1FB8B")
                                    ,icon=ft.Icons.SEND_AND_ARCHIVE,on_click=lambda _: self.cadastro(),width=120),
                        ft.TextButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.BLACK,style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=10,bgcolor=ft.Colors.RED_ACCENT_200)
                                    ,text="Limpar",width=120,on_click=lambda _: self.limpar())           
                        ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=30,)
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                self.empresascontent = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Empresas", size=30,color=ft.Colors.GREY_800,weight=ft.FontWeight.W_400)
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
                return ft.Row(
                    [
                        ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START),
                        ft.Column([ft.Container(content=self.empresascontent,padding=10,width=self.page.width*0.88,)],scroll=ft.ScrollMode.ADAPTIVE,
                                width=self.page.width*0.88,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START)
                    ],
                    width=self.page.width,
                    height=self.page.height,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            elif self.responsive.is_mobile():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.razao = ft.TextField(label="Razão Social",border_radius=10,width=150,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.cnpj = ft.TextField(label="CNPJ",border_radius=10,width=150,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.contato = ft.TextField(label="Contato",border_radius=10,width=150,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.endereco = ft.TextField(label="Endereço",border_radius=10,width=150,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
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
                        ft.TextButton(text="Cadastrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=10,bgcolor="#A1FB8B")
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
                        ft.Column([
                            ft.Text("Procure pela Empresa desejada: "),
                            self.caixadebusca  
                        ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Row([
                            self.main.cardmain("Empresas Cadastradas",None,None,self.tabempresas,True)
                        ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],scroll=ft.ScrollMode.ADAPTIVE,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )
                return ft.Column(
                    [
                        ft.Row([self.sidebar.build()],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([self.empresascontent],scroll=ft.ScrollMode.ADAPTIVE,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ],
                    width=self.page.width,
                    height=self.page.height,
                )
            elif self.responsive.is_tablet():
                self.main = Main_interface(self.page)
                self.sidebar = Sidebar(self.page)
                self.razao = ft.TextField(label="Razão Social",border_radius=10,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.cnpj = ft.TextField(label="CNPJ",border_radius=10,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.contato = ft.TextField(label="Contato",border_radius=10,width=300,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.endereco = ft.TextField(label="Endereço",border_radius=10,width=300,focused_border_color="#74FE4E",label_style=ft.TextStyle(color=ft.Colors.GREY_800))
                self.tabempresas = ft.Container(
                    content=self.buildtableE(self.gerarlinhas(self.dados)),
                    border=ft.Border(top=ft.BorderSide(width=1)),
                    border_radius=16,
                    expand=True
                    )
                self.caixadebusca = ft.TextField(
                    label="Buscar",
                    prefix_icon=ft.Icons.SEARCH,
                    on_change=self.atualizar_tabela,
                    border_radius=16,
                    width=300
                )
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
                        ft.TextButton(text="Cadastrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,elevation=10,bgcolor="#A1FB8B")
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
                            self.main.cardmain("Empresas Cadastradas",None,None,self.tabempresas,True)
                        ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,expand=True
                        )
                    ],scroll=ft.ScrollMode.ADAPTIVE,expand=True),expand=True
                )
                return ft.Column(
                    [
                        ft.Row([self.sidebar.build()],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([self.empresascontent],scroll=ft.ScrollMode.ADAPTIVE,adaptive=True,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,expand=True)
                    ],
                    width=self.page.width,
                    height=self.page.height,
                )