from database.models import Agendamentos
from datetime import datetime
from funcoes import db
import flet as ft
from Interfaces.sidebar import Sidebar
from Interfaces.main_interface import Main_interface
from Interfaces.telaresize import Responsive
from funcoes import listar_empresas_com_agendamento
from funcoes import verempresa
from database.databasecache import ContabilidadeDB
class Agendamento:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.clean()
        self.responsive = Responsive(page)
        self.sidebar = Sidebar(page)
        self.main = Main_interface(page)
        self.agendamentos = listar_empresas_com_agendamento()
        self.page.on_resized = self.on_resize
        self.linhas = self.gerar_linhas(self.agendamentos)
        self.tabela = self.build_table(self.linhas)
        self.page.controls.append(self.tabela)
        self.page.update()
        
        # Campos
        self.buscar = ft.TextField(
            label="Buscar empresa",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.acao_pesquisar,
            border_radius=16,
            width=300
        )

        # Tabela de agendamentos
        self.tab_agendamentos = ft.Container(
            content=self.build_table(self.gerar_linhas(self.agendamentos)),
            border_radius=10,
            alignment=ft.alignment.top_center,
            expand=True,
            adaptive=True
        )

        # Botão flutuante
        self.btn_novo_agendamento = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            text="Novo Agendamento",
            bgcolor="#A1FB8B",
            on_click=self.abrir_formulario_agendamento
        )

        self.mostrar()
    
    
    def formatar_data(self, e):
        texto = self.data_input.value
        numeros = ''.join(filter(str.isdigit, texto))  

        if len(numeros) > 8:
            numeros = numeros[:8]

        
        if len(numeros) >= 5:
            formatado = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
        elif len(numeros) >= 3:
            formatado = f"{numeros[:2]}/{numeros[2:]}"
        else:
            formatado = numeros

        self.data_input.value = formatado
        self.page.update()
    
    def mostrar(self):
        self.page.controls.clear()
        self.page.add(self.build_view())
        self.page.update()
    
    def on_resize(self, e):
        if self.page.route == "/agendamentos":
            self.responsive = Responsive(self.page)
            self.responsive.atualizar_widgets(self.build_view())

    def abrir_formulario_agendamento(self, e):
         
        empresas = verempresa()

        self.empresa_dropdown = ft.Dropdown(
            label="Empresa",
            options=[
                ft.dropdown.Option(f"{empresa[0]}") for empresa in empresas
            ],
            autofocus=True,
            width=400
        )

        
        self.colaborador_input = ft.TextField(
            label="Nome do Colaborador",
            width=400
        )

        self.data_input = ft.TextField(
            label="Data do Exame",
            hint_text="dd/mm/aaaa",
            width=200,
            on_change=self.formatar_data
        )


        self.tipo_input = ft.TextField(
            label="Tipo de Exame",
            width=300
        )

        self.dialog_agendar = ft.AlertDialog(
            title=ft.Text("Novo Agendamento"),
            content=ft.Column([
                self.empresa_dropdown,
                self.data_input,
                self.tipo_input,
                self.colaborador_input
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog()),
                ft.TextButton("Agendar", on_click=self.salvar_agendamento)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.open(self.dialog_agendar)


    
    
    def fechar_dialog(self):
        self.dialog_agendar.open = False
        self.page.update()

    def build_table(self, linhas):
        columns = [
            ft.DataColumn(ft.Text("Empresa")),
            ft.DataColumn(ft.Text("Exame")),
            ft.DataColumn(ft.Text("Data do Agendamento")),
            ft.DataColumn(ft.Text("Ações")),
        ]
        return ft.Column([
            ft.DataTable(
                columns=columns,
                rows=linhas,
                column_spacing=90,
                heading_row_color="#A1FB8B",
                data_row_color=ft.Colors.WHITE,
                heading_text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                border_radius=10
            )
        ], scroll=ft.ScrollMode.ADAPTIVE)

    def gerar_linhas(self, dados):
        linhas = []
        print("Gerando linhas para dados:", dados)
        for i, agendamento in enumerate(dados):
            print(f"Item {i}:", agendamento)
            linha = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(getattr(agendamento, 'nome_empresa', str(agendamento)), size=13)),
                    ft.DataCell(ft.Text(getattr(agendamento, 'tipo_exame', ''), size=13)),
                    ft.DataCell(ft.Text(
                                agendamento.data_exame.strftime("%d/%m/%Y") if agendamento.data_exame else "",
                                size=13)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Editar",
                                on_click=lambda e, index=i: self.acao_editar(index)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Excluir",
                                on_click=lambda e: self.confirmar_exclusao(agendamento),
                            )
                        ], spacing=5)
                    )
                ]
            )
            linhas.append(linha)
        print(f"{len(linhas)} linhas geradas")
        return linhas


    def acao_pesquisar(self, e):
        termo = self.buscar.value.strip().lower()
        if not termo:
            filtradas = self.agendamentos
        else:
            filtradas = [
                ag for ag in self.agendamentos
                if termo in ag.nome_exame.lower()
            ]

        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(filtradas))
        self.tab_agendamentos.update()

    def build_view(self):
        titulo = ft.Text("Agendamentos", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)
        buscar = self.buscar

        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))

        conteudo = ft.Column([
            ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_novo_agendamento], alignment=ft.MainAxisAlignment.END),
            ft.Column([
                buscar,
            ft.Container(
                    content=self.tab_agendamentos,
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    expand=True
                )
            ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        ], expand=True)


        if self.responsive.is_desktop():
            return ft.Row([
                ft.Column([self.sidebar.build()], expand=False),
                conteudo
            ], expand=True)

        return ft.Column([
            self.sidebar.build(),
            ft.Row([titulo, self.btn_novo_agendamento], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.buscar,
            ft.Container(
                content=self.tab_agendamentos,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10
            )
        ], scroll=ft.ScrollMode.ADAPTIVE)
    


    def salvar_agendamento(self, e):
        empresa_nome = self.empresa_dropdown.value
        data_exame = self.data_input.value
        tipo_exame = self.tipo_input.value
        colaborador = self.colaborador_input.value

        if not empresa_nome or not data_exame or not tipo_exame or not colaborador:
            self.page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        
        with db.session() as session:
            novo_agendamento = Agendamentos(
                nome_empresa=empresa_nome,
                data_exame=datetime.strptime(data_exame, "%d/%m/%Y"),
                tipo_exame=tipo_exame,
                colaborador=colaborador
            )
            session.add(novo_agendamento)
            session.commit()

        print(f"✅ Agendamento salvo: {empresa_nome} - {data_exame} - {tipo_exame} - {colaborador}")

        self.fechar_dialog()
        self.agendamentos = listar_empresas_com_agendamento()
        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))
        self.page.update()
