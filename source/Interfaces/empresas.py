import flet as ft
from funcoes import verempresa, cadasempresa, excluiremp
from Interfaces.telaresize import Responsive
from Interfaces.sidebar import Sidebar
from Interfaces.main_interface import Main_interface
from funcoes import atualizarempresa

class Empresas:
    def __init__(self, page: ft.Page):
        self.page = page
        self.responsive = Responsive(self.page)
        self.page.clean()
        self.dados = verempresa()
        self.page.on_resized = self.on_resize
        """ Controles """
        self.razao = ft.TextField(
            label="Razão Social",
            border_radius=30,
            focused_border_color="#74FE4E",
            label_style=ft.TextStyle(color=ft.Colors.GREY_800)
        )
        self.cnpj = ft.TextField(
            label="CNPJ",
            border_radius=10,
            focused_border_color="#74FE4E",
            label_style=ft.TextStyle(color=ft.Colors.GREY_800)
        )
        self.contato = ft.TextField(
            label="Contato",
            border_radius=10,
            focused_border_color="#74FE4E",
            label_style=ft.TextStyle(color=ft.Colors.GREY_800)
        )
        self.endereco = ft.TextField(
            label="Endereço",
            border_radius=10,
            focused_border_color="#74FE4E",
            label_style=ft.TextStyle(color=ft.Colors.GREY_800)
        )
        self.municipio = ft.TextField(
            label="Município",
            border_radius=10,
            focused_border_color="#74FE4E",
            label_style=ft.TextStyle(color=ft.Colors.GREY_800)
        )
        self.caixadebusca = ft.TextField(
            label="Buscar",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.atualizar_tabela,
            border_radius=16,
            width=300
        )
        self.tabempresas = ft.Container(
            content=self.buildtableE(self.gerarlinhas(self.dados)),
            border_radius=10,
            alignment=ft.alignment.top_center,
            expand=True,
            adaptive=True
        )
        self.register_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            text="Cadastrar Empresa",
            on_click=self.abrir_dialog_cadastro,
            bgcolor="#A1FB8B",
        )

    def on_resize(self, e):
        if self.page.route == "/empresas":
            self.responsive = Responsive(self.page)
            self.responsive.atualizar_widgets(self.build_view())

    def cadastro(self, e):
        try:
            if self.razao.value and self.cnpj.value and self.contato.value and self.endereco.value and self.municipio.value:
                cadasempresa(
                    self.razao.value,
                    self.cnpj.value,
                    self.contato.value,
                    self.endereco.value,
                    self.municipio.value
                )
                self.dados = verempresa()
                self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
                self.tabempresas.update()
                self.dialog_cadastro.open = False
                self.page.update()
                self.mostrar_snackbar("Empresa cadastrada com sucesso!")
                return
            self.mostrar_snackbar(f"Preencha todos os campos!", ft.Colors.RED)
            self.page.close(self.dialog_cadastro)
            self.page.update()
        except Exception as e:
            self.mostrar_snackbar(f"Erro ao cadastrar: {str(e)}", ft.Colors.RED)

    def abrir_dialog_cadastro(self, e):
        self.razao.value = ""
        self.cnpj.value = ""
        self.contato.value = ""
        self.endereco.value = ""
        self.municipio.value = ""
        textfields = [
            self.razao, self.cnpj, self.contato, self.endereco, self.municipio
        ]
        for campo in textfields:
            campo.height = 50
            campo.border_radius = 16
            campo.filled = True
            campo.fill_color = ft.Colors.GREY_100
            campo.border_color = ft.Colors.GREY_300
            campo.focused_border_color = "#74FE4E"

        self.dialog_cadastro = ft.AlertDialog(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            title=ft.Text(
            "Cadastrar Nova Empresa",
            size=22,
            weight=ft.FontWeight.BOLD
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    self.razao,
                    self.cnpj,
                    self.contato,
                    self.endereco,
                    self.municipio,
                ],
                tight=True,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=400,  # 👈 aumenta a largura
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        ),
        actions=[
            ft.ElevatedButton(
                "Cancelar",
                on_click=self.fechar_dialog_cadastro,
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_900
            ),
            ft.ElevatedButton(
                "Salvar",
                on_click=self.cadastro,
                bgcolor="#74FE4E",
                color=ft.Colors.BLACK
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=20),
        inset_padding=ft.padding.all(20),
    )

        self.page.open(self.dialog_cadastro)
        self.page.update()

    def fechar_dialog_cadastro(self, e):
        self.dialog_cadastro.open = False
        self.page.update()

    def abrir_dialog_edicao(self, index):
        empresa = self.dados[index]
        
        self.razao.value = empresa[0]
        self.cnpj.value = empresa[1]    
        self.contato.value = empresa[2]
        self.endereco.value = empresa[3]
        self.municipio.value = empresa[4]

        for campo in [self.razao, self.cnpj, self.contato, self.endereco, self.municipio]:
            campo.height = 50
            campo.border_radius = 16
            campo.filled = True
            campo.fill_color = ft.Colors.GREY_100
            campo.border_color = ft.Colors.GREY_300
            campo.focused_border_color = "#74FE4E"
        
        self.dialog_edicao = ft.AlertDialog(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            title=ft.Text(
                f"Editar Empresa:",
                size=15,
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(  
            width=400,         
            content=ft.Column(
                controls=[
                    self.razao,
                    self.cnpj,
                    self.contato,
                    self.endereco,
                    self.municipio,
                ],
                tight=True,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            )
        ),
        actions=[
            ft.ElevatedButton(
                "Cancelar",
                on_click=self.fechar_dialog_edicao,
                bgcolor=ft.Colors.RED_100,
                color=ft.Colors.RED_900
            ),
            ft.ElevatedButton(
                "Salvar",
                on_click=lambda e: self.salvar_edicao(e, index),
                bgcolor="#74FE4E",
                color=ft.Colors.BLACK
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=20),
        inset_padding=20,
    )
        self.page.open(self.dialog_edicao)
        self.page.update()

    def salvar_edicao(self, e, index):
        try:
            cnpj_original = self.dados[index][1]  

            atualizarempresa(cnpj_original, "razao", self.razao.value)
            atualizarempresa(cnpj_original, "contato", self.contato.value)
            atualizarempresa(cnpj_original, "endereco", self.endereco.value)
            atualizarempresa(cnpj_original, "municipio", self.municipio.value)

            self.dados = verempresa()
            self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
            self.tabempresas.update()
            self.fechar_dialog_edicao(None)
            self.mostrar_snackbar("Empresa atualizada com sucesso!")
        except Exception as e:
            self.mostrar_snackbar(f"Erro ao atualizar: {str(e)}", ft.Colors.RED)

    def fechar_dialog_edicao(self, e):
        self.dialog_edicao.open = False
        self.page.update()

    def apagaremp(self, index):
        try:
            ex = self.dados[index]
            excluiremp(ex[1])
            self.dados = verempresa()
            self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
            self.tabempresas.update()
            self.mostrar_snackbar("Empresa excluída com sucesso!")
        except Exception as e:
            self.mostrar_snackbar(f"Erro ao excluir: {str(e)}", ft.Colors.RED)

    def mostrar_snackbar(self, mensagem, cor=ft.Colors.GREEN):
        self.snack_bar = ft.SnackBar(ft.Text(mensagem),bgcolor=cor)
        self.page.open(self.snack_bar)

    def buildtableE(self, linhas):
        if self.responsive.is_mobile():
            columns = [
                ft.DataColumn(ft.Text("Razão Social", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("CNPJ", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Ações", text_align=ft.TextAlign.CENTER)),
            ]
        else:
            columns = [
                ft.DataColumn(ft.Text("Razão Social", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("CNPJ", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Contato", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Endereço", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Município", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Ações", text_align=ft.TextAlign.CENTER)),
            ]
        return ft.Column([ft.DataTable(

            heading_row_color="#A1FB8B",
            horizontal_lines=ft.BorderSide(1),
            data_row_color=ft.Colors.WHITE,
            divider_thickness=1,
            heading_text_style=ft.TextStyle(
                size=15 if self.responsive.is_mobile() else 20,
                weight=ft.FontWeight.BOLD,
                font_family="Arial"
            ),
            columns=columns,
            column_spacing=100,
            rows=linhas,
            border_radius=10,
            sort_ascending=True
        )
        ],scroll=ft.ScrollMode.AUTO)

        

    def gerarlinhas(self, data):
        linhas = []
        for i, empresa in enumerate(data):
            if self.responsive.is_mobile():
                cells = [
                    ft.DataCell(ft.Text(empresa[0])),
                    ft.DataCell(ft.Text(empresa[1])),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, idx=i: self.abrir_dialog_edicao(idx)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, idx=i: self.apagaremp(idx)
                            )
                        ], spacing=5)
                    )
                ]
            else:
                cells = [
                    ft.DataCell(ft.Text(empresa[0].upper(),size=11)),
                    ft.DataCell(ft.Text(empresa[1],size=11)),
                    ft.DataCell(ft.Text(empresa[2],size=11)),
                    ft.DataCell(ft.Text(empresa[3].upper(),size=11)),
                    ft.DataCell(ft.Text(empresa[4].upper(),size=11)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, idx=i: self.abrir_dialog_edicao(idx)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, idx=i: self.apagaremp(idx)
                            )
                        ], spacing=5)
                    )
                ]
            
            linhas.append(ft.DataRow(cells=cells))
        return linhas

    def atualizar_tabela(self, e):
        termo_busca = str(self.caixadebusca.value).lower()
        if not termo_busca:
            self.dados = verempresa()
        else:
            self.dados = [
                emp for emp in verempresa()
                if (termo_busca in (emp[0] or "").lower()) or
                   (termo_busca in (emp[1] or "").lower()) or
                   (termo_busca in (emp[2] or "").lower()) or
                   (termo_busca in (emp[3] or "").lower())
            ]
        
        self.tabempresas.content = self.buildtableE(self.gerarlinhas(self.dados))
        self.tabempresas.update()

    def build_view(self):
        self.main = Main_interface(self.page)
        self.sidebar = Sidebar(self.page)
        
        if self.responsive.is_desktop():
            return ft.Row(
                [
                    ft.Column([self.sidebar.build()], alignment=ft.MainAxisAlignment.START),
                    ft.Column(
                        [
                            ft.Row([ft.Text("Empresas", size=30, color=ft.Colors.GREY_800)], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row(
                                [
                                    self.register_button
                                ],
                                alignment=ft.MainAxisAlignment.END
                            ),
                            ft.Column([self.caixadebusca,self.tabempresas],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.MainAxisAlignment.CENTER,expand=True,scroll=ft.ScrollMode.ADAPTIVE)
                        ],expand=True              
                    )
                ],expand=True
                
            )
        
        elif self.responsive.is_mobile():
            return ft.Column(
                [
                    self.sidebar.build(),
                    ft.Row(
                        [
                            ft.Text("Empresas", size=25),
                            self.register_button
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    self.caixadebusca,
                    self.tabempresas
                ],
                scroll=ft.ScrollMode.ADAPTIVE
            )
        
        elif self.responsive.is_tablet():
            return ft.Column(
                [
                    self.sidebar.build(),
                    ft.Row(
                        [
                            ft.Text("Empresas", size=28),
                            self.register_button
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    self.caixadebusca,
                    self.tabempresas
                ],
                scroll=ft.ScrollMode.ADAPTIVE
            )
