import flet as ft
import asyncio
from src.core.sidebar import Sidebar
from src.utils.telaresize import Responsive

class MainLayout:
    def __init__(self, page: ft.Page):
        self.page = page
        self.responsive = Responsive(self.page)
        self.sidebar = Sidebar(self.page)
        self.content_area = ft.Container(expand=True)
        self.current_route = None

        self.main_container = self._build_layout()

    def _build_layout(self):
        if self.responsive.is_mobile() or self.responsive.is_tablet():
            return ft.Column([
                ft.Row([self.sidebar.build()],
                       alignment=ft.MainAxisAlignment.CENTER,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(content=self.content_area, expand=True, padding=10)
            ], spacing=0)
        else:
            self.sidebar.rota = self.page.route
            return ft.Row([
                ft.Column([self.sidebar.build()], alignment=ft.MainAxisAlignment.START),
                ft.Container(content=self.content_area, expand=True, padding=20)
            ], expand=True)

    async def navigate_to(self, route: str, content_builder):
        if self.current_route == route:
            return
        # Só atualize se já está na página
        if self.content_area.page is None:
            return

        # Loading
        self.content_area.content = ft.Container(
            content=ft.ProgressRing(color="#22ff38"),
            alignment=ft.alignment.center,
            expand=True
        )
        self.content_area.update()
        await asyncio.sleep(0.05)

        try:
            if asyncio.iscoroutinefunction(content_builder):
                new_content = await content_builder()
            else:
                new_content = await asyncio.to_thread(content_builder)
            self.content_area.content = new_content
            self.current_route = route
            self.sidebar.item_selecionado = route
        except Exception as e:
            self.content_area.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=50),
                    ft.Text(f"Erro ao carregar: {str(e)}", color=ft.Colors.RED)
                ], alignment=ft.MainAxisAlignment.CENTER,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        self.content_area.update()
        self.sidebar.on_change(e=None,rota=route)

    def get_view(self, route: str):
        return ft.View(
            route="main",
            controls=[self.main_container],
        )