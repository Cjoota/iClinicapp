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
        self.sidebar = Sidebar(self.page)
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
            self.chipPixRetiro = ft.Chip(label=ft.Text("Pix"),on_select=selected)
            self.chipMoneyRetiro = ft.Chip(label=ft.Text("Dinheiro"),on_select=selected)
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
                    self.chipPixRetiro, self.chipMoneyRetiro
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
                                ft.Text("Contabilidade",size=30)
                            ]
                            ,alignment=ft.MainAxisAlignment.START
                        ),margin=ft.Margin(left=10,top=0,right=0,bottom=0)
                    ),
                    self.cardcontainer,
                    ft.Container(
                        content=ft.Row([
                            self.main_interface_instance.cardmain("Registro de caixa",None,None,self.caixainterface,False),
                            self.main_interface_instance.cardmain("Registro de saîda",None,None,self.retirointerface,False)
                        ]
                        ,alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
                    ft.Container(
                        content=self.main_interface_instance.cardmain("Contabilidade de contas",None,None,self.tablecontent,True)
                    ),
            ],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START)
            future = self.page.run_task(diccreate_force)
            future.add_done_callback(on_diccreate_done)
            return ft.Row(
                [
                    ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Container(content=self.contabcontent,expand=True)
                ],
                width=self.page.width,
                height=self.page.height,
                alignment=ft.MainAxisAlignment.START
            ) 
        elif self.responsive.is_tablet():
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
            self.valores = ft.TextField(label="Valor",prefix_text="R$",width=170, height=42, border_radius=10,
                                input_filter=ft.InputFilter(regex_string=r'[0-9,.]*', replacement_string=""),
                                keyboard_type=ft.KeyboardType.NUMBER,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.MONETIZATION_ON)
            self.servico = ft.TextField(label="Serviço",width=170, height=42, border_radius=10
                                ,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.TEXT_SNIPPET)
            self.chipPix = ft.Chip(label=ft.Text("Pix"),on_select=selected)
            self.chipMoney = ft.Chip(label=ft.Text("Dinheiro"),on_select=selected)
            self.chipPixRetiro = ft.Chip(label=ft.Text("Pix"),on_select=selected)
            self.chipMoneyRetiro = ft.Chip(label=ft.Text("Dinheiro"),on_select=selected)
            self.valoresRetiro = ft.TextField(label="Valor",prefix_text="R$",width=170, height=42, border_radius=10,
                                input_filter=ft.InputFilter(regex_string=r'[0-9,.]*', replacement_string=""),
                                keyboard_type=ft.KeyboardType.NUMBER,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.MONETIZATION_ON)
            self.motivo = ft.TextField(label="Motivo",width=170, height=42, border_radius=10
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
                    ft.Text("Forma de Pagamento:")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                self.chipPix,self.chipMoney
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=registrarpg)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2)      
            self.retirointerface = ft.Column([
                ft.Row([
                    self.valoresRetiro,self.motivo
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.Text("Forma de saída:")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    self.chipPixRetiro, self.chipMoneyRetiro
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=retirarpg)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2)
            self.contabcontent = ft.Column([
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Contabilidade",size=30)
                            ]
                            ,alignment=ft.MainAxisAlignment.START
                        ),margin=ft.Margin(left=10,top=0,right=0,bottom=0)
                    ),
                    self.cardcontainer,
                    ft.Container(
                        content=ft.Row([
                            self.main_interface_instance.cardmain("Registro de caixa",None,None,self.caixainterface,True),
                            self.main_interface_instance.cardmain("Registro de saîda",None,None,self.retirointerface,True)
                        ]
                        ,alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
                    ft.Container(
                        content=self.main_interface_instance.cardmain("Contabilidade de contas",None,None,self.tablecontent,True)
                    ),
            ],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START)
            future = self.page.run_task(diccreate_force)
            future.add_done_callback(on_diccreate_done)
            return ft.Column(
                [
                    ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Container(content=self.contabcontent,expand=True)
                ],
                width=self.page.width,
                height=self.page.height+80,
                alignment=ft.MainAxisAlignment.START
            )
        elif self.responsive.is_mobile():
            def BuildTableMobile(linhas):
                self.contasinterface = ft.Column([
                    ft.Row([
                        ft.DataTable(
                            column_spacing=10,
                            expand=True,
                            columns=[
                                ft.DataColumn(ft.Text("Conta"),heading_row_alignment=ft.MainAxisAlignment.START),
                                ft.DataColumn(ft.Text("Valor"),heading_row_alignment=ft.MainAxisAlignment.START),
                                ft.DataColumn(ft.Text("Vencimento"),heading_row_alignment=ft.MainAxisAlignment.START),
                                ft.DataColumn(ft.Text("Ações"),heading_row_alignment=ft.MainAxisAlignment.START),
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
            self.valores = ft.TextField(label="Valor",prefix_text="R$",width=170, height=42, border_radius=10,
                                input_filter=ft.InputFilter(regex_string=r'[0-9,.]*', replacement_string=""),
                                keyboard_type=ft.KeyboardType.NUMBER,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.MONETIZATION_ON)
            self.servico = ft.TextField(label="Serviço",width=170, height=42, border_radius=10
                                ,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.TEXT_SNIPPET)
            self.chipPix = ft.Chip(label=ft.Text("Pix"),on_select=selected)
            self.chipMoney = ft.Chip(label=ft.Text("Dinheiro"),on_select=selected)
            self.chipPixRetiro = ft.Chip(label=ft.Text("Pix"),on_select=selected)
            self.chipMoneyRetiro = ft.Chip(label=ft.Text("Dinheiro"),on_select=selected)
            self.valoresRetiro = ft.TextField(label="Valor",prefix_text="R$",width=170, height=42, border_radius=10,
                                input_filter=ft.InputFilter(regex_string=r'[0-9,.]*', replacement_string=""),
                                keyboard_type=ft.KeyboardType.NUMBER,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.MONETIZATION_ON)
            self.motivo = ft.TextField(label="Motivo",width=170, height=42, border_radius=10
                                ,bgcolor=ft.Colors.WHITE,prefix_icon=ft.Icons.TEXT_SNIPPET)
            self.linhas = [
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(conta[0]),),
                            ft.DataCell(ft.Text(f"R${conta[1]}")),
                            ft.DataCell(ft.Text(conta[2])),
                            ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.BLACK,bgcolor=ft.Colors.RED_100))

                        ]
                    ) for i, conta in enumerate(self.dados)
                ]
            self.cardcontainer = ft.Container(
                content=self.buildcards(self.diario,self.mensal,self.contas)
            )
            self.tablecontent = ft.Container(
                content=BuildTableMobile(self.linhas)
            ) 
            self.caixainterface = ft.Column([
                ft.Row([
                    self.valores,self.servico
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),

                ft.Row([
                    ft.Text("Forma de Pagamento:")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                self.chipPix,self.chipMoney
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=registrarpg)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2)      
            self.retirointerface = ft.Column([
                ft.Row([
                    self.valoresRetiro,self.motivo
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.Text("Forma de saída:")
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    self.chipPixRetiro, self.chipMoneyRetiro
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=retirarpg)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2)
            self.contabcontent = ft.Column([
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Contabilidade",size=30)
                            ]
                            ,alignment=ft.MainAxisAlignment.START
                        ),margin=ft.Margin(left=10,top=0,right=0,bottom=0)
                    ),
                    self.cardcontainer,
                    ft.Container(
                        content=ft.Row([
                            self.main_interface_instance.cardmain("Registro de caixa",None,None,self.caixainterface,True),
                            self.main_interface_instance.cardmain("Registro de saîda",None,None,self.retirointerface,True)
                        ]
                        ,alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
                    ft.Container(
                        content=self.main_interface_instance.cardmain("Contabilidade de contas",None,None,self.tablecontent,True)
                    ),
            ],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START)
            future = self.page.run_task(diccreate_force)
            future.add_done_callback(on_diccreate_done)
            return ft.Column(
                [
                    ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Container(content=self.contabcontent,expand=True)
                ],
                width=self.page.width,
                height=self.page.height+80,
                alignment=ft.MainAxisAlignment.START
            )
    def buildcards(self,diario, mensal, contas):
        self.card_diario_home = self.main_interface_instance.cardfloat(icon=ft.Icons.MONETIZATION_ON_OUTLINED, title="Entrada", value=locale.currency(diario, grouping=True),
                                  barra="Entrada de hoje", iconbarra=ft.Icons.ARROW_UPWARD, corbarra=ft.Colors.GREEN, larg=None, color=ft.Colors.BLACK)
        self.card_mensal_home = self.main_interface_instance.cardfloat(icon=ft.Icons.MONEY, title="Mensal", value=locale.currency(mensal, grouping=True),
                                  barra="Receita do mês", iconbarra=ft.Icons.ARROW_UPWARD, corbarra=ft.Colors.GREEN, larg=None, color=ft.Colors.BLACK)
        self.card_contas_home = self.main_interface_instance.cardfloat(icon=ft.Icons.MONEY_OFF, title="A Pagar", value=locale.currency(contas, grouping=True),
                                  barra="Saida de caixa", iconbarra=ft.Icons.ARROW_DOWNWARD, corbarra=ft.Colors.RED, larg=None, color=ft.Colors.RED)
        for card in [self.card_diario_home, self.card_mensal_home, self.card_contas_home]:
            card.col = {"xs": 4, "md": 3, "sm": 3}

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


