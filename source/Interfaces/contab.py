from funcoes import vercontas
from decimal import Decimal
from database.models import ContaAPagar,Caixa
from database.databasecache import ContabilidadeDB,contabilidade_db
from Interfaces.main_interface import Main_interface
import locale
import flet as ft
from Interfaces.sidebar import Sidebar
from Interfaces.telaresize import Responsive

class ContabilidadePage:
    def __init__(self, page: ft.Page):
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.page = page
        self.responsive = Responsive(self.page)
        self.sidebar = Sidebar(self.page)
        self.db = ContabilidadeDB()
        self.main_interface_instance = Main_interface(page)
        self.card_dados = contabilidade_db.cache.get("contabilidade")
        self.contas_tabela = self.page.run_task(self.get_contas).result()
        self.selected_chip = None
        self.data_conta = ""
        self.dados = vercontas()
        self.page.on_resized = self.on_resize
    
    def on_resize(self,e):
        if self.page.route == "/contabilidade":
            self.responsive = Responsive(self.page)
            self.responsive.atualizar_widgets(self.build_view())

    async def get_contas(self):
        contas = await contabilidade_db.buscar_contas()
        return contas
    

    async def atualizar_cards(self):
        await contabilidade_db.invalidar_cache()
        self.card_dados = contabilidade_db.cache.get("contabilidade")
        self.diario = self.card_dados['diario'] if self.card_dados else 0.0
        self.mensal = self.card_dados['mensal'] if self.card_dados else 0.0
        self.contas = self.card_dados['contas'] if self.card_dados else 0.0
        if self.cardcontainer.page is not None:
            self.cardcontainer.content = self.buildcards(self.diario,self.mensal,self.contas)
            self.cardcontainer.update()

    async def atualizar_tabela(self): 
        self.dados_tabela = await self.db.buscar_contas()
        if self.tablecontent.page is not None:
            self.tablecontent.content = self.buildtable(self.gerar_linhas(self.dados_tabela))
            self.tablecontent.update()

    def build_view(self):
        async def retirar_valores(e):
            saida = str(self.valoresRetiro.value).replace(",",".")
            saida = Decimal(saida)
            forma_pagamento = self.selected_chip.label.value if self.selected_chip else "Nenhuma"
            motivoSaida = f"{self.motivo.value}, retirado via: {forma_pagamento}"
            if saida and motivoSaida:
                async with self.db.async_session() as session:
                    _retiro_ = Caixa(valor=-saida,descricao=motivoSaida,type="Saída")
                    session.add(_retiro_)
                    await session.commit()
                await self.atualizar_cards()
                self.valoresRetiro.value = ""
                self.motivo.value = ""
                self.valoresRetiro.update()
                self.motivo.update()
            else:
                snack = ft.SnackBar(content=ft.Text("Preencha todos os campos"))
                snack.open = True
                self.page.open(snack)
        async def registrar_pagamento(e):
            entrada = str(self.valores.value).replace(",",".")
            entrada = Decimal(entrada)
            forma_pagamento = self.selected_chip.label.value if self.selected_chip else "Nenhuma"
            servico = f"{self.servico.value}, Pago com: {forma_pagamento} "
            if entrada and servico:
                async with self.db.async_session() as session:
                    __insert__ = Caixa(valor=entrada,descricao=servico)
                    session.add(__insert__)
                    await session.commit()
                self.valores.value = ""
                self.servico.value = ""
                self.valores.update()
                self.servico.update()
                await self.atualizar_cards()
            else:
                self.barra_aviso("Preencha todos os campos!","#FF0000")
        if self.responsive.is_desktop():
            def selected(e: ft.ControlEvent):
                self.clicked = e.control
                if self.selected_chip and self.selected_chip != self.clicked:
                    self.selected_chip.selected = False
                self.clicked.selected = True
                self.selected_chip = self.clicked
                self.page.update()
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
            self.cardcontainer = ft.Container(
                content=self.buildcards(self.card_dados["diario"],self.card_dados["mensal"],self.card_dados["contas"])
            )
            self.tablecontent = ft.Container(content=self.buildtable(self.gerar_linhas(self.contas_tabela)),expand=True,border_radius=10) 
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
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK),icon_color=ft.Colors.BLACK45,on_click=registrar_pagamento)
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
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK),icon_color=ft.Colors.BLACK45,on_click=retirar_valores)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.contabcontent = ft.Column([
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Contabilidade", size=30,color=ft.Colors.GREY_800,weight=ft.FontWeight.W_400)
                            ]
                            ,alignment=ft.MainAxisAlignment.CENTER
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
            return ft.Row(
                [
                    ft.Column([self.sidebar.build()],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START),
                    ft.Container(content=self.contabcontent,expand=True)
                ],
                width=self.page.width,
                height=self.page.height,
                alignment=ft.MainAxisAlignment.START,
            ) 
        elif self.responsive.is_tablet():
            def selected(e: ft.ControlEvent):
                self.clicked = e.control
                if self.selected_chip and self.selected_chip != self.clicked:
                    self.selected_chip.selected = False
                self.clicked.selected = True
                self.selected_chip = self.clicked
                self.page.update()
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
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=registrar_pagamento)
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
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=retirar_valores)
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
            def selected(e: ft.ControlEvent):
                self.clicked = e.control
                if self.selected_chip and self.selected_chip != self.clicked:
                    self.selected_chip.selected = False
                self.clicked.selected = True
                self.selected_chip = self.clicked
                self.page.update()
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
                ft.Column([
                    self.valores,self.servico
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
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
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=registrar_pagamento)
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
            ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=2)      
            self.retirointerface = ft.Column([
                ft.Column([
                    self.valoresRetiro,self.motivo
                ],alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER
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
                    ft.TextButton(icon=ft.Icons.SEND,text="Registrar",style=ft.ButtonStyle(color=ft.Colors.BLACK,bgcolor="#dcdcdc"),icon_color=ft.Colors.BLACK45,on_click=retirar_valores)
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
                        ,alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER,scale=0.8)
                    ),
                    ft.Container(
                        content=self.main_interface_instance.cardmain("Contabilidade de contas",None,None,self.tablecontent,True)
                    ),
            ],alignment=ft.MainAxisAlignment.START,horizontal_alignment=ft.CrossAxisAlignment.START)
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
    
    def barra_aviso(self,mensagem:str ,cor:str):
        snack_bar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=cor
        )
        self.page.open(snack_bar)

    async def deletar_conta(self,idx):
        for i,conta in enumerate(self.dados_tabela):
            if idx==i:
                await self.db.deletar_contas(conta.descricao)
        await self.atualizar_tabela()
        await self.atualizar_cards()
            
    def registrar_conta(self,e):
        import datetime
        def date_picker(e):
            self.data_conta = date.value.strftime("%d/%m/%Y")
            visualizer.label = "Vencimento"
            visualizer.value = self.data_conta
            visualizer.disabled = False
            visualizer.update()
        async def registro_conta():
            self.page.close(modal) 
            valor_conta = Decimal(self.valor_conta.value)
            async with self.db.async_session() as session:
                _insrt_ = ContaAPagar(
                    descricao=self.descricao_conta.value,
                    valor=valor_conta,
                    vencimento=self.data_conta
                )
                session.add(_insrt_)
                await session.commit()   
            self.barra_aviso("Conta Registrada","#00FF15")
            await self.atualizar_tabela()
            await self.db.invalidar_cache()
            self.card_dados = self.cache.get("dados_contabilidade")
            self.diario = self.card_dados['diario'] if self.card_dados else 0.0
            self.mensal = self.card_dados['mensal'] if self.card_dados else 0.0
            self.contas = self.card_dados['contas'] if self.card_dados else 0.0
            if self.cardcontainer.page is not None:
                self.cardcontainer.content = self.buildcards(self.diario,self.mensal,self.contas)
                self.cardcontainer.update()
        
       
        date = ft.DatePicker(current_date=datetime.datetime.now(),on_change=lambda e: date_picker(e))
        self.descricao_conta = ft.TextField(label=ft.Text("Nome da conta"),border_radius=10,width=180,border_color=ft.Colors.RED)
        self.valor_conta = ft.TextField(label=ft.Text("Valor"),border_radius=10,width=180,border_color=ft.Colors.RED)
        self.vencimento_conta = ft.ElevatedButton(text="Vencimento",on_click=lambda _: self.page.open(date),color="#F12626")
        visualizer = ft.TextField(disabled=True,width=115,
                                  label_style=ft.TextStyle(color=ft.Colors.BLACK,),
                                  border_radius=10,border_color=ft.Colors.RED,
                                  )
        modal = ft.AlertDialog(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            title="Registar uma conta",
            actions=[ft.ElevatedButton(text="Registrar",on_click=lambda e: self.page.run_task(registro_conta))],
            content=ft.Column([
                ft.Row([ft.Text("INSIRA AS INFORMAÇÕES",weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.Row([self.descricao_conta,self.valor_conta],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([visualizer],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.vencimento_conta],alignment=ft.MainAxisAlignment.CENTER),
                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER)



            ],width=400,height=300)
        )
        self.page.open(modal)
    
    def buildtable(self,linhas):
        return ft.Column([
            ft.Row([
                ft.DataTable(
                    column_spacing=10,
                    heading_row_color="#A1FB8B",
                    border_radius=10,
                    expand=True,
                    columns=[
                        ft.DataColumn(ft.Text("Conta",weight=ft.FontWeight.BOLD,size=15),heading_row_alignment=ft.MainAxisAlignment.START),
                        ft.DataColumn(ft.Text("Valor",weight=ft.FontWeight.BOLD,size=15),numeric=True,heading_row_alignment=ft.MainAxisAlignment.CENTER),
                        ft.DataColumn(ft.Text("Vencimento",weight=ft.FontWeight.BOLD,size=15),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                        ft.DataColumn(ft.Text("Status",weight=ft.FontWeight.BOLD,size=15),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                        ft.DataColumn(ft.Text("Ações",weight=ft.FontWeight.BOLD,size=15),heading_row_alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    rows=linhas
                )
                ],alignment=ft.MainAxisAlignment.CENTER,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.TextButton(icon=ft.Icons.PAYMENTS,text="Registrar Conta",style=ft.ButtonStyle(color=ft.Colors.BLACK),
                                icon_color=ft.Colors.BLACK45,on_click=lambda e: self.registrar_conta(e))
                ])
        ])

    def gerar_linhas(self, data):
        linhas = []
        for i, conta in enumerate(data):
            async def deletar():  
                await self.deletar_conta(i)
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Container(content=ft.Text(conta.descricao),alignment=ft.alignment.center_left)),
                    ft.DataCell(ft.Container(content=ft.Text(f"R${conta.valor}"),alignment=ft.alignment.center)),
                    ft.DataCell(ft.Container(content=ft.Text(conta.vencimento),alignment=ft.alignment.center)),
                    ft.DataCell(ft.Container(content=ft.Text(conta.status),alignment=ft.alignment.center)),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.BLACK,
                                bgcolor=ft.Colors.RED_100,
                                on_click=lambda e, fn=deletar: self.page.run_task(fn) 
                            )
                        ],alignment=ft.MainAxisAlignment.CENTER)
                    )
                ]
            )
            linhas.append(row)
        return linhas

    
