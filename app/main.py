"""
API para Geração de Propostas e Contratos Comerciais Solar
Level5 Engenharia Elétrica

Porta: 3493
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import os
import uuid
from datetime import datetime, date

from app.models.proposta import PropostaRequest, PropostaResponse
from app.models.contrato import ContratoRequest, ContratoResponse
from app.services.pdf_generator import PDFGenerator
from app.services.graficos import GraficoService

app = FastAPI(
    title="API Gerador de Propostas e Contratos Solar",
    description="API para geração automática de propostas comerciais e contratos para sistemas fotovoltaicos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "/tmp/propostas"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {
        "api": "Gerador de Propostas e Contratos Solar",
        "versao": "1.0.0",
        "status": "online"
    }


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# ROTAS DE PROPOSTA (já existentes)
# ============================================================

@app.post("/api/v1/proposta/gerar", response_model=PropostaResponse)
async def gerar_proposta(request: PropostaRequest):
    try:
        grafico_service = GraficoService()
        pdf_generator = PDFGenerator()
        
        investimento_total = request.investimento_kit_fotovoltaico + request.investimento_mao_de_obra
        
        ano_payback = None
        valor_payback = None
        for item in request.retorno_investimento:
            if item.saldo > 0:
                ano_payback = item.ano
                valor_payback = item.saldo
                break
        
        economia_25_anos = request.retorno_investimento[-1].saldo if request.retorno_investimento else 0
        
        grafico_producao_path = grafico_service.gerar_grafico_producao(
            dados_producao=request.producao_mensal,
            quantidade_modulos=request.modulos_quantidade,
            output_dir=OUTPUT_DIR
        )
        
        tabela_retorno_path = grafico_service.gerar_tabela_retorno(
            dados_retorno=request.retorno_investimento,
            output_dir=OUTPUT_DIR
        )
        
        nome_arquivo = f"proposta_{request.nome.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, nome_arquivo)
        
        pdf_generator.gerar_proposta_plana(
            nome_cliente=request.nome,
            modulos_quantidade=request.modulos_quantidade,
            especificacoes_modulo=request.especificacoes_modulo,
            inversores_quantidade=request.inversores_quantidade,
            especificacoes_inversores=request.especificacoes_inversores,
            investimento_kit=request.investimento_kit_fotovoltaico,
            investimento_mao_de_obra=request.investimento_mao_de_obra,
            investimento_total=investimento_total,
            grafico_producao_path=grafico_producao_path,
            tabela_retorno_path=tabela_retorno_path,
            ano_payback=ano_payback,
            valor_payback=valor_payback,
            economia_25_anos=economia_25_anos,
            output_path=pdf_path
        )
        
        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        if os.path.exists(grafico_producao_path):
            os.remove(grafico_producao_path)
        if os.path.exists(tabela_retorno_path):
            os.remove(tabela_retorno_path)
        
        return PropostaResponse(
            success=True,
            message="Proposta gerada com sucesso",
            pdf_filename=nome_arquivo,
            pdf_url=f"/api/v1/download/{nome_arquivo}",
            pdf_base64=pdf_base64,
            dados_calculados={
                "investimento_total": investimento_total,
                "ano_payback": ano_payback,
                "valor_payback": valor_payback,
                "economia_25_anos": economia_25_anos
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar proposta: {str(e)}")


# ============================================================
# ROTAS DE CONTRATO (novas)
# ============================================================

@app.post("/api/v1/contrato/gerar", response_model=ContratoResponse)
async def gerar_contrato(request: ContratoRequest):
    """
    Gera um contrato de prestação de serviço para sistema fotovoltaico
    """
    try:
        pdf_generator = PDFGenerator()
        
        # Preparar dados
        numero_contrato = request.numero_contrato or f"LEVEL5-{uuid.uuid4().hex[:8].upper()}"
        data_contrato = request.data_contrato or date.today().strftime("%d de %B de %Y")
        
        # Converter data se necessário
        if request.data_contrato and "T" in request.data_contrato:
            # Se vier em ISO format
            data_obj = datetime.fromisoformat(request.data_contrato)
            meses_br = {
                1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
                5: "maio", 6: "junho", 7: "julho", 8: "agosto",
                9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
            }
            data_contrato = f"{data_obj.day:02d} de {meses_br[data_obj.month]} de {data_obj.year}"
        
        # Calcular investimento total
        investimento_total = request.valor_material + request.valor_mao_obra
        
        nome_arquivo = f"contrato_{request.cliente_nome.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, nome_arquivo)
        
        # Converter itens técnicos para lista de dicts
        itens_list = [
            {
                'numero': item.numero,
                'quantidade': item.quantidade,
                'descricao': item.descricao
            }
            for item in request.itens_tecnicos
        ]
        
        # Gerar PDF
        pdf_generator.gerar_contrato(
            cliente_nome=request.cliente_nome,
            cliente_cpf=request.cliente_cpf,
            cliente_endereco=request.cliente_endereco,
            cliente_cep=request.cliente_cep,
            numero_contrato=numero_contrato,
            data_contrato=data_contrato,
            itens_tecnicos=itens_list,
            descricao_objeto=request.descricao_objeto,
            valor_material=request.valor_material,
            valor_mao_obra=request.valor_mao_obra,
            percentual_entrada_mao_obra=request.percentual_entrada_mao_obra,
            prazo_execucao_dias=request.prazo_execucao_dias,
            garantia_modulos_anos=request.garantia_modulos_anos,
            garantia_performance_anos=request.garantia_performance_anos,
            garantia_inversores_anos=request.garantia_inversores_anos,
            garantia_estrutura_anos=request.garantia_estrutura_anos,
            garantia_instalacao_meses=request.garantia_instalacao_meses,
            observacoes=request.observacoes,
            local_execucao=request.local_execucao,
            output_path=pdf_path
        )
        
        # Ler e codificar em base64
        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        return ContratoResponse(
            success=True,
            message="Contrato gerado com sucesso",
            pdf_filename=nome_arquivo,
            pdf_url=f"/api/v1/download/{nome_arquivo}",
            pdf_base64=pdf_base64,
            dados_contrato={
                "numero_contrato": numero_contrato,
                "data_contrato": data_contrato,
                "cliente_nome": request.cliente_nome,
                "cliente_cpf": request.cliente_cpf,
                "investimento_total": investimento_total,
                "valor_material": request.valor_material,
                "valor_mao_obra": request.valor_mao_obra,
                "percentual_entrada": request.percentual_entrada_mao_obra,
                "prazo_dias": request.prazo_execucao_dias
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar contrato: {str(e)}")


@app.get("/api/v1/contrato/template")
async def get_template_contrato():
    """
    Retorna um exemplo completo de request para geração de contrato
    Útil para documentação e testes
    """
    return {
        "exemplo_request": {
            "cliente_nome": "Paulo Roberto Barreto",
            "cliente_cpf": "198.585.316-72",
            "cliente_endereco": "Rua I, Granja 32F, Parque das Colinas",
            "cliente_cep": "36120-000",
            "numero_contrato": "LEVEL5-2025-001",
            "data_contrato": "2025-01-28",
            "itens_tecnicos": [
                {
                    "numero": 1,
                    "quantidade": "6",
                    "descricao": "Módulos Fotovoltaicos 610Wp - DMEGC"
                },
                {
                    "numero": 2,
                    "quantidade": "1",
                    "descricao": "Inversor 3,1 kW - Sofar"
                }
            ],
            "descricao_objeto": "Entrega e instalação de um sistema de geração de energia solar fotovoltaica, conforme especificações técnicas.",
            "valor_material": 6311.53,
            "valor_mao_obra": 4200.00,
            "percentual_entrada_mao_obra": 30,
            "prazo_execucao_dias": 40,
            "garantia_modulos_anos": 15,
            "garantia_performance_anos": 25,
            "garantia_inversores_anos": 12,
            "garantia_estrutura_anos": 5,
            "garantia_instalacao_meses": 12,
            "observacoes": "Projeto sujeito à aprovação da concessionária de energia local."
        },
        "descricao_campos": {
            "cliente_nome": "Nome completo do cliente",
            "cliente_cpf": "CPF do cliente (formato: xxx.xxx.xxx-xx)",
            "cliente_endereco": "Endereço completo",
            "cliente_cep": "CEP do cliente",
            "numero_contrato": "Número único do contrato (auto-gerado se omitido)",
            "data_contrato": "Data do contrato (ISO format ou deixar em branco para usar hoje)",
            "itens_tecnicos": "Lista de itens com numero, quantidade e descrição",
            "descricao_objeto": "Descrição do escopo do contrato",
            "valor_material": "Valor dos equipamentos/materiais em reais",
            "valor_mao_obra": "Valor da mão de obra em reais",
            "percentual_entrada_mao_obra": "Percentual de entrada (0-100)",
            "prazo_execucao_dias": "Prazo em dias corridos",
            "garantia_*_anos": "Períodos de garantia em anos",
            "garantia_instalacao_meses": "Período de garantia da instalação em meses"
        }
    }


# ============================================================
# ROTA DE DOWNLOAD (para ambas propostas e contratos)
# ============================================================

@app.get("/api/v1/download/{filename}")
async def download_proposta(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(path=file_path, filename=filename, media_type="application/pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3493)
