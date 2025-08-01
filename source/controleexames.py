
import datetime
from pathlib import Path
from openpyxl import load_workbook
import json
import shutil
class ControleExames:
    def __init__(self, pasta_export="exportados"):
        self.raiz = Path("relacoes")
        self.raiz_modelos = Path(r"relacoes/modelos")
        self.modelo = Path(r"relacoes/modelos/relacao.xlsx")
        self.json = Path("Relacao_empresas.json")
        self.pasta_export = Path(pasta_export)
        if not self.raiz.exists():
            self.raiz.mkdir(exist_ok=True)
        if not self.raiz_modelos.exists():
            self.raiz_modelos.mkdir(exist_ok=True)
        if not self.pasta_export.exists():
            self.pasta_export.mkdir(exist_ok=True)
        if datetime.datetime.now().day == 1:
            self.fechar_mes()
        self.init_json()


    def init_json(self):   
        dados = {} 
        if not self.json.exists():
            with open("Relacao_empresas.json", "w",encoding="utf-8") as f:
                json.dump(dados,f,indent=4,ensure_ascii=False)

    def _carregar_json(self,empresa):
        try:
            caminho = Path("Relacao_empresas.json")
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados[empresa]
        except:
            self._salvar_json(empresa,6)
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados[empresa]


    def _salvar_json(self,empresa,value):
        with open("Relacao_empresas.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados[empresa] = value
        with open("Relacao_empresas.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
 

    def _criar_planilha(self,empresa:str):
        wb = load_workbook(self.modelo)
        ws = wb.active
        ws["B2"] = empresa
        empresa_arquivo = f"{empresa}_{datetime.datetime.now().strftime("%m-%Y")}.xlsx"
        saida = Path("relacoes")
        wb.save(fr"{saida}/{empresa_arquivo}")

    def registrar_exames(self, empresa: str, nome: str, exames: list[str], data_exame: str):
        relacao = Path(rf"relacoes/{empresa}_{datetime.datetime.now().strftime("%m-%Y")}.xlsx")
        if not relacao.exists():
            self._criar_planilha(empresa)
            self._salvar_json(empresa,6)
        wb = load_workbook(relacao)
        ws = wb.active
        inicial_value = self._carregar_json(empresa)
        while True:
            ws[f"B{inicial_value}"] = nome
            ws[f"D{inicial_value}"] = f"{exames}".replace("[","").replace("]","").replace("'","").replace("'","")
            ws[f"K{inicial_value}"]= data_exame
            self._salvar_json(empresa,inicial_value+1)
            break
        wb.save(relacao)

    def fechar_mes(self):
        data_atual = datetime.datetime.now()
        if data_atual.day != 1:
            return  # só executa se for dia 1 do mês

        if not self.json.exists():
            return

        with open(self.json, "r", encoding="utf-8") as f:
            empresas_json = json.load(f)

        for empresa in empresas_json:
            nome_arquivo_atual = f"{empresa}_{data_atual.strftime('%m-%Y')}.xlsx"
            caminho_arquivo_atual = Path("relacoes") / nome_arquivo_atual

            if caminho_arquivo_atual.exists():
                destino = self.pasta_export / nome_arquivo_atual

            
                shutil.move(str(caminho_arquivo_atual), str(destino))

            self._criar_planilha(empresa)
            self._salvar_json(empresa, 5)