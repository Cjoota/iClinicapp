import flet as ft
class Resize:
    def __init__(self,page: ft.Page):
        self.page = page
        self.larguraTela = page.width 
        self.alturaTela = page.height 
    def tamanhoTela(self) -> float:
        if self.larguraTela >= 1920.0 and self.alturaTela >= 900.0: #Full HD
            return 1.0
        elif self.larguraTela >= 1366.0 and self.alturaTela >= 600.0: #sHD
            return 0.8
        elif self.larguraTela >= 1330.0 and self.alturaTela >= 600.0: #Tablet
            return 0.8
        elif self.larguraTela >= 400.0 and self.alturaTela >= 750.0: #Mobile
            return 0.5
    def barraLateral(self) -> float:
        if self.tamanhoTela() == 0.8:
            return 0 # Informa a Sidebar a entrada de Tablet ou sHD

        if self.tamanhoTela() == 1.0:
            return 1 # Informa a Sidebar a entrada de FullHD

        if self.tamanhoTela() == 0.5:
            return 2 # Informa a Sidebar a entrada de Mobile


class Responsive:
    def __init__(self, page: ft.Page):
        self.page = page
        self.width = page.width
        self.height = page.height

    def atualizar_widgets(self,build_view):
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                self.page.route,
                [build_view]
            )
        )
        self.page.go(self.page.route)
    def is_mobile(self):
        return self.width <= 480

    def is_tablet(self):
        return self.width >= 800 and self.width <= 1334

    def is_desktop(self):
        return self.width > 1337
    
    def is_shd(self):
        return self.width <= 1337 and self.width >= 1335

    def content_width(self) -> float:
        if self.is_mobile():
            return self.width * 1.0
        elif self.is_tablet():
            return self.width * 1.0
        else:
            return self.width * 0.88 

    def content_cards(self):
        if self.is_mobile():
            return self.width * 0.95 * 0.60
        elif self.is_tablet():
            return self.width * 0.85 * 0.20
        else:
            return self.width * 0.70 * 0.20


    def size_widget(self):
        if self.is_mobile():
            return 0.9
        elif self.is_tablet():
            return 1.0
        else:
            return 1.0


    def content_height(self):
        if self.is_mobile():
            return self.height * 0.8
        elif self.is_tablet():
            return self.height * 0.75
        else:
            return self.height * 0.7

    def font_size(self):
        if self.is_mobile():
            return 15
        elif self.is_tablet():
            return 15
        else:
            return 25

    def button_width(self):
        if self.is_mobile():
            return self.width * 0.9
        elif self.is_tablet():
            return self.width * 0.6
        else:
            return self.width * 0.4

    def spacing(self):
        if self.is_mobile():
            return 0
        elif self.is_tablet():
            return 20
        else:
            return 10
    def padding(self):
        if self.is_mobile():
            return 6
        elif self.is_tablet():
            return 10
        else:
            return 20
