"""
Modelos Pydantic para validação de dados da API de Contratos
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ItemTecnicoContrato(BaseModel):
    """Item técnico do contrato"""
    numero: int = Field(..., description="Número sequencial do item")
    quantidade: str = Field(..., description="Quantidade (ex: 6, 1)")
    descricao: str = Field(..., description="Descrição do item")


class ContratoRequest(BaseModel):
    """Request para geração de contrato"""
    # DADOS DO CLIENTE
    cliente_nome: str = Field(..., description="Nome completo do cliente")
    cliente_cpf: str = Field(..., description="CPF do cliente (formato: xxx.xxx.xxx-xx)")
    cliente_endereco: str = Field(..., description="Endereço completo do cliente")
    cliente_cep: str = Field(..., description="CEP do cliente")
    
    # DADOS DO CONTRATO
    numero_contrato: Optional[str] = Field(None, description="Número do contrato (auto-gerado se omitido)")
    data_contrato: Optional[str] = Field(None, description="Data do contrato (ISO format, hoje se omitida)")
    
    # ESPECIFICAÇÕES TÉCNICAS
    itens_tecnicos: List[ItemTecnicoContrato] = Field(..., description="Lista de itens técnicos")
    descricao_objeto: str = Field(..., description="Descrição completa do objeto/escopo")
    
    # INVESTIMENTO
    valor_material: float = Field(..., ge=0, description="Valor do material/equipamentos")
    valor_mao_obra: float = Field(..., ge=0, description="Valor da mão de obra")
    percentual_entrada_mao_obra: float = Field(default=30, ge=0, le=100, description="% de entrada na mão de obra")
    
    # PRAZOS E GARANTIAS
    prazo_execucao_dias: int = Field(default=40, ge=1, description="Prazo em dias corridos")
    garantia_modulos_anos: int = Field(default=15, description="Garantia dos módulos contra defeitos")
    garantia_performance_anos: int = Field(default=25, description="Garantia de performance dos módulos")
    garantia_inversores_anos: int = Field(default=12, description="Garantia dos inversores")
    garantia_estrutura_anos: int = Field(default=5, description="Garantia da estrutura metálica")
    garantia_instalacao_meses: int = Field(default=12, description="Garantia da instalação em meses")
    
    # INFORMAÇÕES ADICIONAIS
    observacoes: Optional[str] = Field(None, description="Observações/Notas adicionais")
    local_execucao: Optional[str] = Field(None, description="Local de execução (se diferente do endereço)")


class ContratoResponse(BaseModel):
    """Response da geração de contrato"""
    success: bool
    message: str
    pdf_filename: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None
    dados_contrato: Optional[dict] = None
