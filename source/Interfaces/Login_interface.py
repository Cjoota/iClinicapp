import flet as ft 
from funcoes import Auth

class Login:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.Colors.WHITE
        self.GlobalColor = '#26BD00'
        self.GlobalModal = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.GREEN)
        self.is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.appbar = ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.DARK_MODE, tooltip="Alternar tema", on_click=lambda e: self.change_theme(e)),
            leading_width=50,
            bgcolor=ft.Colors.WHITE)

    def build_view(self):
        self.bypass = ft.Button(text="Bypass", icon=ft.Icons.BACKUP, tooltip="Bypass", on_click=lambda e: self.page.go("/home"))
        self.title = ft.Text("iClínica", size=50, weight=ft.FontWeight.BOLD, color=self.GlobalColor)
        self.subtitle = ft.Text('Faça seu login', size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, font_family='Semibold')
        self.subtitleInstruction = ft.Text('Entre com seu usuário e senha', size=13, weight=ft.FontWeight.W_400, color=ft.Colors.BLACK, font_family='Semibold')
        self.user = ft.TextField(label="Usuário",
                        width=350, height=35, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE if not self.is_dark else ft.Colors.BLACK),
                        color=ft.Colors.BLACK if not self.is_dark else ft.Colors.WHITE)
        self.passw = ft.TextField(label="Senha",
                            password=True, can_reveal_password=True,
                            width=350, height=35, border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE if not self.is_dark else ft.Colors.BLACK),
                            color=ft.Colors.BLACK if not self.is_dark else ft.Colors.WHITE)
        self.entryButton = ft.ElevatedButton("Entrar", color=ft.Colors.WHITE,
                            width=340, height=35,
                            bgcolor=ft.Colors.with_opacity(0.7, '#26BD00' if not self.is_dark else ft.Colors.BLACK),
                            on_click=self.on_login_click)
        self.cadastroButton = ft.ElevatedButton("Cadastrar", color=ft.Colors.WHITE,
                            width=340, height=35,
                            bgcolor=ft.Colors.with_opacity(0.7, '#26BD00' if not self.is_dark else ft.Colors.BLACK), on_click=self.on_cadastro_click)
        return ft.Column(
            [
                self.bypass,
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

    def change_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.bgcolor = ft.Colors.BLACK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.bgcolor = ft.Colors.WHITE
        self.update_component_colors()
        self.page.update()

    def update_component_colors(self):
        """Atualiza as cores dos componentes quando o tema muda"""
        self.is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.user.bgcolor = ft.Colors.with_opacity(0.7, ft.Colors.WHITE if not self.is_dark else ft.Colors.BLACK)
        self.user.color = ft.Colors.BLACK if not self.is_dark else ft.Colors.WHITE
        self.passw.bgcolor = ft.Colors.with_opacity(0.7, ft.Colors.WHITE if not self.is_dark else ft.Colors.BLACK)
        self.passw.color = ft.Colors.BLACK if not self.is_dark else ft.Colors.WHITE
        self.appbar.bgcolor = ft.Colors.WHITE if not self.is_dark else ft.Colors.GREY_900
        self.page.bgcolor = ft.Colors.WHITE if not self.is_dark else ft.Colors.GREY_900

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
                self.appbar.visible = False
                self.show_loading(True)
                self.page.overlay.clear()
                self.page.update()
                self.page.client_storage.set("logado", "sim")
                self.page.go("/home") # Navigate to main interface
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