import datetime
from funcoes import db
import flet as ft
from Interfaces.sidebar import Sidebar
from Interfaces.main_interface import Main_interface
from Interfaces.telaresize import Responsive
from funcoes import listar_empresas_com_agendamento
from funcoes import verempresa
from database.databasecache import ContabilidadeDB

class Agendamento:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.clean()
        self.responsive = Responsive(page)
        self.sidebar = Sidebar(page)
        self.main = Main_interface(page)
        self.agendamentos = listar_empresas_com_agendamento()
        self.page.on_resized = self.on_resize
        self.linhas = self.gerar_linhas(self.agendamentos)
        self.tabela = self.build_table(self.linhas)
        self.page.controls.append(self.tabela)
        self.page.update()

        self.buscar = ft.TextField(
            label="Buscar empresa",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.acao_pesquisar,
            border_radius=16,
            width=300
        )

        self.tab_agendamentos = ft.Container(
            content=self.build_table(self.gerar_linhas(self.agendamentos)),
            border_radius=10,
            alignment=ft.alignment.top_center,
            expand=True,
            adaptive=True
        )

        self.btn_novo_agendamento = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            text="Novo Agendamento",
            bgcolor="#A1FB8B",
            on_click=self.abrir_formulario_agendamento
        )

        self.mostrar()

    def formatar_data(self, e):
        texto = self.data_input.value
        numeros = ''.join(filter(str.isdigit, texto))  
        if len(numeros) > 8:
            numeros = numeros[:8]
        if len(numeros) >= 5:
            formatado = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
        elif len(numeros) >= 3:
            formatado = f"{numeros[:2]}/{numeros[2:]}"
        else:
            formatado = numeros
        self.data_input.value = formatado
        self.page.update()

    def mostrar(self):
        self.page.controls.clear()
        self.page.add(self.build_view())
        self.page.update()

    def on_resize(self, e):
        if self.page.route == "/agendamentos":
            self.responsive = Responsive(self.page)
            self.responsive.atualizar_widgets(self.build_view())

    def abrir_formulario_agendamento(self, e):
        empresas = verempresa()
        self.empresa_dropdown = ft.Dropdown(
            label="Empresa",
            options=[
                ft.dropdown.Option(f"{empresa[0]}") for empresa in empresas
            ],
            autofocus=True,
            width=400
        )

        self.colaborador_input = ft.TextField(
            label="Nome do Colaborador",
            width=400
        )

        self.data_input = ft.TextField(
            label="Data do Exame",
            hint_text="dd/mm/aaaa",
            width=200,
            on_change=self.formatar_data
        )

        self.tipo_input = ft.TextField(
            label="Tipo de Exame",
            width=300
        )

        self.dialog_agendar = ft.AlertDialog(
            title=ft.Text("Novo Agendamento"),
            content=ft.Column([
                self.empresa_dropdown,
                self.data_input,
                self.tipo_input,
                self.colaborador_input
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog()),
                ft.TextButton("Agendar", on_click=self.salvar_agendamento)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.open(self.dialog_agendar)

    def abrir_editar_agendamento(self, index):
        agendamento = self.agendamentos[index]

        self.empresa_dropdown = ft.Dropdown(
            label="Empresa",
            value=agendamento.nome_empresa,
            options=[ft.dropdown.Option(agendamento.nome_empresa)],
            width=400
        )
        self.data_input = ft.TextField(
            label="Data do Exame",
            value=agendamento.data_exame.strftime("%d/%m/%Y") if agendamento.data_exame else "",
            hint_text="dd/mm/aaaa",
            width=200,
            on_change=self.formatar_data
        )
        self.tipo_input = ft.TextField(
            label="Tipo de Exame",
            value=agendamento.tipo_exame,
            width=300
        )
        self.colaborador_input = ft.TextField(
            label="Nome do Colaborador",
            value=agendamento.colaborador,
            width=400
        )

        self.dialog_agendar = ft.AlertDialog(
            title=ft.Text("Editar Agendamento"),
            content=ft.Column([
                self.empresa_dropdown,
                self.data_input,
                self.tipo_input,
                self.colaborador_input
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog()),
                ft.TextButton("Salvar", on_click=lambda e: self.salvar_agendamento_editado(index))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.open(self.dialog_agendar)

    def salvar_agendamento_editado(self, index):
        agendamento = self.agendamentos[index]
        agendamento.nome_empresa = self.empresa_dropdown.value
        agendamento.data_exame = datetime.datetime.strptime(self.data_input.value, "%d/%m/%Y")
        agendamento.tipo_exame = self.tipo_input.value
        agendamento.colaborador = self.colaborador_input.value

        from database.models import Agendamentos
        with db.session() as session:
            ag = session.query(Agendamentos).filter_by(id=agendamento.id).first()
            if ag:
                ag.nome_empresa = agendamento.nome_empresa
                ag.data_exame = agendamento.data_exame
                ag.tipo_exame = agendamento.tipo_exame
                ag.colaborador = agendamento.colaborador
                session.commit()

        self.fechar_dialog()
        self.agendamentos = listar_empresas_com_agendamento()
        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))
        self.page.update()

    def acao_excluir(self, index):
        from database.models import Agendamentos
        agendamento = self.agendamentos[index]

    def confirmar_exclusao(self, agendamento):
        def excluir(e):
            try:
                from database.models import Agendamentos
                with db.session() as session:
                    session.query(Agendamentos).filter_by(id=agendamento.id).delete()
                    session.commit()
                self.fechar_dialog()  # Usa seu método existente
                self.agendamentos = listar_empresas_com_agendamento()
                self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))

                # Feedback visual
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("✅ Agendamento excluído com sucesso!"),
                    bgcolor=ft.Colors.GREEN_400
                )
                self.page.snack_bar.open = True
                self.page.update()
            
            except Exception as e:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"❌ Erro ao excluir: {str(e)}"),
                    bgcolor=ft.Colors.RED_400
                )
                self.page.snack_bar.open = True
                self.page.update()
                #dialog de confirmação
                self.page.dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Exclusão",weight=ft.FontWeight.BOLD),
                    content=ft.Text(f"Execluir agendamento de {agendamento.nome_empresa} {agendamento.tipo_exame}?"),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog()),
                        ft.TextButton(
                            "Confirmar",
                            on_click=excluir,
                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED)
                        )
                            
                    ]
                )
                self.page.dialog.open = True
                self.page.update()
                    
                
        

    def acao_editar(self, index):
        self.abrir_editar_agendamento(index)

    def fechar_dialog(self):
        self.dialog_agendar.open = False
        self.page.update()

    def build_table(self, linhas):
        columns = [
            ft.DataColumn(ft.Text("Empresa")),
            ft.DataColumn(ft.Text("Exame")),
            ft.DataColumn(ft.Text("Data do Agendamento")),
            ft.DataColumn(ft.Text("Ações")),
        ]
        return ft.Column([
            ft.DataTable(
                columns=columns,
                rows=linhas,
                column_spacing=260,
                heading_row_color="#A1FB8B",
                data_row_color=ft.Colors.WHITE,
                heading_text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                border_radius=300
            )
        ], scroll=ft.ScrollMode.ADAPTIVE)

    def gerar_linhas(self, dados):
        linhas = []

        def editar_agendamento(index):
            def abrir_popup(e):
                self.acao_editar(index)
            return abrir_popup

        def excluir_agendamento(index, agendamento):
            def abrir_popup(e):
                self.page.dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Exclusão", size=16, weight="bold"),
                    content=ft.Text(f"Tem certeza que deseja excluir o agendamento de\n{agendamento.nome_empresa} - {agendamento.tipo_exame}?"),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda _: self.fechar_dialogo()),
                        ft.TextButton(
                            "Excluir",
                            style=ft.ButtonStyle(color="white", bgcolor="red"),
                            on_click=lambda _: self.acao_excluir(index)
                        )
                    ],
                    actions_alignment="end"
                )
                self.page.dialog.open = True
                self.page.update()
            return abrir_popup

        for i, agendamento in enumerate(dados):
            linha = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(getattr(agendamento, 'nome_empresa', str(agendamento)), size=13)),
                    ft.DataCell(ft.Text(getattr(agendamento, 'tipo_exame', ''), size=13)),
                    ft.DataCell(ft.Text(
                        agendamento.data_exame.strftime("%d/%m/%Y") if agendamento.data_exame else "",
                        size=13)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Editar",
                                on_click=editar_agendamento(i)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Excluir",
                                on_click=lambda e, ag=agendamento: self.excluir_direto(ag)
                            )
                        ], spacing=5)
                    )
                ]
            )
            linhas.append(linha)
        return linhas
    def excluir_direto(self, agendamento):
        from database.models import Agendamentos
        with db.session() as session:
            session.query(Agendamentos).filter_by(id=agendamento.id).delete()
            session.commit()
        self.agendamentos = listar_empresas_com_agendamento()
        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))
        self.page.update()

    
    def acao_pesquisar(self, e):
        termo = self.buscar.value.strip().lower()
        if not termo:
            filtradas = self.agendamentos
        else:
            filtradas = [
                ag for ag in self.agendamentos
                if termo in ag.nome_exame.lower()
            ]

        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(filtradas))
        self.tab_agendamentos.update()

    def build_view(self):
        titulo = ft.Text("Agendamentos", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)
        buscar = self.buscar

        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))

        conteudo = ft.Column([
            ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_novo_agendamento], alignment=ft.MainAxisAlignment.END),
            ft.Column([
                buscar,
            ft.Container(
                    content=self.tab_agendamentos,
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    expand=True
                )
            ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        ], expand=True)

        if self.responsive.is_desktop():
            return ft.Row([
                ft.Column([self.sidebar.build()], expand=False),
                conteudo
            ], expand=True)

        return ft.Column([
            self.sidebar.build(),
            ft.Row([titulo, self.btn_novo_agendamento], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.buscar,
            ft.Container(
                content=self.tab_agendamentos,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10
            )
        ], scroll=ft.ScrollMode.ADAPTIVE)

    def salvar_agendamento(self, e):
        empresa_nome = self.empresa_dropdown.value
        data_exame = self.data_input.value
        tipo_exame = self.tipo_input.value
        colaborador = self.colaborador_input.value

        if not empresa_nome or not data_exame or not tipo_exame or not colaborador:
            self.page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        from database.models import Agendamentos
        from datetime import datetime
        with db.session() as session:
            novo_agendamento = Agendamentos(
                nome_empresa=empresa_nome,
                data_exame=datetime.strptime(data_exame, "%d/%m/%Y"),
                tipo_exame=tipo_exame,
                colaborador=colaborador
            )
            session.add(novo_agendamento)
            session.commit()

        self.fechar_dialog()
        self.agendamentos = listar_empresas_com_agendamento()
        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))
        self.page.update()
