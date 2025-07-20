import flet as ft
from funcoes import Auth,set_cargo,set_apelido


class Cadastro:
    def __init__(self,page:ft.Page):
        self.page = page 
        self.GlobalColor = '#26BD00'


    def build_view(self):
        self.title = ft.Text("iClínica", size=50, weight=ft.FontWeight.BOLD, color=self.GlobalColor)
        self.subtitle = ft.Text('Cadastre-se', size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family='Semibold')
        self.subtitleInstruction = ft.Text('Preencha as informações a seguir:', size=13, weight=ft.FontWeight.W_400, color=ft.Colors.BLACK, font_family='Semibold')
        self.user = ft.TextField(label="Usuário",
                        width=350, height=35, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        color=ft.Colors.BLACK)
        self.passw = ft.TextField(label="Senha",
                            password=True, can_reveal_password=True,
                            width=350, height=35, border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                            color=ft.Colors.BLACK )
        self.apelido = ft.TextField(label="Apelido",
                        width=350, height=35, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        color=ft.Colors.BLACK)
        self.cargo = ft.TextField(label="Codigo do cargo",
                        width=350, height=35, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        color=ft.Colors.BLACK,value="001")
        self.cadastroButton = ft.ElevatedButton("Cadastrar", color=ft.Colors.WHITE,
                            width=340, height=35,
                            bgcolor=ft.Colors.with_opacity(0.7, '#26BD00'), on_click=self.cadastrar)
        return ft.Column(
            [
                self.title,
                self.subtitle,
                self.subtitleInstruction,
                self.user,
                self.passw,
                self.apelido,
                self.cargo,
                self.cadastroButton
            ],
            width=self.page.width,
            height=self.page.height,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def barra_aviso(self,mensagem:str ,cor:str, text_color=ft.Colors.WHITE, icone=ft.Icon(ft.Icons.WARNING,color=ft.Colors.YELLOW_900 )):
        snack_bar = ft.SnackBar(
            content=ft.Row([icone,ft.Text(mensagem,color=text_color)]),
            bgcolor=cor,
        )
        self.page.open(snack_bar)

    def cadastrar(self,e):
        auth = Auth()
        _user = self.user.value
        _passw = self.passw.value
        _apelido = self.apelido.value
        if _user and _passw and _apelido:
            msg,codigo = auth.cadastro(_user,_passw)
            if self.cargo.value == "248105":
                set_cargo(_user,"developer")
            elif self.cargo.value == "2020":
                set_cargo(_user,"secretaria")
            if msg == "Sucesso":
                self.barra_aviso(f"Cadastrado com {msg}",ft.Colors.RED if codigo == 150 else ft.Colors.GREEN,icone=ft.Icon(ft.Icons.VERIFIED,ft.Colors.BLACK))
                set_apelido(_user,_apelido)
            elif msg != "Sucesso":
                self.barra_aviso(f"{msg}",ft.Colors.RED if codigo == 150 else ft.Colors.YELLOW,icone=ft.Icon(ft.Icons.WARNING,ft.Colors.BLACK))
                return
            self.user.value = ""
            self.passw.value = ""
            self.apelido.value = ""
            self.cargo.value = ""
            self.page.update()
            return
        self.barra_aviso("Preencha todos os campos!", ft.Colors.RED,icone=ft.Icon(ft.Icons.CLOSE,ft.Colors.BLACK))