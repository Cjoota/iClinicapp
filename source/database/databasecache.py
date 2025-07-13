import asyncio
import datetime
import time
import logging
from typing import Dict, Optional, Any
from decimal import Decimal
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, delete
from dotenv import load_dotenv
import os
from database.models import Base, Caixa, CaixaMensal, ContaAPagar, CaixaDiario

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuração do cache"""
    timeout: int = 300  
    max_size: int = 100
    auto_refresh: bool = True

class SmartCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Dict]:
        """Recupera item do cache se válido"""
        if key not in self._cache:
            return None
            
        # Verifica se expirou
        if time.time() - self._timestamps[key] > self.config.timeout:
            self.invalidate(key)
            return None
            
        return self._cache[key]
    
    def set(self, key: str, value: Dict) -> None:
        """Armazena item no cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
        
        # Limpa cache se muito grande
        if len(self._cache) > self.config.max_size:
            self._cleanup_old_entries()
    
    def invalidate(self, key: str) -> None:
        """Remove item do cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self._cache.clear()
        self._timestamps.clear()
    
    def _cleanup_old_entries(self) -> None:
        """Remove entradas mais antigas"""
        sorted_keys = sorted(self._timestamps.items(), key=lambda x: x[1])
        keys_to_remove = [k for k, _ in sorted_keys[:10]]  
        
        for key in keys_to_remove:
            self.invalidate(key)

class ContabilidadeDB:
    
    def __init__(self, cache_config: Optional[CacheConfig] = None):
        _database_url = (
                f"postgresql+asyncpg://{os.getenv('DB_USER')}:"
                f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
                f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
            )
        self.engine = create_async_engine(
                _database_url, 
                echo=False,
                future=True
            )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.cache = SmartCache(cache_config or CacheConfig())
        self._initialized = False
        self._auto_refresh_task = None
    
    async def initialize(self) -> None:

        try:
            self.async_session = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
  
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._initialized = True
            logger.info("Banco inicializado com sucesso")
            

            if self.cache.config.auto_refresh:
                self._auto_refresh_task = asyncio.create_task(
                    self._auto_refresh_loop()
                )
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco: {e}")
            raise


    async def buscar_contas(self):
        async with self.async_session() as session:
            stmt = select(ContaAPagar)
            result = await session.execute(stmt)
            return result.scalars().all()
        
    async def deletar_contas(self,desc):
        try:
            async with self.async_session() as session:
                stmt = delete(ContaAPagar).where(ContaAPagar.descricao==desc)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    async def _executar_diario(self, session: AsyncSession) -> Decimal:

        hoje = datetime.date.today()
        stmt = select(func.coalesce(func.sum(Caixa.valor), 0)).where(
            Caixa.data == hoje
        )
        result = await session.execute(stmt)
        return Decimal(result.scalar())
    
    async def _executar_upmensal(self, session: AsyncSession) -> Decimal:
        stmt = select(func.coalesce(func.sum(CaixaDiario.valor), 0))
        result = await session.execute(stmt)
        return Decimal(result.scalar())
    
    async def _executar_mensal(self, session: AsyncSession) -> Decimal:

        stmt = select(func.coalesce(func.sum(CaixaMensal.valor), 0))
        result = await session.execute(stmt)
        return Decimal(result.scalar())
    
    async def _executar_contas(self, session: AsyncSession) -> Decimal:

        stmt = select(func.coalesce(func.sum(ContaAPagar.valor), 0))
        result = await session.execute(stmt)
        return Decimal(result.scalar())
    
    async def buscar_dados(self, force_update: bool = False) -> Optional[Dict]:
        cache_key = "dados_contabilidade"
        
        # Tenta cache primeiro
        if not force_update:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info("Dados recuperados do cache")
                return cached_data
        
        if not self._initialized:
            await self.initialize()
        
        try:
            async with self.async_session() as session1, \
               self.async_session() as session2, \
               self.async_session() as session3:
        
                resultados = await asyncio.gather(
                    self._executar_diario(session1),
                    self._executar_mensal(session2),
                    self._executar_contas(session3),
                    return_exceptions=True
                )
                

                for i, resultado in enumerate(resultados):
                    if isinstance(resultado, Exception):
                        logger.error(f"Erro na query {i}: {resultado}")
                        return None
                
                dados = {
                    'diario': resultados[0],
                    'mensal': resultados[1],
                    'contas': resultados[2],
                    'ultima_atualizacao': datetime.datetime.now().isoformat(),
                    'cache_hit': False
                }
                

                self.cache.set(cache_key, dados)
                logger.info("Dados atualizados e armazenados no cache")
                
                return dados
                
        except Exception as e:
            logger.error(f'Erro ao buscar dados: {e}')
            return None
    
    async def _auto_refresh_loop(self) -> None:
        """Loop de atualização automática do cache"""
        while True:
            try:
                await asyncio.sleep(self.cache.config.timeout // 2)  
                await self.buscar_dados(force_update=True)
                logger.info("Cache atualizado automaticamente")
            except Exception as e:
                logger.error(f"Erro no refresh automático: {e}")
                await asyncio.sleep(60)
    
    async def invalidar_cache(self) -> None:

        self.cache.clear()
        logger.info("Cache invalidado manualmente")
    
    async def close(self) -> None:

        if self._auto_refresh_task:
            self._auto_refresh_task.cancel()
            
        if self.engine:
            await self.engine.dispose()
            
        logger.info("Conexões fechadas")


contabilidade_db = ContabilidadeDB()

async def diccreate(force_update: bool = False) -> Optional[Dict]:
    return await contabilidade_db.buscar_dados(force_update)

async def inicializar_db() -> None:
    await contabilidade_db.initialize()