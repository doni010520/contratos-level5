"""
Funções de formatação de dados
"""


def formatar_moeda_br(valor: float) -> str:
    """
    Formata um valor numérico para o padrão de moeda brasileira (R$)
    
    Args:
        valor: Valor numérico a ser formatado
        
    Returns:
        String formatada como moeda (ex: R$ 1.234,56)
    """
    # Formata com 2 casas decimais
    formatted = f"{valor:,.2f}"
    
    # Substitui ponto por X temporariamente
    formatted = formatted.replace(",", "X")
    # Substitui vírgula (milhar) por ponto
    formatted = formatted.replace(".", ",")
    # Substitui X (decimal) por vírgula
    formatted = formatted.replace("X", ",")
    
    return formatted


def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF para o padrão XXX.XXX.XXX-XX
    
    Args:
        cpf: CPF sem formatação
        
    Returns:
        CPF formatado
    """
    cpf_limpo = cpf.replace(".", "").replace("-", "")
    if len(cpf_limpo) != 11:
        return cpf
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"


def formatar_cep(cep: str) -> str:
    """
    Formata CEP para o padrão XXXXX-XXX
    
    Args:
        cep: CEP sem formatação
        
    Returns:
        CEP formatado
    """
    cep_limpo = cep.replace("-", "")
    if len(cep_limpo) != 8:
        return cep
    return f"{cep_limpo[:5]}-{cep_limpo[5:]}"


def formatar_percentual(valor: float, casas_decimais: int = 2) -> str:
    """
    Formata um valor percentual
    
    Args:
        valor: Valor percentual
        casas_decimais: Número de casas decimais
        
    Returns:
        Percentual formatado (ex: 15,50%)
    """
    return f"{valor:.{casas_decimais}f}%".replace(".", ",")
