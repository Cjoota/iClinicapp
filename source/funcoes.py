from datetime import datetime
import asyncio
import hashlib
import secrets
import re
import psycopg2
import datetime
import logging
from database.datacreator import connectlocal,commitlocal
from database.databasecache import ContabilidadeDB
from database.models import CaixaDiario, CaixaMensal,User,Agendamentos,Empresa
from sqlalchemy.sql import insert, select
from pathlib import Path
import json
import subprocess
import platform
from database.models import Empresa

# Habilitando o sistema de log de erros.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
db = ContabilidadeDB()

class Auth:
    """ 
        AUTENTICAÇÃO DE LOGIN E CADASTRO.
        --------------------------------
        Cadastro: Recebe as credênciais, criptografa a senha em hash e armazena a senha em hash e o salt para descriptografar. \n
        Login: Recebe as credênciais, verifica o hash da senha informada e compara com o hash armazenado, verificando tambem se o usuário existe e contem a mesma senha.
    """

    def hashsenha(self,senha:str,salt=None):
        """ 
            Senha para Hash - sha256
            -
            Transforma a senha em hash gerado em SHA256, retornando a senha criptografada e o salt de descriptografia. \n
            senha: Podendo receber uma string ou objeto. \n
            salt: (OPCIONAL), o salt pode ser gerado pela função ou informado um proprio.
        """
        if salt is None:
            salt = secrets.token_hex(16) 
        senhahash = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return senhahash, salt

    def login(self,usuario,password):
        """ 
            Login
            -
            Recebe as credênciais (user,password).\n
            Transforma a senha em hash e comparada com a senha armazenada no usuário informado 
        """
        result= connectlocal(f"SELECT passw, salt FROM users WHERE usuario= ('{usuario}')")
        if result:
            senhasalva, salt = result[0]
            senhacalculada, _ = self.hashsenha(password, salt)
            return secrets.compare_digest(senhasalva, senhacalculada)
        
        return False
        
    def cadastro(self,user,passw,):
        """ 
            Cadastro
            -
            Recebe as credênciais (user,password).\n
            Analisa a senha para identificar senhas fracas e fora de padrão. \n
            Trabsforma a senha em hash e armazena a senha, o salt para descriptografia e o usuario informado.
            
        """
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

    
def excluir_agendamentos_vencidos():
    try:
        from datetime import datetime
        with db.session() as session:
            qtd = session.query(Agendamentos).filter(
                Agendamentos.data_exame < datetime.now().date()
            ).delete()
            session.commit()
            logger.info(f"{qtd} agendamentos vencidos removidos")
            
    except Exception as e:
        logger.info(f"Erro ao limpar agendamentos: {str(e)}")
        session.rollback()
        return 0

def listar_empresas_com_agendamento():
    with db.session() as session:
        slc = select(Agendamentos)
        result = session.execute(slc).scalars().all()
        return result


def vercontas() :
    """ Seleciona no Banco de dados as informações sobre contas registradas e as retorna. """
    try:
        dados = connectlocal("SELECT descricao,valor,vencimento, data_pagamento, status FROM contas_a_pagar")
        if dados == []:
            return [("-","0,00","-","-","-")]
        else: 
            return dados
    except Exception as e:
        print(f"Erro: {str(e)}")
        return [("SEM CONEXÃO","-","-","-","-")]

def cadasempresa(razao, cnpj, contato, endereco, municipio):
    """ Cadastra uma nova empresa no banco de dados empresarial. """
    try:
        commitlocal(f"INSERT INTO empresas (razao, cnpj, contato, endereco, municipio) VALUES ('{razao}', '{cnpj}', '{contato}', '{endereco}','{municipio}')")
    except psycopg2.DatabaseError as e:
        print(f"Erro ao cadastrar: {str(e)}")

def verempresa():
    """ Seleciona no banco de dados todas as empresas encontradas e registradas. """
    try:
        dados = connectlocal("SELECT razao, cnpj, contato, endereco, municipio FROM empresas")
        return dados
    except psycopg2.DatabaseError as e:
        print(e)
        return ["sem conexão","sem conexão","sem conexão","sem conexão","sem conexão"]
    
