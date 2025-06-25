from funcoes import (inserirdiario,vercontas,inserircontas,excluirconta,retirardiario)
from decimal import Decimal
from database.databasecache import diccreate
from Interfaces.main_interface import Main_interface
import locale
import flet as ft
from Interfaces.sidebar import Sidebar
from Interfaces.telaresize import Responsive

class ContabilidadePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.responsive = Responsive(self.page)
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.diario = 0.0
        self.mensal = 0.0
        self.contas = 0.0
        self.selected_chip = None
        self.dados = vercontas()
        self.main_interface_instance = Main_interface(page) # Keep this for cardmain and cardfloat

    def build_view(self):
        if self.responsive.is_desktop():
            async def diccreate_force():
                return await diccreate(force_update=True)
            def selected(e: ft.ControlEvent):
                self.clicked = e.control
                if self.selected_chip and self.selected_chip != self.clicked:
                    self.selected_chip.selected = False
                self.clicked.selected = True
                self.selected_chip = self.clicked
                self.page.update()
            def on_diccreate_done(future):
                dadosapi = future.result()
                self.diario = dadosapi['diario'] if dadosapi else 0.0
                self.mensal = dadosapi['mensal'] if dadosapi else 0.0
                self.contas = dadosapi['contas'] if dadosapi else 0.0
                self.cardcontainer.content = self.buildcards(self.diario,self.mensal,self.contas)
                self.cardcontainer.update()
                self.page.update()
            async def retirarpg(e):
                def on_update_done(future):
                    dadosapi = future.result()
                    diario = dadosapi['diario'] if dadosapi else 0.0
                    mensal = dadosapi['mensal'] if dadosapi else 0.0
                    contas = dadosapi['contas'] if dadosapi else 0.0
                    self.cardcontainer.content = self.buildcards(diario, mensal, contas)
                    self.cardcontainer.update()
                    self.page.update()
                saida = str(self.valoresRetiro.value)
                saida = saida.replace(",",".")
                saida = Decimal(saida)
                motivoSaida = self.motivo.value
                forma_pagamento = self.selected_chip.label.value if self.selected_chip else "Nenhuma"
                if saida and motivoSaida:
                    retirardiario(saida, motivoSaida)
                    future = self.page.run_task(diccreate_force)
                    future.add_done_callback(on_update_done)
                    self.valoresRetiro.value = ""
                    self.motivo.value = ""
                    self.valoresRetiro.update()
                    self.motivo.update()
                else:
                    snack = ft.SnackBar(content=ft.Text("Preencha todos os campos"))
                    snack.open = True
                    self.page.open(snack)
            async def registrarpg(e):
                entrada = str(self.valores.value)
                entrada = entrada.replace(",",".")
                entrada = Decimal(entrada)
                servico = self.servico.value
                forma_pagamento = self.selected_chip.label.value if self.selected_chip else "Nenhuma"
                if entrada and servico:
                    inserirdiario(entrada, servico)
                    dadosapi = await diccreate(force_update=True)
                    self.diario = dadosapi['diario'] if dadosapi else 0.0
                    self.mensal = dadosapi['mensal'] if dadosapi else 0.0
                    self.contas = dadosapi['contas'] if dadosapi else 0.0
                    self.cardcontainer.content = self.buildcards(self.diario, self.mensal, self.contas)
                    self.cardcontainer.update()
                    self.valores.value = ""
                    self.servico.value = ""
                    self.valores.update()
                    self.servico.update()
                else:
                    pass
            self.valores = ft.TextField(label="Valor",prefix_text="R$",width=200, height=35, border_radius=10,
                                input_filter=ft.InputFilter(regex_string=r'[0-9,.]*', replacement_string=""),
                                keyboard_type=ft.KeyboardType.NUMBER,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.MONETIZATION_ON)
            self.servico = ft.TextField(label="Serviço",width=200, height=35, border_radius=10
                                ,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.TEXT_SNIPPET)
            self.chipPix = ft.Chip(label=ft.Text("Pix"),on_select=selected)
            self.chipMoney = ft.Chip(label=ft.Text("Dinheiro"),on_select=selected)
            self.valoresRetiro = ft.TextField(label="Valor",prefix_text="R$",width=200, height=35, border_radius=10,
                                input_filter=ft.InputFilter(regex_string=r'[0-9,.]*', replacement_string=""),
                                keyboard_type=ft.KeyboardType.NUMBER,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.MONETIZATION_ON)
            self.motivo = ft.TextField(label="Motivo e Quem",width=200, height=35, border_radius=10
                                ,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.TEXT_SNIPPET)
            self.linhas = [
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(conta[0])),
                            ft.DataCell(ft.Text(f"R${conta[1]}")),
                            ft.DataCell(ft.Text(conta[2])),
                            ft.DataCell(ft.Text(conta[3])),
                            ft.DataCell(ft.Text(conta[4])),
                            ft.DataCell(ft.IconButton(icon=ft.Icons.CHECK, icon_color=ft.Colors.BLACK,bgcolor=ft.Colors.GREEN_100)),
                            ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.BLACK,bgcolor=ft.Colors.RED_100))

                        ]
                    ) for i, conta in enumerate(self.dados)
                ]
            self.cardcontainer = ft.Container(
                content=self.buildcards(self.diario,self.mensal,self.contas)
            )
            self.tablecontent =ft.Container(
                content=self.buildtable(self.linhas)
            ) 
            self.caixainterface = ft.Column([
                ft.Row([
                    self.valores,self.servico
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),

                ft.Row([
                    ft.Icon(ft.Icons.MONEY, color=ft.Colors.BLACK),
                    ft.Text("Forma de Pagamento:")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                self.chipPix,self.chipMoney
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK),icon_color=ft.Colors.BLACK45,on_click=registrarpg)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)      
            self.retirointerface = ft.Column([
                ft.Row([
                    self.valoresRetiro,self.motivo
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.Icon(ft.Icons.MONEY, color=ft.Colors.BLACK),
                    ft.Text("Forma de saída:")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    self.chipPix, self.chipMoney
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK),icon_color=ft.Colors.BLACK45,on_click=retirarpg)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.contabcontent = ft.Column([
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.MONETIZATION_ON,color=ft.Colors.GREEN),
                                ft.Text("Contabilidade",size=30)
                            ],alignment=ft.MainAxisAlignment.CENTER
                        )
                    ),
                    
                    self.cardcontainer,

                    ft.Container(
                    content=ft.Row([
                        self.main_interface_instance.cardmain("Registro de caixa",None,None,self.caixainterface,False),
                        self.main_interface_instance.cardmain("Registro de saîda",None,None,self.retirointerface,False)
                    ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
                    ft.Container(
                        content=ft.Row([
                            self.main_interface_instance.cardmain("Contabilidade de contas",None,None,self.tablecontent,True)
                        ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            future = self.page.run_task(diccreate_force)
            future.add_done_callback(on_diccreate_done)
            sidebar_instance = Sidebar(self.page)
            return ft.Row(
                [
                    ft.Column([sidebar_instance.build()],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([ft.Container(content=self.contabcontent,padding=10,width=self.page.width*0.88,)],scroll=ft.ScrollMode.ADAPTIVE,
                            width=self.page.width*0.88,expand=True,adaptive=True,alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                width=self.page.width,
                height=self.page.height,
            ) 
    
    def buildcards(self,diario, mensal, contas):
        self.card_diario = self.main_interface_instance.cardfloat(icon=ft.Icons.MONETIZATION_ON_OUTLINED,title="Entrada",value=locale.currency(diario,grouping=True),
                            barra="Entrada de hoje",iconbarra=ft.Icons.ARROW_UPWARD,corbarra=ft.Colors.GREEN,larg=300,color=ft.Colors.BLACK)
        self.card_mensal = self.main_interface_instance.cardfloat(icon=ft.Icons.MONEY,title="Mensal",value=locale.currency(mensal,grouping=True),
                            barra="Receita do mês anterior",iconbarra=ft.Icons.ARROW_UPWARD,corbarra=ft.Colors.GREEN,larg=300,color=ft.Colors.BLACK)
        self.card_contas = self.main_interface_instance.cardfloat(icon=ft.Icons.MONEY_OFF,title="A Pagar",value=locale.currency(contas,grouping=True),
                            barra="Saida de caixa",iconbarra=ft.Icons.ARROW_DOWNWARD,corbarra=ft.Colors.RED,larg=300,color=ft.Colors.RED)
        return ft.Row(
            [
                self.card_diario,
                self.card_contas,
                self.card_mensal,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def buildtable(self,linhas):
        self.contasinterface = ft.Column([
            ft.Row([
                ft.DataTable(
                    column_spacing=40,
                    border_radius=25,
                    expand=True,
                    columns=[
                        ft.DataColumn(ft.Text("Conta"),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                        ft.DataColumn(ft.Text("Valor"),numeric=True),
                        ft.DataColumn(ft.Text("Vencimento")),
                        ft.DataColumn(ft.Text("Pagamento")),
                        ft.DataColumn(ft.Text("Status")),
                        ft.DataColumn(ft.Text("Ações")),
                        ft.DataColumn(ft.Text("Ações")),
                    ],
                    rows=linhas
                )
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.PAYMENTS,text="Registrar Conta",style=ft.ButtonStyle(color=ft.Colors.BLACK),
                                icon_color=ft.Colors.BLACK45)
                ])
        ])
        return self.contasinterface

    def gerar_linhas(self, dataatt):
            return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(conta[0])),
                        ft.DataCell(ft.Text(f"R${conta[1]}")),
                        ft.DataCell(ft.Text(conta[2])),
                        ft.DataCell(ft.Text(conta[3])),
                        ft.DataCell(ft.Text(conta[4])),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.CHECK, icon_color=ft.Colors.BLACK, bgcolor=ft.Colors.GREEN_100)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.BLACK,
                                bgcolor=ft.Colors.RED_100
                            )
                        ),
                    ]
                ) for i, conta in enumerate(dataatt)
            ]


