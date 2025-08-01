from sqlalchemy import Column, Integer, String, Numeric, Date, Text, TIMESTAMP,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class Empresa(Base):
    __tablename__ = 'empresas'
    
    id = Column(Integer, primary_key=True)
    razao = Column(String(100), nullable=False)
    cnpj = Column(String(18), nullable=False)
    contato = Column(Text)
    endereco = Column(Text)
    municipio = Column(Text)
    criado_em = Column(TIMESTAMP, default=func.now())

class ContaAPagar(Base):
    __tablename__ = 'contas_a_pagar'
    
    id = Column(Integer, primary_key=True)
    descricao = Column(String(50))
    valor = Column(Numeric(10, 2), nullable=False)
    vencimento = Column(String(15))
    status = Column(String(20), default='pendente')
    data_pagamento = Column(String(15))
    criado_em = Column(TIMESTAMP, default=func.now())

class CaixaMensal(Base):
    __tablename__ = 'caixa_mensal'
    
    id = Column(Integer, primary_key=True)
    datarefence = Column(Date, nullable=False)
    descricao = Column(String(50))
    valor = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(TIMESTAMP, default=func.now())

class CaixaDiario(Base):
    __tablename__ = 'caixa_diario'
    
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    descricao = Column(String(50))
    valor = Column(Numeric(10, 2), nullable=False)
    registrado_em = Column(TIMESTAMP, default=func.now())

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    usuario = Column(String(255), unique=True)
    passw = Column(Text, nullable=False)
    salt = Column(Text)
    cargo = Column(String(50), server_default="funcionario")
    apelido = Column(String(50))
    criado_em = Column(TIMESTAMP, server_default=func.now())

class Caixa(Base):
    __tablename__ = 'caixa'
    
    id = Column(Integer, primary_key=True)
    data = Column(Date, default=datetime.date.today, server_default=text('CURRENT_DATE'))
    valor = Column(Numeric(10, 2), nullable=False)
    descricao = Column(String(50), nullable=False)
    type = Column(String(10), default='Entrada')
    registrado_em = Column(TIMESTAMP, default=func.now())

class Agendamentos(Base):
    __tablename__ = 'agendamentos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_empresa = Column(String(255), nullable=False)   
    data_exame = Column(Date, nullable=False)    
    tipo_exame = Column(String(100), nullable=False) 
    criado_em = Column(TIMESTAMP, default=func.now())
    colaborador = Column(String(255), nullable=False)
    