def excluiremp(cnpj):
    """ Exclui uma empresas do Banco de dados. """
    try:
        commitlocal(f"DELETE FROM empresas WHERE cnpj='{cnpj}'")
    except psycopg2.DatabaseError as e:
        logging.info(f"Erro ao deletar {e}")

def puxardados(razao):
    """ Seleciona os dados de uma empresa especifica. """
    dt = connectlocal(f"SELECT razao, cnpj, endereco, municipio FROM empresas WHERE razao='{razao}'")
    empresa = []
    for i in dt:
        empresa.append(i[0])
        empresa.append(i[1])
        empresa.append(i[2])
        empresa.append(i[3])
    return empresa

                 

def atualizarempresa(cnpj, coluna, valor):
        if coluna:
            with db.session() as session:
                empresa = session.query(Empresa).filter_by(cnpj=cnpj).first()
                if empresa:
                    match coluna:
                        case "razao":
                            empresa.razao = valor
                        case "contato":
                            empresa.contato = valor
                        case "endereco":
                            empresa.endereco = valor
                        case "municipio":
                            empresa.municipio = valor
                    session.commit()
                else:
                    raise ValueError("Empresa não encontrada com esse CNPJ.")

def converter_xlsx_para_pdf(caminho_xlsx, caminho_pdf):
    """ Converte arquivos ( .xlsx ) para ( .pdf )."""
    if platform.system() == "Windows":
        # Caminho completo para o executável soffice.exe
        libreoffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
    else:
        # No Linux geralmente está no PATH
        libreoffice_path = "libreoffice"

    caminho_arquivo = caminho_xlsx
    pasta_saida = caminho_pdf

    subprocess.run([
        libreoffice_path,
        "--headless",
        "--convert-to", "pdf",
        str(caminho_arquivo),
        "--outdir", str(pasta_saida)
    ], check=True)


def get_cargo(user):
    """ Seleciona o cargo do usuario inserido, no banco de dados. """
    try:
        with db.session() as session:
            slec = select(User).where(User.usuario == user)
            result = session.execute(slec).scalar_one_or_none()
            return result.cargo
    except:
        """  RETIRAR NA MASTER   """
        return "Bypass"
def set_cargo(user:str,cargo:str):
    """ Altera o Cargo do usuario inserido, no banco de dados. """
    with db.session() as session:
        cg = session.query(User).filter_by(usuario=user).first()
        if cg:
            cg.cargo = cargo
            session.commit()
            session.close()
        else:
            logger.info("Usuario não encontrado")
def set_apelido(user:str, apelido:str):
    """ Altera o Apelido inserido no cadastro do usuario. """
    with db.session() as session:
        ap = session.query(User).filter_by(usuario=user).first()
        if ap:
            ap.apelido = apelido
            session.commit()
            session.close()
def get_apelido(user:str):
    """ Seleciona o apelido do usuario registrado no bando de dados. """
    try:
        with db.session() as session:
            slc = session.query(User).filter_by(usuario=user).first()
            result = slc.apelido 
            session.close()
            return result
    except:
        """  RETIRAR NA MASTER   """
        return "Bypass"
class Verificacoes:
    """VERIFICAÇÕES DE ESTADO \n -
    Verifica o estado do banco de dados e dos uploads do caixa para nuvem.
    - init_config:\n 
        Seta as configuraçoes iniciais do sistema.\n


    - get_config:\n
        Puxa os dados armazenados dos estados das verificações.\n

    
    - set_config:\n
        Altera os dados armazenados dos estados.\n

    
    - close:\n
        Retorna os dados ao padrão.\n

    
    - Uptable / Updiario:\n  
        Sobe o registro do mes para o banco de dados / sobe o registro diario para o registro do mês.\n

     """
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
        """ seta os estados para as configurações.\n
         parametros:\n
            config: qual verificação quer setar (v: verificado hoje, m: executado o up mensal, d: executado o up diario)\n
            set: qual o valor salvar. """
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
        """ Retorna o valor da configuração informada.\n
        parametros:\n
            config: qual verificação quer pegar: (v: verificado hoje, m: executado o up mensal, d: executado o up diario)\n
        """
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
    


