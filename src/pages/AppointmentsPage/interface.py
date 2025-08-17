from datetime import datetime
import flet as ft

from src.pages.HomePage.interface import HomePage
from src.utils.telaresize import Responsive
from src.functions.funcs import listar_empresas_com_agendamento,verempresa
from src.database.databasecache import ContabilidadeDB
from src.database.models import Agendamentos


class AppointmentPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = ContabilidadeDB()
        self.responsive = Responsive(page)
        self.main = HomePage(page)
        self.agendamentos = listar_empresas_com_agendamento()
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
            alignment=ft.alignment.top_center,
            expand=True,
            border_radius=15
        )

        self.btn_novo_agendamento = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            text="Novo Agendamento",
            bgcolor="#A1FB8B",
            on_click=self.abrir_formulario_agendamento
        )


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
        agendamento.data_exame = datetime.strptime(self.data_input.value, "%d/%m/%Y")
        agendamento.tipo_exame = self.tipo_input.value
        agendamento.colaborador = self.colaborador_input.value

        if datetime.strptime(self.data_input.value,"%d/%m/%Y").date() < datetime.now().date():
            self.snack_bar = ft.SnackBar(ft.Text("Data não pode ser inferior á atual!"),bgcolor=ft.Colors.RED)
            self.page.open(self.snack_bar)
            self.page.update()
            self.fechar_dialog()
            return
        
        with self.db.session() as session:
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


    def acao_editar(self, index):
        self.abrir_editar_agendamento(index)

    def fechar_dialog(self):
        self.dialog_agendar.open = False
        self.page.update()

    def build_table(self, linhas):
        columns = [
            ft.DataColumn(ft.Text("Colaborador")),
            ft.DataColumn(ft.Text("Empresa",width=300)),
            ft.DataColumn(ft.Text("Exame")),
            ft.DataColumn(ft.Text("Data do Agendamento")),
            ft.DataColumn(ft.Text("Ações"),heading_row_alignment=ft.MainAxisAlignment.CENTER)  
                ]
        return ft.Column([
            ft.DataTable(
                border_radius=10,
                columns=columns,
                rows=linhas,
                column_spacing=100,
                heading_row_color="#A1FB8B",
                data_row_color=ft.Colors.WHITE,
                heading_text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
                expand=True
                
            )
        ], scroll=ft.ScrollMode.ADAPTIVE)

    def gerar_linhas(self, dados):
        linhas = []

        def editar_agendamento(index):
            def abrir_popup(e):
                self.acao_editar(index)
            return abrir_popup


        for i, agendamento in enumerate(dados):
            linha = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(getattr(agendamento, 'colaborador' ''),size=13)),
                    ft.DataCell(ft.Text(getattr(agendamento, 'nome_empresa', str(agendamento)), size=11)),
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
                        ], spacing=5,vertical_alignment=ft.CrossAxisAlignment.CENTER,alignment=ft.MainAxisAlignment.CENTER)
                    )
                ]
            )
            linhas.append(linha)
        return linhas
    def excluir_direto(self, agendamento):
        with self.db.session() as session:
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
                if termo in ag.colaborador.lower()
            ]

        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(filtradas))
        self.tab_agendamentos.update()

    def build_content(self):
        titulo = ft.Text("Agendamentos", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)
        buscar = self.buscar

        self.tab_agendamentos.content = self.build_table(self.gerar_linhas(self.agendamentos))

        conteudo = ft.Column([
            ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.btn_novo_agendamento], alignment=ft.MainAxisAlignment.END),
            ft.Column([
                buscar,
                self.tab_agendamentos,   
            ],expand=True)
        ], expand=True)

        if self.responsive.is_desktop():
            return conteudo


    def salvar_agendamento(self, e):
        empresa_nome = self.empresa_dropdown.value
        data_exame = self.data_input.value
        tipo_exame = self.tipo_input.value
        colaborador = self.colaborador_input.value
        if not empresa_nome or not data_exame or not tipo_exame or not colaborador:
            self.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"),bgcolor=ft.Colors.RED)
            self.page.open(self.snack_bar)
            self.page.update()
            return
        if datetime.strptime(data_exame,"%d/%m/%Y").date() < datetime.now().date():
            self.snack_bar = ft.SnackBar(ft.Text("Data não pode ser inferior á atual!"),bgcolor=ft.Colors.RED)
            self.page.open(self.snack_bar)
            self.page.update()
            self.fechar_dialog()
            return
        with self.db.session() as session:
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
