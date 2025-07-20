import flet as ft 
from funcoes import Auth, get_cargo



class Login:
    """SISTEMA DE LOGIN\n-
- Gerencia o login e gera a pagina de login.\n

    """
    def __init__(self, page: ft.Page):
        self.page = page 
        self.GlobalColor = '#26BD00'
        self.GlobalModal = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.GREEN)

    def build_view(self):
        self.title = ft.Text("iClínica", size=50, weight=ft.FontWeight.BOLD, color=self.GlobalColor)
        self.subtitle = ft.Text('Faça seu login', size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family='Semibold')
        self.subtitleInstruction = ft.Text('Entre com seu usuário e senha', size=13, weight=ft.FontWeight.W_400, color=ft.Colors.BLACK, font_family='Semibold')
        self.user = ft.TextField(label="Usuário",
                        width=350, height=35, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        color=ft.Colors.BLACK)
        self.passw = ft.TextField(label="Senha",
                            password=True, can_reveal_password=True,
                            width=350, height=35, border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                            color=ft.Colors.BLACK )
        self.entryButton = ft.ElevatedButton("Entrar", color=ft.Colors.WHITE,
                            width=340, height=35,
                            bgcolor=ft.Colors.with_opacity(0.7, '#26BD00'),
                            on_click=self.on_login_click)
        self.cadastroButton = ft.ElevatedButton("Cadastrar", color=ft.Colors.WHITE,
                            width=340, height=35,
                            bgcolor=ft.Colors.with_opacity(0.7, '#26BD00'), on_click=lambda e: self.page.go("/cadastro"))
        return ft.Column(
            [
                self.title,
                self.subtitle,
                self.subtitleInstruction,
                self.user,
                self.passw,
                self.GlobalModal,
                self.entryButton,
                self.cadastroButton
            ],
            width=self.page.width,
            height=self.page.height,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )


    def show_loading(self, show=True):
        loading = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(width=50, height=50, color=ft.Colors.LIGHT_GREEN),
                    ft.Text("Carregando...", size=16, color=self.GlobalColor)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
            expand=True
        )
        if show:
            self.page.overlay.append(loading)
        else:
            if loading in self.page.overlay:
                self.page.overlay.remove(loading)
                self.page.overlay.clear()
                loading.visible = False
                self.page.update()
            else:
                pass
        self.page.update()

    def auth_session(self,user):
        cargo = get_cargo(user)
        if not self.page.client_storage.contains_key("nick"):
            self.page.client_storage.set("nick",f"{user}")
        self.page.session.set("user",f"{user}")
        self.page.session.set("logado",True)
        if cargo == "secretaria" or cargo == "developer":
            self.page.session.set("perm", "all")


    def on_login_click(self, e):
        auth = Auth()
        usuario = self.user.value
        senha = self.passw.value
        if not usuario or not senha:
            self.GlobalModal.content = ft.Text("Preencha todos os campos")
            self.GlobalModal.bgcolor = ft.Colors.RED
            self.GlobalModal.open = True
            self.GlobalModal.update()
        else:
            if auth.login(usuario=usuario, password=senha):
                self.show_loading(True)
                self.page.overlay.clear()
                self.page.update()
                self.auth_session(usuario)
                self.page.go("/home") 
            else:
                self.GlobalModal.content = ft.Text("Usuário ou senha inválidos")
                self.GlobalModal.bgcolor = ft.Colors.RED
                self.page.snack_bar = self.GlobalModal
                self.page.add(self.GlobalModal)
                self.GlobalModal.open = True
                self.page.update()

    def on_cadastro_click(self, e):
        auth = Auth()
        usuario = self.user.value
        senha = self.passw.value
        if not usuario or not senha:
            self.GlobalModal.content = ft.Text("Preencha todos os campos")
            self.GlobalModal.bgcolor = ft.Colors.RED
            self.page.snack_bar = self.GlobalModal
            self.page.add(self.GlobalModal)
            self.GlobalModal.open = True
            self.page.update()
        else:
            msg, sucesso = auth.cadastro(user=usuario, passw=senha)
            self.GlobalModal.content = ft.Text(msg)
            self.GlobalModal.bgcolor = ft.Colors.GREEN if sucesso == 200 else ft.Colors.RED
            self.page.snack_bar = self.GlobalModal
            self.page.add(self.GlobalModal)
            self.GlobalModal.open = True
            self.show_loading(True)
            self.page.overlay.clear()
            self.user.value = ""
            self.passw.value = ""
            self.page.update()



    
