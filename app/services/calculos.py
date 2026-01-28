"""
Serviço de Cálculos
Funções auxiliares para cálculos da proposta solar
"""
from typing import List, Tuple, Optional


class CalculoService:
    """Serviço para cálculos relacionados à proposta solar"""
    
    def calcular_investimento_total(
        self,
        kit_fotovoltaico: float,
        mao_de_obra: float
    ) -> float:
        """
        Calcula o investimento total.
        
        Args:
            kit_fotovoltaico: Valor do kit fotovoltaico
            mao_de_obra: Valor da mão de obra, projeto e periféricos
            
        Returns:
            Investimento total
        """
        return kit_fotovoltaico + mao_de_obra
    
    def encontrar_ano_payback(
        self,
        dados_retorno: List
    ) -> Tuple[Optional[int], Optional[float]]:
        """
        Encontra o primeiro ano em que o saldo se torna positivo.
        
        Args:
            dados_retorno: Lista com dados de retorno por ano
            
        Returns:
            Tupla (ano_payback, valor_saldo) ou (None, None) se não encontrado
        """
        for item in dados_retorno:
            if item.saldo > 0:
                return item.ano, item.saldo
        return None, None
    
    def calcular_economia_total(
        self,
        dados_retorno: List
    ) -> float:
        """
        Retorna a economia acumulada no último ano (25 anos).
        
        Args:
            dados_retorno: Lista com dados de retorno por ano
            
        Returns:
            Economia acumulada em 25 anos
        """
        if not dados_retorno:
            return 0.0
        return dados_retorno[-1].saldo
    
    def calcular_potencia_sistema(
        self,
        quantidade_modulos: int,
        potencia_modulo_w: int
    ) -> float:
        """
        Calcula a potência total do sistema em kWp.
        
        Args:
            quantidade_modulos: Quantidade de módulos
            potencia_modulo_w: Potência de cada módulo em Watts
            
        Returns:
            Potência total em kWp
        """
        return (quantidade_modulos * potencia_modulo_w) / 1000
    
    def calcular_geracao_por_placa(
        self,
        geracao_total: float,
        quantidade_modulos: int
    ) -> float:
        """
        Calcula a geração por placa.
        
        Args:
            geracao_total: Geração total em kWh
            quantidade_modulos: Quantidade de módulos
            
        Returns:
            Geração por placa em kWh
        """
        if quantidade_modulos == 0:
            return 0.0
        return geracao_total / quantidade_modulos
