"""
Modelos Pydantic para validação de dados da API de Propostas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any


class ProducaoMensalModel(BaseModel):
    """Dados de produção mensal"""
    mes: Union[int, str] = Field(..., description="Mês (1-12 ou 'média')")
    geracao_total: float = Field(..., ge=0, description="Geração total estimada em kWh")


class RetornoInvestimentoModel(BaseModel):
    """Dados de retorno do investimento por ano"""
    ano: int = Field(..., ge=1, le=25, description="Ano (1-25)")
    saldo: float = Field(..., description="Saldo acumulado")
    economia_mensal: float = Field(..., ge=0, description="Economia média mensal")
    economia_anual: float = Field(..., ge=0, description="Economia anual")


class PropostaRequest(BaseModel):
    """Request para geração de proposta - estrutura plana"""
    nome: str = Field(..., description="Nome do cliente")
    modulos_quantidade: int = Field(..., ge=1, description="Quantidade de módulos")
    especificacoes_modulo: str = Field(..., description="Ex: 620W Mono Honor Solar")
    inversores_quantidade: int = Field(..., ge=1, description="Quantidade de inversores")
    especificacoes_inversores: str = Field(..., description="Ex: SOFAR 20kW AFCI")
    investimento_kit_fotovoltaico: float = Field(..., ge=0, description="Valor do kit")
    investimento_mao_de_obra: float = Field(..., ge=0, description="Valor da mão de obra")
    producao_mensal: List[ProducaoMensalModel]
    retorno_investimento: List[RetornoInvestimentoModel]


class PropostaResponse(BaseModel):
    """Response da geração de proposta"""
    success: bool
    message: str
    pdf_filename: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None
    dados_calculados: Optional[Dict[str, Any]] = None
