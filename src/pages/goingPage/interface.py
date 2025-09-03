import json
from dataclasses import dataclass
from PIL import Image as PILImage
import shutil
import os
import flet as ft
import flet.canvas as cv
import openpyxl
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.utils import column_index_from_string
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
from openpyxl.drawing.image import Image as ExcelImage
from datetime import datetime
from pathlib import Path
from src.functions.funcs import converter_xlsx_para_pdf, pdf_para_imagem_redimensionada
from PIL import Image, ImageDraw
from src.utils.telaresize import Responsive
@dataclass
class State:
    x: float
    y: float

class Andamentos:
    def __init__(self, page: ft.Page):
        self.page = page
        self.json_anamnese = self.carregar_jsons("ANAMNESE")
        self.json_aso = self.carregar_jsons("ASO")
        self.json_audio = self.carregar_jsons("AUDIOMETRIA")
        self.state = State(x=0,y=0)
        self.responsive = Responsive(self.page)
        self.caminho_imagem_x = self.criar_imagem_x()
        self.empresas_exames = self.listar_empresas()
        self.search_field = ft.TextField(
            hint_text="Pesquisar empresa",
            width=400,
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.GREY_400,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.GREY_900,
            border_radius=8,
            height=48,
            on_change=self.filtrar_empresas
        )
        self.expansion_list = ft.ExpansionPanelList(
            expand_icon_color=ft.Colors.BLACK54,
            divider_color=ft.Colors.WHITE,
            elevation=10,
            on_change=self.expandir_empresas
        )
        self.carregar_empresa()

    def carregar_jsons(self, nome_arquivo: str) -> dict:
        caminho_json = Path(f"src/pages/goingPage/Jsons/{nome_arquivo}.json")
        if not caminho_json.exists():
            return {}
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)

    def criar_imagem_x(self, tamanho=15, cor="black", espessura=2, caminho_saida="assets/marcacao_x/x_mark.png"):
        caminho_saida_path = Path(caminho_saida)
        if not caminho_saida_path.exists():
            caminho_saida_path.parent.mkdir(parents=True, exist_ok=True)
            img = Image.new("RGBA", (tamanho, tamanho), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.line((0, 0, tamanho, tamanho), fill=cor, width=espessura)
            draw.line((0, tamanho, tamanho, 0), fill=cor, width=espessura)
            img.save(str(caminho_saida_path))
        return str(caminho_saida_path)
    
    def inserir_marcacao(self, ws, celula, caminho_imagem, offset_x_pixels=0, offset_y_pixels=0):
        caminho_imagem_path = Path(caminho_imagem)
        if not caminho_imagem_path.exists():
            # Cria a imagem X se não existir
            caminho_imagem = self.criar_imagem_x(caminho_saida=str(caminho_imagem_path))

        # Resto do código para inserir a imagem no Excel
        offset_x = int(offset_x_pixels * 9525)
        offset_y = int(offset_y_pixels * 9525)

        img = ExcelImage(caminho_imagem)

        col_letter = ''.join(filter(str.isalpha, celula))
        row_number = int(''.join(filter(str.isdigit, celula)))
        col = column_index_from_string(col_letter)

        ext_x = int(img.width * 9525)
        ext_y = int(img.height * 9525)

        marker = AnchorMarker(col=col-1, colOff=offset_x, row=row_number-1, rowOff=offset_y)
        size = XDRPositiveSize2D(cx=ext_x, cy=ext_y)
        anchor = OneCellAnchor(_from=marker, ext=size)
        img.anchor = anchor

        ws.add_image(img)

    def listar_empresas(self):
        documentos_dir = Path("documentos_gerados")
        empresas = {}

        if not documentos_dir.exists():
            return {}

        hoje = datetime.now().date()

        for arquivo in documentos_dir.glob("*.xlsx"):
            nome_arquivo = arquivo.stem
            partes = nome_arquivo.split()

            if len(partes) < 5:
                continue

            data_str = partes[-2]

            try:
                data_arquivo = datetime.strptime(data_str, "%d-%m-%Y").date()
            except ValueError:
                continue

            if data_arquivo == hoje:
                empresa = " ".join(partes[1:-3])
                if empresa not in empresas:
                    empresas[empresa] = []
                empresas[empresa].append(arquivo)

        return empresas

    def criar_painel_empresa(self, empresa: str, cnpj):
        return ft.ExpansionPanel(
            can_tap_header=True,
            bgcolor="#EEFFEA",
            header=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            empresa.upper(),
                            size=18,
                            weight=ft.FontWeight.NORMAL,
                            color=ft.Colors.GREY_900,
                            font_family="Roboto"
                        ),
                        ft.Text(
                            cnpj,
                            size=14,
                            color=ft.Colors.GREY_600,
                            font_family="Roboto"
                        ) if cnpj else ft.Container()
                    ],
                    spacing=2,
                ),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor="#EEFFEA",
                border_radius=5
            ),
            content=ft.Container(
                content=ft.Text(
                    "Carregando documentos",
                    italic=True,
                    size=14,
                    color=ft.Colors.GREY_500
                ),
                bgcolor="#EEFFEA",
                padding=16
            )
        )

    def carregar_empresa(self, filtro=""):
        self.expansion_list.controls.clear()
        for empresa, arquivos in self.empresas_exames.items():
            if filtro.lower() in empresa.lower():
                if len(self.expansion_list.controls) >= 50:
                    break
                painel = self.criar_painel_empresa(empresa, "")
                self.expansion_list.controls.append(painel)
        self.page.update()

    def filtrar_empresas(self, e):
        filtro = e.control.value
        self.carregar_empresa(filtro)

    def expandir_empresas(self, e):
        index = int(e.data)
        if index < 0:
            return

        painel = self.expansion_list.controls[index]
        empresa = list(self.empresas_exames.keys())[index]

        exames_da_empresa = [ex for ex in self.listar_exames() if ex["empresa"] == empresa]

        controles_exames = []
        for exame in exames_da_empresa:
            botoes = self.gerenciar_painel_exames(exame["arquivo"], exame["tipo_exame"])

            linha_exame = ft.Row(
                [
                    ft.Text(
                        f"Colaborador: {exame['colaborador']} | Exame: {exame['tipo_exame']} | Data: {exame['data']}",
                        size=14,
                        color=ft.Colors.GREY_800,
                        expand=True
                    ),
                    *botoes
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            )
            controles_exames.append(linha_exame)

        painel.content = ft.Container(
            content=ft.Column(controles_exames, spacing=6),
            bgcolor="#EEFFEA",
            padding=16
        )
        self.page.update()

    def listar_exames(self):
        documentos_dir = Path("documentos_gerados")
        exames = []

        if not documentos_dir.exists():
            return []

        hoje = datetime.now().date()

        for arquivo in documentos_dir.glob("*.xlsx"):
            nome_arquivo = arquivo.stem
            partes = nome_arquivo.split()

            if len(partes) < 5:
                continue

            data_str = partes[-2]

            try:
                data = datetime.strptime(data_str, "%d-%m-%Y").date()
            except ValueError:
                continue

            if data == hoje:
                tipo_exame = partes[0]
                colaborador = partes[-3]
                empresa = " ".join(partes[1:-3])

                exames.append({
                    "tipo_exame": tipo_exame,
                    "empresa": empresa,
                    "colaborador": colaborador,
                    "data": data.strftime("%d/%m/%Y"),
                    "arquivo": arquivo
                })

        return exames

    def abrir_dialog_assinatura(self, caminho_xlsx: Path, tipo_exame: str, quem_assina: str):
        # Copia o arquivo para edição
        caminho_para_editar = self.preparar_arquivo_para_edicao(caminho_xlsx)

        linhas_desenhadas = []
        largura, altura = 400, 150  # tamanho do canvas para assinatura

        def pan_start(e: ft.DragStartEvent):
            self.state.x = e.local_x
            self.state.y = e.local_y

        def pan_update(e: ft.DragUpdateEvent):
            linha = cv.Line(
                self.state.x, self.state.y, e.local_x, e.local_y,
                paint=ft.Paint(stroke_width=3, color=ft.Colors.BLACK)
            )
            linhas_desenhadas.append(linha)
            canvas.shapes.append(linha)
            canvas.update()
            self.state.x = e.local_x
            self.state.y = e.local_y

        def salvar_assinatura(e):
            try:
                img = Image.new("RGBA", (largura, altura), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)

                for linha in linhas_desenhadas:
                    draw.line(
                        [(linha.x1, linha.y1), (linha.x2, linha.y2)],
                        fill=(0, 0, 0, 255),
                        width=3
                    )

                nome_assinatura = f"{caminho_para_editar.stem}_assinatura_{quem_assina}.png"
                caminho_assinatura = Path("assets/assinaturas") / nome_assinatura
                caminho_assinatura.parent.mkdir(parents=True, exist_ok=True)
                img.save(str(caminho_assinatura))

                # Usa o caminho da cópia para editar o Excel
                self.inserir_assinatura_excel(caminho_para_editar, caminho_assinatura, tipo_exame, quem_assina)

                dialog_assinatura.open = False
                self.page.update()

            except Exception as ex:
                print(f"Erro ao salvar assinatura: {ex}")

        def limpar_canvas(e):
            canvas.shapes.clear()
            linhas_desenhadas.clear()
            canvas.update()

        canvas = cv.Canvas(
            [],
            content=ft.GestureDetector(
                on_pan_start=pan_start,
                on_pan_update=pan_update,
                drag_interval=2,
                width=largura,
                height=altura,
            ),
            width=largura,
            height=altura,
        )

        canvas_container = ft.Container(
            content=canvas,
            width=largura,
            height=altura,
            bgcolor=ft.Colors.WHITE,
        )

        dialog_assinatura = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Assinatura - {quem_assina.capitalize()}"),
            content=canvas_container,
            actions=[
                ft.TextButton("Limpar", on_click=limpar_canvas),
                ft.TextButton("Salvar", on_click=salvar_assinatura),
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog(dialog_assinatura)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dialog_assinatura)
        self.page.update()

    def inserir_assinatura_excel(self, caminho_xlsx: Path, caminho_assinatura: Path, tipo_exame: str, quem_assina: str):
        try:
            wb = openpyxl.load_workbook(str(caminho_xlsx))

            if tipo_exame.upper() == "ANAMNESE":
                if len(wb.worksheets) > 1:
                    ws = wb.worksheets[1] 
                else:
                    ws = wb.worksheets[0]  
            else:
                ws = wb.worksheets[0]  

            
            img_pil = PILImage.open(caminho_assinatura)
            largura_original, altura_original = img_pil.size

            
            largura_desejada = 150  
            altura_desejada = int(altura_original * (largura_desejada / largura_original))

            img_excel = ExcelImage(str(caminho_assinatura))
            img_excel.width = largura_desejada
            img_excel.height = altura_desejada

            if tipo_exame.upper() == "ANAMNESE":
                if quem_assina == "paciente":
                    ws.merge_cells('C51:D51')
                    ws.add_image(img_excel, 'C51')

            elif tipo_exame.upper() == "ASO":
                if quem_assina == "paciente":
                    ws.merge_cells('B58:C58')
                    ws.add_image(img_excel, 'B58')

            elif tipo_exame.upper() == "AUDIOMETRIA":
                if quem_assina == "paciente":
                    ws.merge_cells('O66:P66')
                    ws.add_image(img_excel, 'O66')

            else:
                print(f"Tipo de exame '{tipo_exame}' não reconhecido para inserir assinatura.")
                return

            wb.save(str(caminho_xlsx))
            print(f"Assinatura do {quem_assina} inserida no arquivo {caminho_xlsx} para o exame {tipo_exame}")

        except Exception as e:
            print(f"Erro ao inserir assinatura no Excel: {e}")

    def preparar_arquivo_para_edicao(self, caminho_original: Path) -> Path:
        pasta_destino = Path("documentos_editados")
        pasta_destino.mkdir(parents=True, exist_ok=True)

        caminho_copia = pasta_destino / caminho_original.name

        shutil.copy2(caminho_original, caminho_copia)

        print(f"Arquivo copiado para edição: {caminho_copia}")

        return caminho_copia

    def gerenciar_painel_exames(self, caminho_xlsx: Path, tipo_exame: str):
        botoes = []
        tipo = tipo_exame.upper()

        if tipo == "ANAMNESE":
            botoes.append(
                ft.ElevatedButton(
                    text="Marcar Opções ANAMNESE",
                    icon=ft.Icons.CHECK,
                    bgcolor="#2196F3",
                    color=ft.Colors.WHITE,
                    height=35,
                    on_click=lambda e, caminho=caminho_xlsx: self.controlar_anamnese(caminho)
                )
            )
            botoes.append(
                ft.ElevatedButton(
                    text="Assinatura Paciente",
                    icon=ft.Icons.BRUSH,
                    bgcolor="#4CAF50",
                    color=ft.Colors.BLACK,
                    height=35,
                    on_click=lambda e, caminho=caminho_xlsx, tipo=tipo: self.abrir_dialog_assinatura(caminho, tipo, "paciente")
                )
            )

        elif tipo == "ASO":
            botoes.append(
                ft.ElevatedButton(
                    text="Marcar opções ASO",
                    icon=ft.Icons.CHECK,
                    bgcolor="#2196F3",
                    color=ft.Colors.WHITE,
                    height=35,
                    on_click=lambda e, caminho=caminho_xlsx: self.controlar_aso(caminho)
                )
            )
            botoes.append(
                ft.ElevatedButton(
                    text="Assinatura Paciente",
                    icon=ft.Icons.BRUSH,
                    bgcolor="#4CAF50",
                    color=ft.Colors.BLACK,
                    height=35,
                    on_click=lambda e, caminho=caminho_xlsx, tipo=tipo: self.abrir_dialog_assinatura(caminho, tipo, "paciente")
                )
            )

        elif tipo == "AUDIOMETRIA":
            botoes.append(
                ft.ElevatedButton(
                    text="Marcar opções AUDIOMETRIA",
                    icon=ft.Icons.CHECK,
                    bgcolor="#2196F3",
                    color=ft.Colors.WHITE,
                    height=35,
                    on_click=lambda e, caminho=caminho_xlsx: self.controlar_audiometria(caminho)
                )
            )
            botoes.append(
                ft.ElevatedButton(
                    text="Assinatura Paciente",
                    icon=ft.Icons.BRUSH,
                    bgcolor="#4CAF50",
                    color=ft.Colors.BLACK,
                    height=35,
                    on_click=lambda e, caminho=caminho_xlsx, tipo=tipo: self.abrir_dialog_assinatura(caminho, tipo, "paciente")
                )
            )

        return botoes

    def controlar_anamnese(self, caminho_xlsx: Path):
        caminho_x_img = self.caminho_imagem_x 

        controles_opcoes = []
        for descricao, celulas in self.json_anamnese.items():
            rg = ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value="sim", label="SIM"),
                    ft.Radio(value="nao", label="NÃO"),
                ]),
                value="nao"
            )
            controles_opcoes.append((descricao, celulas, rg))

        lista_controles = []
        for descricao, celulas, rg in controles_opcoes:
            lista_controles.append(ft.Text(descricao))
            lista_controles.append(rg)

        coluna_opcoes = ft.Column(lista_controles, scroll=ft.ScrollMode.AUTO, height=400)

        def salvar_opcoes(e):
            try:
                wb = openpyxl.load_workbook(str(caminho_xlsx))
                ws = wb.worksheets[0]

                todas_celulas = []
                for _, celulas, _ in controles_opcoes:
                    todas_celulas.extend([celulas.get("sim", ""), celulas.get("nao", "")])
                todas_celulas = [c for c in todas_celulas if c]

                imagens_para_remover = []
                for img in ws._images:
                    anchor = img.anchor
                    if isinstance(anchor, str) and anchor in todas_celulas:
                        imagens_para_remover.append(img)
                    elif hasattr(anchor, "_from"):
                        col = anchor._from.col + 1
                        row = anchor._from.row + 1
                        cel = openpyxl.utils.get_column_letter(col) + str(row)
                        if cel in todas_celulas:
                            imagens_para_remover.append(img)
                for img in imagens_para_remover:
                    ws._images.remove(img)

                # Insere as novas marcações com deslocamento ajustado
                for descricao, celulas, rg in controles_opcoes:
                    valor = rg.value
                    if valor == "sim":
                        self.inserir_marcacao(ws, celulas["sim"], caminho_x_img, offset_x_pixels=5, offset_y_pixels=19)
                    else:
                        self.inserir_marcacao(ws, celulas["nao"], caminho_x_img, offset_x_pixels=5, offset_y_pixels=19)

                wb.save(str(caminho_xlsx))
                dialog_opcoes.open = False
                self.page.update()
            except Exception as ex:
                print(f"Erro ao salvar opções ANAMNESE: {ex}")

        dialog_opcoes = ft.AlertDialog(
            modal=True,
            title=ft.Text("Marcar opções - ANAMNESE"),
            content=coluna_opcoes,
            actions=[
                ft.TextButton("Salvar", on_click=salvar_opcoes),
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog(dialog_opcoes)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dialog_opcoes)
        self.page.update()

    def controlar_aso(self, caminho_xlsx: Path):
        caminho_x_img = self.criar_imagem_x()

        controles_opcoes = []
        for descricao, celula in self.json_aso.items():
            cb = ft.Checkbox(label=descricao, value=False)
            controles_opcoes.append((descricao, celula, cb))

        lista_controles = [cb for _, _, cb in controles_opcoes]
        coluna_opcoes = ft.Column(lista_controles, scroll=ft.ScrollMode.AUTO, height=400)

        def salvar_opcoes(e):
            try:
                wb = openpyxl.load_workbook(str(caminho_xlsx))
                ws = wb.worksheets[0]

                # Remove imagens antigas nas células do ASO
                todas_celulas = [celula for _, celula, _ in controles_opcoes]
                imagens_para_remover = []
                for img in ws._images:
                    anchor = img.anchor
                    if isinstance(anchor, str) and anchor in todas_celulas:
                        imagens_para_remover.append(img)
                    elif hasattr(anchor, "_from"):
                        col = anchor._from.col + 1
                        row = anchor._from.row + 1
                        cel = openpyxl.utils.get_column_letter(col) + str(row)
                        if cel in todas_celulas:
                            imagens_para_remover.append(img)
                for img in imagens_para_remover:
                    ws._images.remove(img)

                # Insere as novas marcações com deslocamento ajustado
                for descricao, celula, cb in controles_opcoes:
                    if cb.value:
                        self.inserir_marcacao(ws, celula, caminho_x_img, offset_x_pixels=4, offset_y_pixels=3)

                wb.save(str(caminho_xlsx))
                dialog_opcoes.open = False
                self.page.update()
            except Exception as ex:
                print(f"Erro ao salvar opções ASO: {ex}")

        dialog_opcoes = ft.AlertDialog(
            modal=True,
            title=ft.Text("Marcar opções - ASO"),
            content=coluna_opcoes,
            actions=[
                ft.TextButton("Salvar", on_click=salvar_opcoes),
                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_dialog(dialog_opcoes)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dialog_opcoes)
        self.page.update()

    def controlar_audiometria(self, caminho_xlsx: str):

        caminho_x_img = self.caminho_imagem_x

        offsets_personalizados = {
            "B54": (22, 8),
            "D56": (22, 4),
            "F56": (46, 3),
            "B57": (24, 15),
            "E57": (30, 15),
            "I57": (38, 15),
            "M57": (21, 15),
            "B60": (22, 8),
            "D62": (22, 4),
            "F62": (46, 3),
            "B63": (24, 11),
            "E63": (30, 11),
            "I63": (38, 11),
            "M63": (21, 11)
        }

        def inserir_marcacao_personalizada(ws, celula, caminho_imagem):
            offset_x, offset_y = offsets_personalizados.get(celula, (0, 0))
            self.inserir_marcacao(ws, celula, caminho_imagem, offset_x_pixels=offset_x, offset_y_pixels=offset_y)

        def salvar_desenho_audiometria(e, linhas_desenhadas, caminho_xlsx_alvo, dialog_para_fechar):
            if not linhas_desenhadas:
                print("Nenhum desenho para salvar.")
                self.fechar_dialog(dialog_para_fechar)
                return

            try:
                LARGURA_EXCEL_PX = 1116
                ALTURA_EXCEL_PX = 516

                caminho_imagem_fundo = Path("assets/audiometria/audiometria.png")
                with Image.open(caminho_imagem_fundo) as img_fundo:
                    largura_canvas, altura_canvas = img_fundo.size

                # Define o caminho de saída para a nova imagem transparente
                pasta_saida_desenhos = Path("assets/desenhos_audiometria")
                pasta_saida_desenhos.mkdir(parents=True, exist_ok=True)
                nome_arquivo_saida = f"{Path(caminho_xlsx_alvo).stem}_desenho_overlay.png"
                caminho_imagem_saida = pasta_saida_desenhos / nome_arquivo_saida

                # Cria uma imagem transparente com as mesmas dimensões do canvas onde foi desenhado
                desenho_transparente = Image.new("RGBA", (largura_canvas, altura_canvas), (0, 0, 0, 0))
                draw = ImageDraw.Draw(desenho_transparente)

                # Desenha as linhas nesta imagem transparente
                for linha in linhas_desenhadas:
                    draw.line(
                        [(linha.x1, linha.y1), (linha.x2, linha.y2)],
                        fill=(255, 0, 0, 255),  # Cor vermelha (RGBA)
                        width=3
                    )

                # Salva a imagem que contém APENAS o desenho transparente
                desenho_transparente.save(caminho_imagem_saida)
                print(f"Desenho transparente salvo em: {caminho_imagem_saida}")

                wb = openpyxl.load_workbook(str(caminho_xlsx_alvo))
                ws = wb.worksheets[0]
                

                img_excel = ExcelImage(caminho_imagem_saida)
                

                img_excel.width = LARGURA_EXCEL_PX
                img_excel.height = ALTURA_EXCEL_PX

                celula_alvo = 'A22'
                ws.add_image(img_excel, celula_alvo)

                wb.save(str(caminho_xlsx_alvo))
                print(f"Desenho sobreposto e redimensionado com sucesso no Excel!")

            except Exception as ex:
                print(f"Erro ao salvar o desenho da audiometria: {ex}")
            
            finally:
                self.fechar_dialog(dialog_para_fechar)
        
        def fechar_dialog(dialog):
            dialog.open = False
            self.page.update()

        def abrir_dialogo_tabela_audio(self, e=None):

            caminho_imagem = "audiometria/audiometria.png"
            with Image.open(os.path.abspath("assets/audiometria/audiometria.png")) as img:
                largura, altura = img.size

            linhas_desenhadas = []
            last_x, last_y = 0, 0

            def pan_start(e: ft.DragStartEvent):
                nonlocal last_x, last_y
                last_x = e.local_x
                last_y = e.local_y

            def pan_update(e: ft.DragUpdateEvent):
                nonlocal last_x, last_y
                linha = ft.canvas.Line(
                    last_x, last_y, e.local_x, e.local_y,
                    paint=ft.Paint(stroke_width=3, color=ft.Colors.RED)
                )
                linhas_desenhadas.append(linha)
                canvas.shapes.append(linha)
                canvas.update()
                last_x = e.local_x
                last_y = e.local_y

            def limpar_canvas(e):
                canvas.shapes.clear()
                linhas_desenhadas.clear()
                canvas.update()

            canvas = ft.canvas.Canvas(
                [],
                width=largura,
                height=altura,
            )

            gesture_detector = ft.GestureDetector(
                content=canvas,
                on_pan_start=pan_start,
                on_pan_update=pan_update,
                drag_interval=2,
                width=largura,
                height=altura,
            )

            stack = ft.Stack(
                controls=[
                    ft.Image(
                src=caminho_imagem,
                width=largura,
                height=altura,
                fit=ft.ImageFit.CONTAIN
            ),
                gesture_detector,
                ],
                width=largura,
                height=altura,
            )

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Tabela Audiometria - Marque as frequências"),
                content=stack,
                actions=[
                    ft.TextButton("Limpar", on_click=lambda:limpar_canvas),
                    ft.TextButton("Fechar", on_click=lambda:fechar_dialog),
                    ft.TextButton("Salvar", on_click=lambda e: salvar_desenho_audiometria(e, linhas_desenhadas, caminho_xlsx, dialog)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.open(dialog)
            self.page.update()

        botao_tabela_audio = ft.ElevatedButton("Tabela Audio", on_click=abrir_dialogo_tabela_audio)

        self.controles_opcoes = []
        for secao, opcoes in self.json_audio.items():
            self.controles_opcoes.append(ft.Text(secao, style="headlineSmall", weight=ft.FontWeight.BOLD))
            grupo_secao = []
            for descricao, dados in opcoes.items():
                tipo = dados.get("tipo", "checkbox")
                celula = dados.get("celula")
                if tipo == "checkbox":
                    controle = ft.Checkbox(label=descricao, value=False)
                elif tipo == "texto":
                    controle = ft.TextField(label=descricao, width=400, multiline=True, max_lines=3)
                else:
                    controle = ft.Text(f"Tipo desconhecido para {descricao}")
                grupo_secao.append((descricao, celula, tipo, controle))
            self.controles_opcoes.append(grupo_secao)

        lista_controles = []
        for item in self.controles_opcoes:
            if isinstance(item, ft.Text):
                lista_controles.append(item)
            else:
                for _, _, _, controle in item:
                    lista_controles.append(controle)

        coluna_opcoes = ft.Column(lista_controles, scroll=ft.ScrollMode.AUTO, height=500)

        def salvar_opcoes(e):
            try:
                wb = openpyxl.load_workbook(str(caminho_xlsx))
                ws = wb.worksheets[0]

                todas_celulas_checkbox = []
                for item in self.controles_opcoes:
                    if isinstance(item, list):
                        for _, celula, tipo, _ in item:
                            if tipo == "checkbox":
                                todas_celulas_checkbox.append(celula)

                imagens_para_remover = []
                for img_excel in ws._images:
                    anchor = img_excel.anchor
                    if isinstance(anchor, str) and anchor in todas_celulas_checkbox:
                        imagens_para_remover.append(img_excel)
                    elif hasattr(anchor, "_from"):
                        col = anchor._from.col + 1
                        row = anchor._from.row + 1
                        cel = openpyxl.utils.get_column_letter(col) + str(row)
                        if cel in todas_celulas_checkbox:
                            imagens_para_remover.append(img_excel)
                for img_excel in imagens_para_remover:
                    ws._images.remove(img_excel)

                for item in self.controles_opcoes:
                    if isinstance(item, list):
                        for descricao, celula, tipo, controle in item:
                            if tipo == "checkbox":
                                if controle.value:
                                    inserir_marcacao_personalizada(ws, celula, caminho_x_img)
                            elif tipo == "texto":
                                texto = controle.value or ""
                                ws[celula] = texto

                wb.save(str(caminho_xlsx))
                dialog_opcoes.open = False
                self.page.update()
            except Exception as ex:
                print(f"Erro ao salvar opções AUDIOMETRIA: {ex}")

        dialog_opcoes = ft.AlertDialog(
            modal=True,
            title=ft.Text("Marcar opções - AUDIOMETRIA"),
            content=coluna_opcoes,
            actions=[
                ft.TextButton("Salvar", on_click=salvar_opcoes),
                ft.TextButton("Cancelar", on_click=lambda e: fechar_dialog(dialog_opcoes)),
                botao_tabela_audio  # botão para abrir o diálogo da tabela audiometria
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dialog_opcoes)
        self.page.update()
        

    def fechar_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def build_content(self):
        main_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Andamentos",
                            size=36,
                            weight=ft.FontWeight.NORMAL,
                            color=ft.Colors.GREY_900,
                            font_family="Roboto"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    height=80
                ),
                ft.Row(
                    [self.search_field],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    height=60
                ),
                self.expansion_list
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=main_content,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=30,
                        padding=30,
                        margin=ft.margin.symmetric(horizontal=20, vertical=20),
                        expand=True,
                        alignment=ft.alignment.top_center
                    )
                ],
                width=self.page.width,
                height=self.page.height,
                alignment=ft.MainAxisAlignment.START
            ),
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.GREY_100),
            expand=True
        )