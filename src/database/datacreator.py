import psycopg2
from dotenv import load_dotenv
import logging
import os
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
keys = [
    os.getenv("DB_HOSTn"),
    os.getenv("DB_NAMEn"),
    os.getenv("DB_USERn"),
    os.getenv("DB_PASSWORDn"),
    os.getenv("DB_PORTn")
]
localkeys: list[str|None] = [
    os.getenv("DB_HOST"),
    os.getenv("DB_NAME"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD"),
    os.getenv("DB_PORT")
]
def connectlocal(command):
    try:
        conn = psycopg2.connect(
            host=localkeys[0],
            database=localkeys[1],
            user=localkeys[2],
            password=localkeys[3],
            port=localkeys[4]
        )
        cursor = conn.cursor()
        cursor.execute(command)
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except psycopg2.Error as e:
            cursor.close()
            conn.close()
            return f"Erro ao conectar: {str(e)}"
def commitlocal(command) -> tuple[str,int]:
    try:
        conn = psycopg2.connect(
            host=localkeys[0],
            database=localkeys[1],
            user=localkeys[2],
            password=localkeys[3],
            port=localkeys[4]
        )
        cursor = conn.cursor()
        cursor.execute(command)
        conn.commit()
        cursor.close()
        conn.close()
        return f"Sucesso",int(200)
    except psycopg2.Error as e:
            cursor.close()
            conn.close()
            print(e)
            return f"Erro ao cadastrar: {e}",int(150)
def connectremote(command,commit):
    try:
        conn = psycopg2.connect(
            host=keys[0],
            database=keys[1],
            user=keys[2],
            password=keys[3],
            port=keys[4]
        )
        cursor = conn.cursor()
        cursor.execute(command)
        if commit is True:
            conn.commit()
            cursor.close()
            conn.close()
            return print("OK")
        else:
            dados = cursor.fetchall()
            cursor.close()
            conn.close()
            return dados, print("Retornando Consulta sem commit")
    except psycopg2.DatabaseError as e:
            cursor.close()
            conn.close()
            return print(f"Erro ao conectar: {str(e)}")
def dbcreator():
    commitlocal("""
            CREATE TABLE IF NOT EXISTS empresas (
                id SERIAL PRIMARY KEY,
                razao VARCHAR(100) NOT NULL,
                cnpj VARCHAR(18) NOT NULL,
                contato TEXT,
                endereco TEXT,
                criado_em TIMESTAMP DEFAULT NOW()
            )
        """)
    commitlocal("""
            CREATE TABLE IF NOT EXISTS contas_a_pagar (
                id SERIAL PRIMARY KEY,
                descricao VARCHAR(50),
                valor NUMERIC(10, 2) NOT NULL,
                vencimento VARCHAR(15),
                status VARCHAR(20) DEFAULT 'pendente',
                data_pagamento VARCHAR(15),
                criado_em TIMESTAMP DEFAULT NOW()
            )
        """)
    commitlocal("""
            CREATE TABLE IF NOT EXISTS caixa_mensal (
                id SERIAL PRIMARY KEY,
                datarefence DATE NOT NULL,
                descricao VARCHAR(50) ,
                valor NUMERIC(10, 2) NOT NULL,
                criado_em TIMESTAMP DEFAULT NOW()
            )
        """)
    commitlocal("""
            CREATE TABLE IF NOT EXISTS caixa_diario (
                id SERIAL PRIMARY KEY,
                data DATE NOT NULL,
                descricao VARCHAR(50),
                valor NUMERIC(10, 2) NOT NULL,
                registrado_em TIMESTAMP DEFAULT NOW()
            )
        """)
    commitlocal("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(255) UNIQUE,
                passw TEXT NOT NULL,
                salt TEXT,
                criado_em TIMESTAMP DEFAULT NOW()
            )
        """)
    commitlocal("""
        CREATE TABLE IF NOT EXISTS caixa(
            id SERIAL PRIMARY KEY,
            data DATE DEFAULT CURRENT_DATE,
            valor NUMERIC(10,2) NOT NULL,
            descricao VARCHAR(50) NOT NULL,
            type VARCHAR(10) DEFAULT 'Entrada',
            registrado_em TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("DataBase verificada")
