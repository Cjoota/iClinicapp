import asyncio
import hashlib
import secrets
import re
import comtypes.client
import os
from database.datacreator import keys
import psycopg2
import datetime
import locale
import logging
from database.datacreator import connectlocal,commitlocal
from database.databasecache import ContabilidadeDB
from database.models import CaixaDiario, CaixaMensal
from sqlalchemy.sql import insert
from pathlib import Path
import json
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Auth:
    def __init__(self):
        pass

    def hashsenha(self,senha,salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        senhahash = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return senhahash, salt

    def login(self,usuario,password):
        result= connectlocal(f"SELECT passw, salt FROM users WHERE usuario= ('{usuario}')")
        if result:
            senhasalva, salt = result[0]
            senhacalculada, _ = self.hashsenha(password, salt)
            
            return secrets.compare_digest(senhasalva, senhacalculada)
        
        return False
        
    def cadastro(self,user,passw):
        if len(passw) < 8 or not re.search(r'[A-Z]', passw) or not re.search(r'[0-9]', passw):
            return "Senha deve ter pelo menos 8 caracteres, uma letra maiúscula e um número.", 150
        senhahash, salt = self.hashsenha(passw)
        try:
            qr = commitlocal(f"INSERT INTO users (usuario, passw, salt) VALUES ('{user}', '{senhahash}', '{salt}')")
            return qr
        except psycopg2.IntegrityError:
            return "Usuário Invalido.", 150
        except Exception as e:
            return f"Erro ao cadastrar: {str(e)}", 150
        
def inserirmensal(valor,desc):
    data = datetime.datetime.now().strftime("%d-%m-%Y")
    try:
        conn = psycopg2.connect(
            host=keys[0],
            database=keys[1],
            user=keys[2],
            password=keys[3],
            port=keys[4])
        cursor = conn.cursor()
        cursor.execute("INSERT INTO caixa_mensal (data, valor, descricao) VALUES (%s, %s, %s)", (data, valor, desc))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.DatabaseError as e:
        conn.close()
        cursor.close()
        return False, f"Erro ao Introduzir: {str(e)}"

def consultamensal():
    try:
        valmensal = connectlocal("SELECT SUM(valor) FROM caixa_mensal")
        valores = re.findall(r"'(.*?)'", str(valmensal[0]))
        if valores == []:
            return "R$ 0,00"
        else:
            valores = float(valores[0])
            valores = locale.currency(valores, grouping=True)
            return valores
    except psycopg2.Error:
        return "Falha ao conectar"

def inserirdiario(valor,desc):
    try:    
        ms =  commitlocal(F"INSERT INTO caixa (valor, descricao) VALUES ('{valor}','{desc}')")
        return ms
    except Exception as e:
        print(str(e))
   

def retirardiario(valor,desc):
   ms =  commitlocal(F"INSERT INTO caixa (valor, descricao, type) VALUES ('{-valor}','{desc}','Saida')")
   return ms

def consultadiaria():
    try:
        data = datetime.datetime.now().strftime("%Y-%m-%d")
        condiaria = connectlocal(f"SELECT SUM(valor) FROM caixa WHERE data='{data}'")
        condiaria = re.findall(r"'(.*?)'", str(condiaria[0]))
        if condiaria:
            valor = condiaria
            if valor == []:
                valor = "R$ 0,00"
                return valor
            else:
                valor = float(valor[0])
                valor = locale.currency(valor, grouping=True)
                return valor
        else:
            return "R$ 0,00"
    except Exception as e:
        print(str(e))
        return "Falha na conexão"

def inserircontas(desc,valor,venc,status, datapg):
    try:
        commitlocal(f"INSERT INTO contas_a_pagar (descricao, valor, vencimento, status, data_pagamento) VALUES ('{desc}', '{valor}', '{venc}', '{status}', '{datapg}')")
    except psycopg2.Error as e:
        return False, print(f"Erro ao Introduzir: {e}")

def consultacontas():
    try:
        valapagar = connectlocal("SELECT SUM(valor) FROM contas_a_pagar")
        valapagar = re.findall(r"'(.*?)'", str(valapagar[0]))
        if valapagar == []:
            valor_total = 0.0
            valores = locale.currency(valor_total, grouping=True)
            return valores
        else:
            valor_total = float(valapagar[0]) if valapagar and valapagar[0] is not None else 0.0
            valores = locale.currency(valor_total, grouping=True)
            return valores
    except psycopg2.DatabaseError as e:
        return "Falha de DB!"

def vercontas() :
    try:
        dados = connectlocal("SELECT descricao,valor,vencimento, data_pagamento, status FROM contas_a_pagar")
        if dados == []:
            return [("-","0,00","-","-","-")]
        else: 
            return dados
    except Exception as e:
        print(f"Erro: {str(e)}")
        return [("SEM CONEXÃO","-","-","-","-")]

def excluirconta(desc):
    try:
        commitlocal(f"DELETE FROM contas_a_pagar WHERE descricao='{desc}'")
        return True
    except psycopg2.DatabaseError as e:
        return False, print(f"Erro ao deletar: {e}")

def cadasempresa(razao, cnpj, contato, endereco, municipio):
    try:
        commitlocal(f"INSERT INTO empresas (razao, cnpj, contato, endereco, municipio) VALUES ('{razao}', '{cnpj}', '{contato}', '{endereco}','{municipio}')")
    except psycopg2.DatabaseError as e:
        print(f"Erro ao cadastrar: {str(e)}")

def verempresa():
    try:
        dados = connectlocal("SELECT razao, cnpj, contato, endereco, municipio FROM empresas")
        return dados
    except psycopg2.DatabaseError as e:
        print(e)
        return ["sem conexão","sem conexão","sem conexão","sem conexão","sem conexão"]
    
def excluiremp(cnpj):
    try:
        commitlocal(f"DELETE FROM empresas WHERE cnpj='{cnpj}'")
    except psycopg2.DatabaseError as e:
        logging.info(f"Erro ao deletar {e}")

def puxardados(razao):
   dt = connectlocal(f"SELECT (cnpj) FROM empresas WHERE razao='{razao}'")
   return dt


class Verificacoes:
    def __init__(self):
        self.db = ContabilidadeDB()
        self.init_config()
        self.executado_hoje = False


    def init_config(self):
        dados_iniciais = {
            "verificado_hoje": False,
            "executado_hoje_mensal": False,
            "executado_hoje_diario": False
        }
        verify = Path("verify.json")
        if not verify.exists():
            with open("verify.json", "w", encoding="utf-8") as f:
                json.dump(dados_iniciais, f, ensure_ascii=False, indent=4)
        del dados_iniciais

    def close(self):
        dados = {
            "verificado_hoje": False,
            "executado_hoje_mensal": False,
            "executado_hoje_diario": False
        }
        with open("verify.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)

    def set_config(self,config:str, set:bool):
        verify = Path("verify.json")
        if verify.exists():
            with open("verify.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
            match config:
                case "v":
                    dados["verificado_hoje"] = set
                case "m":
                    dados["executado_hoje_mensal"] = set
                case "d":
                    dados["executado_hoje_diario"] = set
                case None:
                    pass
            with open("verify.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)

    def get_config(self,config:str) -> bool:
        verify = Path("verify.json")
        if verify.exists():
            with open("verify.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
            match config:
                case "v":
                    return dados["verificado_hoje"]
                case "m":
                    return dados["executado_hoje_mensal"]
                case "d":
                    return dados["executado_hoje_diario"]
        return True
    
    async def uptable(self):
        if not self.get_config("v"):
            hoje = datetime.datetime.now().strftime("%d")
            if hoje == "01":
                if not self.get_config("e"):
                    date = datetime.datetime.now()
                    valores = await self.db._executar_upmensal(self.db.async_session())
                    async with self.db.async_session() as session:
                        _isrt_ = insert(CaixaMensal).values(datarefence=datetime.datetime.date(date),descricao='Fecha de mensal automatico',valor=valores)
                        await session.execute(_isrt_)
                        await session.commit() 
                        await session.close()
                    logging.info("Renda Mensal Disponível!")
                    self.set_config("v",True)
                    self.set_config("m",True)
            else:
                self.set_config("v",True)
                logging.info("O Mês não terminou!")
                del hoje
            


    async def updiario(self):
        try:          
            date = datetime.datetime.now()
            caixa = await self.db._executar_diario(self.db.async_session())
            async with self.db.async_session() as session:
                _isrt_ = insert(CaixaDiario).values(data=datetime.datetime.date(date),descricao='Fecha de caixa automático',valor=caixa)
                await session.execute(_isrt_)
                await session.commit()
                await session.close()
            logging.info("Caixa Diario Registrado")
        except Exception as e:
            logging.info(f"Erro inesperado no Banco de Dados!: {str(e)}")
        except ValueError as v:
            logging.info(f"Erro inesperado de VALORES: {str(v)}")
        except Exception as ex:
            logging.info(f"Erro INESPERADO: {str(ex)}")
        finally:
            del date
            del caixa
            del _isrt_

    async def verify(self):
        while True:
            agora = datetime.datetime.now()
            hora_atual = agora.time()

            
            if datetime.time(18, 0) <= hora_atual <= datetime.time(18, 1) and not self.get_config("d"):
                logging.info(f"São 18h! Executando upload para DB... {agora}")
                await self.updiario()
                self.set_config("d",True)

            

            
            await asyncio.sleep(30)

def converter_xlsx_para_pdf(caminho_xlsx, caminho_pdf):
    excel = None
    workbook = None
    try:
        caminho_xlsx_abs = os.path.abspath(caminho_xlsx)
        caminho_pdf_abs = os.path.abspath(caminho_pdf)
        if not os.path.exists(caminho_xlsx_abs):
            print(f"Arquivo não encontrado: {caminho_xlsx_abs}")
            return False
        os.makedirs(os.path.dirname(caminho_pdf_abs), exist_ok=True)
        if os.path.exists(caminho_pdf_abs):
            os.remove(caminho_pdf_abs)
        excel = comtypes.client.CreateObject("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False  
        workbook = excel.Workbooks.Open(caminho_xlsx_abs)
        workbook.ExportAsFixedFormat(
            Type=0,  
            Filename=caminho_pdf_abs,
            Quality=1,  
            IgnorePrintAreas=False,
            OpenAfterPublish=False
        )
        print("Conversão concluída!")
        return True
    except Exception as e:
        print(f"Erro ao converter para PDF: {e}")
        return False
    finally:
        try:
            if workbook:
                workbook.Close(SaveChanges=False)
        except:
            pass
        try:
            if excel:
                excel.Quit()
        except:
            pass