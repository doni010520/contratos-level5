"""
Serviço para geração de gráficos e tabelas
"""
import matplotlib.pyplot as plt
import matplotlib
import io
from typing import List, Dict
import uuid

matplotlib.use('Agg')


class GraficoService:
    """Serviço para geração de gráficos e tabelas de propostas"""
    
    def gerar_grafico_producao(self, dados_producao: List[Dict], quantidade_modulos: int, output_dir: str) -> str:
        """
        Gera gráfico de produção mensal de energia
        
        Args:
            dados_producao: Lista com dados de produção mensal
            quantidade_modulos: Quantidade de módulos (para cálculo por módulo)
            output_dir: Diretório de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            # Preparar dados
            meses = []
            producoes = []
            
            for item in dados_producao:
                if item.mes != 'média':
                    meses.append(self._mes_numero_para_nome(item.mes))
                    producoes.append(item.geracao_total)
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(meses, producoes, color='#16A085', edgecolor='#336777', linewidth=1.5)
            ax.set_ylabel('Geração (kWh)', fontsize=11, fontweight='bold')
            ax.set_title('Produção Mensal Estimada', fontsize=13, fontweight='bold', color='#336777')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Salvar
            filename = f"grafico_producao_{uuid.uuid4().hex[:8]}.png"
            filepath = f"{output_dir}/{filename}"
            fig.tight_layout()
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            return filepath
        except Exception as e:
            print(f"Erro ao gerar gráfico: {str(e)}")
            return ""
    
    def gerar_tabela_retorno(self, dados_retorno: List[Dict], output_dir: str) -> str:
        """
        Gera tabela de retorno do investimento
        
        Args:
            dados_retorno: Lista com dados de retorno por ano
            output_dir: Diretório de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            # Preparar dados (amostra a cada 5 anos)
            anos = []
            saldos = []
            
            for i, item in enumerate(dados_retorno):
                if i % 5 == 0 or item.ano == dados_retorno[-1].ano:
                    anos.append(f"Ano {item.ano}")
                    saldos.append(f"R$ {item.saldo:,.2f}")
            
            # Criar figura com tabela
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.axis('tight')
            ax.axis('off')
            
            table_data = [['Período', 'Saldo Acumulado']]
            for ano, saldo in zip(anos, saldos):
                table_data.append([ano, saldo])
            
            table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                           colWidths=[0.4, 0.6])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            
            # Estilo
            for i in range(len(table_data)):
                for j in range(2):
                    cell = table[(i, j)]
                    if i == 0:
                        cell.set_facecolor('#336777')
                        cell.set_text_props(weight='bold', color='white')
                    else:
                        cell.set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
            
            # Salvar
            filename = f"tabela_retorno_{uuid.uuid4().hex[:8]}.png"
            filepath = f"{output_dir}/{filename}"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            return filepath
        except Exception as e:
            print(f"Erro ao gerar tabela: {str(e)}")
            return ""
    
    def _mes_numero_para_nome(self, mes: int) -> str:
        """Converte número do mês para nome"""
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        return meses[mes - 1] if 1 <= mes <= 12 else str(mes)
