"""
Gerador de Contratos PDF - Level 5 Engenharia Elétrica
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

# Cores do layout
AZUL_ESCURO = HexColor("#1a3a4a")
AZUL_HEADER = HexColor("#3a8a9a")
LARANJA = HexColor("#f5a623")

# Diretório de assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')


def get_asset_path(filename):
    """Retorna o caminho completo de um asset"""
    return os.path.join(ASSETS_DIR, filename)


def draw_header(c, width, height):
    """Desenha o header com logo nas páginas internas"""
    # Faixa azul do header
    c.setFillColor(AZUL_HEADER)
    c.rect(0, height - 45*mm, 120*mm, 45*mm, fill=1, stroke=0)
    
    # Texto "CONTRATO DE PRESTAÇÃO DE SERVIÇO"
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(15*mm, height - 28*mm, "CONTRATO DE PRESTAÇÃO DE SERVIÇO")
    
    # Logo no canto direito
    logo_path = get_asset_path('logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width - 55*mm, height - 40*mm, width=45*mm, height=30*mm, 
                   preserveAspectRatio=True, mask='auto')


def format_cpf(cpf):
    """Formata CPF para exibição"""
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    if len(cpf_clean) == 11:
        return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
    return cpf


def format_currency(value):
    """Formata valor para moeda brasileira"""
    try:
        valor = float(value)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {value}"


def valor_por_extenso(valor):
    """Converte valor numérico para extenso"""
    unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
    dezenas = ['', 'dez', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
    dez_a_dezenove = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
    centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
    
    try:
        valor = float(valor)
    except:
        return ""
    
    inteiro = int(valor)
    centavos = int(round((valor - inteiro) * 100))
    
    def converte_grupo(n):
        if n == 0:
            return ''
        elif n == 100:
            return 'cem'
        elif n < 10:
            return unidades[n]
        elif n < 20:
            return dez_a_dezenove[n - 10]
        elif n < 100:
            d, u = divmod(n, 10)
            if u == 0:
                return dezenas[d]
            return f"{dezenas[d]} e {unidades[u]}"
        else:
            c, resto = divmod(n, 100)
            if resto == 0:
                return 'cem' if c == 1 else centenas[c]
            return f"{centenas[c]} e {converte_grupo(resto)}"
    
    resultado = []
    
    if inteiro >= 1000:
        milhares, resto = divmod(inteiro, 1000)
        if milhares == 1:
            resultado.append("mil")
        else:
            resultado.append(f"{converte_grupo(milhares)} mil")
        inteiro = resto
    
    if inteiro > 0:
        resultado.append(converte_grupo(inteiro))
    
    if not resultado:
        texto_inteiro = "zero reais"
    elif len(resultado) == 2 and resultado[1]:
        texto_inteiro = f"{resultado[0]} {resultado[1]} reais"
    else:
        texto_inteiro = f"{' '.join(resultado)} reais" if resultado else "zero reais"
    
    if centavos > 0:
        texto_centavos = f"{converte_grupo(centavos)} centavo{'s' if centavos > 1 else ''}"
        return f"{texto_inteiro} e {texto_centavos}"
    
    return texto_inteiro


def draw_paragraph(c, text, x, y, width, style, leading=14):
    """Desenha um parágrafo com quebra de linha automática"""
    p = Paragraph(text, style)
    w, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return h


def generate_contract_pdf(data):
    """
    Gera o PDF do contrato
    
    data = {
        'nome': str,
        'cpf': str,
        'endereco': str,
        'bairro': str,
        'cep': str,
        'cidade': str,
        'estado': str,
        'valor_total': float,
        'valor_material': float,
        'valor_mao_obra': float,
        'qtd_modulos': int,
        'potencia_modulo': str (ex: "610 Wp"),
        'marca_modulo': str,
        'potencia_inversor': str (ex: "3,1 kW"),
        'marca_inversor': str,
        'prazo_execucao': int (dias),
        'percentual_entrada': int,
        'data_contrato': str (formato dd/mm/yyyy)
    }
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Estilos de parágrafo
    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle(
        'Normal',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    style_bold = ParagraphStyle(
        'Bold',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # ================== PÁGINA 1 - CAPA ==================
    capa_path = get_asset_path('capa.jpg')
    if os.path.exists(capa_path):
        c.drawImage(capa_path, 0, 0, width=width, height=height)
    else:
        # Fallback se não houver imagem da capa
        c.setFillColor(white)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # Desenha elementos básicos da capa
        c.setFillColor(AZUL_ESCURO)
        c.setFont("Helvetica-Bold", 48)
        c.drawString(50*mm, height - 180*mm, "CONTRATO")
        
        c.setStrokeColor(AZUL_HEADER)
        c.setLineWidth(2)
        c.line(50*mm, height - 185*mm, 160*mm, height - 185*mm)
    
    # Nome do cliente na capa
    c.setFillColor(AZUL_ESCURO)
    c.setFont("Helvetica", 12)
    c.drawString(50*mm, height - 205*mm, "CLIENTE:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50*mm, height - 215*mm, data['nome'].upper())
    
    c.showPage()
    
    # ================== PÁGINA 2 ==================
    draw_header(c, width, height)
    
    y_pos = height - 60*mm
    margin_left = 20*mm
    margin_right = 20*mm
    text_width = width - margin_left - margin_right
    
    # CONTRATANTE
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "CONTRATANTE:")
    y_pos -= 5*mm
    
    endereco_completo = f"{data['endereco']}, {data['bairro']} - CEP {data['cep']}, {data['cidade']}-{data['estado']}"
    texto_contratante = f"<b>{data['nome']}</b>, inscrito no <b>CPF nº {format_cpf(data['cpf'])}</b>, residente na {endereco_completo}"
    
    h = draw_paragraph(c, texto_contratante, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 8*mm
    
    # CONTRATADA
    c.drawString(margin_left, y_pos, "CONTRATADA:")
    y_pos -= 5*mm
    
    texto_contratada = """<b>LEVEL 5 ENGENHARIA ELÉTRICA LTDA</b>, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº <b>57.946.157/0001-21</b>, com sede em Juiz de Fora – MG, doravante denominada "CONTRATADA"."""
    
    h = draw_paragraph(c, texto_contratada, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 5*mm
    
    texto_intro = """As partes acima identificadas celebram o presente Contrato de Compra e Instalação de Sistema de Energia Solar Fotovoltaica, mediante as cláusulas e condições seguintes:"""
    
    h = draw_paragraph(c, texto_intro, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 8*mm
    
    # 1. DO OBJETO
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "1. DO OBJETO")
    y_pos -= 7*mm
    
    texto_objeto_1 = """1.1. O presente contrato tem por objeto a entrega e instalação, pela CONTRATADA, de um sistema de geração de energia solar fotovoltaica, conforme especificações técnicas definidas em proposta previamente aprovada pelo CONTRATANTE."""
    
    h = draw_paragraph(c, texto_objeto_1, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 5*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "1.2. A instalação incluirá, dentre outros serviços:")
    y_pos -= 6*mm
    
    servicos = [
        "Elaboração de projeto com emissão de ART;",
        "Montagem das estruturas e módulos;",
        "Instalação e conexão dos inversores e cabeamentos;",
        "Configuração do sistema e testes operacionais;",
        "Solicitação de acesso junto à distribuidora local."
    ]
    
    for servico in servicos:
        c.drawString(margin_left + 5*mm, y_pos, f"• {servico}")
        y_pos -= 5*mm
    
    y_pos -= 5*mm
    
    # 2. DAS GARANTIAS
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "2. DAS GARANTIAS")
    y_pos -= 7*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "2.1. Os componentes fornecidos possuem as seguintes garantias diretas dos fabricantes:")
    y_pos -= 6*mm
    
    garantias = [
        "Módulos Fotovoltaicos: 15 anos contra defeitos de fabricação e 25 anos quanto à performance;",
        "Inversores: 12 anos;",
        "Estruturas Metálicas: 5 anos contra corrosão e falhas estruturais."
    ]
    
    for garantia in garantias:
        c.drawString(margin_left + 5*mm, y_pos, f"• {garantia}")
        y_pos -= 5*mm
    
    y_pos -= 3*mm
    
    texto_garantia_2 = """2.2. A CONTRATADA oferece garantia de 12 (doze) meses sobre os serviços de instalação, abrangendo vícios de execução e falhas técnicas."""
    h = draw_paragraph(c, texto_garantia_2, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 5*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "2.3. Estão excluídos da garantia:")
    y_pos -= 6*mm
    
    exclusoes = [
        "Danos causados por mau uso, sobrecarga ou alterações não autorizadas;",
        "Intervenções de terceiros não autorizados;",
        "Ocorrências naturais como raios, enchentes, ventos extremos e tempestades;",
        "Obras civis não executadas pela CONTRATADA."
    ]
    
    for exclusao in exclusoes:
        c.drawString(margin_left + 5*mm, y_pos, f"• {exclusao}")
        y_pos -= 5*mm
    
    c.showPage()
    
    # ================== PÁGINA 3 ==================
    draw_header(c, width, height)
    
    y_pos = height - 60*mm
    
    # 3. DO PREÇO E DAS CONDIÇÕES DE PAGAMENTO
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "3. DO PREÇO E DAS CONDIÇÕES DE PAGAMENTO")
    y_pos -= 7*mm
    
    valor_extenso = valor_por_extenso(data['valor_total'])
    texto_valor = f"""3.1. O valor total do presente contrato é de {format_currency(data['valor_total'])} ({valor_extenso}), referentes aos projetos e instalação do sistema fotovoltaico com {data['qtd_modulos']:02d} módulos fotovoltaicos de {data['potencia_modulo']} - {data['marca_modulo']} e 1 inversor de {data['potencia_inversor']} - {data['marca_inversor']}."""
    
    h = draw_paragraph(c, texto_valor, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 5*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "3.2. O pagamento será realizado, conforme se segue:")
    y_pos -= 6*mm
    
    percentual_restante = 100 - data['percentual_entrada']
    pagamentos = [
        f"Material: {format_currency(data['valor_material'])};",
        f"Mão de obra: {format_currency(data['valor_mao_obra'])} sendo {data['percentual_entrada']}% na assinatura do contrato e o restante ao final da instalação."
    ]
    
    for pagamento in pagamentos:
        c.drawString(margin_left + 5*mm, y_pos, f"• {pagamento}")
        y_pos -= 5*mm
    
    y_pos -= 8*mm
    
    # 4. DO PRAZO DE EXECUÇÃO
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "4. DO PRAZO DE EXECUÇÃO")
    y_pos -= 7*mm
    
    texto_prazo = f"""4.1. O prazo estimado para a execução dos serviços é de até {data['prazo_execucao']} ({valor_por_extenso(data['prazo_execucao']).replace(' reais', '').replace(' real', '')}) dias corridos, contados a partir da assinatura deste contrato e da liberação de acesso ao local."""
    
    h = draw_paragraph(c, texto_prazo, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 5*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "4.2. O prazo poderá ser prorrogado em caso de:")
    y_pos -= 6*mm
    
    prorrogacoes = [
        "Condições climáticas adversas;",
        "Atrasos de responsabilidade do CONTRATANTE;",
        "Fatores externos fora do controle da CONTRATADA."
    ]
    
    for item in prorrogacoes:
        c.drawString(margin_left + 5*mm, y_pos, f"• {item}")
        y_pos -= 5*mm
    
    y_pos -= 8*mm
    
    # 5. DAS OBRIGAÇÕES DO CONTRATANTE
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "5. DAS OBRIGAÇÕES DO CONTRATANTE")
    y_pos -= 7*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "5.1. São obrigações do CONTRATANTE:")
    y_pos -= 6*mm
    
    obrigacoes = [
        "Disponibilizar acesso livre e seguro ao local de instalação;",
        "Garantir infraestrutura elétrica e civil compatível com o projeto;",
        "Providenciar rede de internet, se exigida para monitoramento remoto;",
        "Fornecer documentos e autorizações quando necessário para homologação junto à concessionária."
    ]
    
    for obrigacao in obrigacoes:
        texto_obrigacao = f"• {obrigacao}"
        h = draw_paragraph(c, texto_obrigacao, margin_left + 5*mm, y_pos, text_width - 5*mm, style_normal)
        y_pos -= h + 2*mm
    
    y_pos -= 5*mm
    
    # 6. DAS LIMITAÇÕES DE RESPONSABILIDADE
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "6. DAS LIMITAÇÕES DE RESPONSABILIDADE")
    y_pos -= 7*mm
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, "6.1. A CONTRATADA não se responsabiliza por:")
    y_pos -= 6*mm
    
    limitacoes = [
        "Alterações normativas ou exigências adicionais impostas pela concessionária local;",
        "Obras civis, reforços estruturais ou adequações não previstas;",
        "Atrasos provenientes de instituições financeiras, cartórios ou terceiros."
    ]
    
    for limitacao in limitacoes:
        c.drawString(margin_left + 5*mm, y_pos, f"• {limitacao}")
        y_pos -= 5*mm
    
    c.showPage()
    
    # ================== PÁGINA 4 ==================
    draw_header(c, width, height)
    
    y_pos = height - 60*mm
    
    # 7. DA RESCISÃO CONTRATUAL
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "7. DA RESCISÃO CONTRATUAL")
    y_pos -= 7*mm
    
    c.setFont("Helvetica", 10)
    texto_rescisao = """7.1. Este contrato poderá ser rescindido por qualquer das partes, mediante comunicação formal, nas seguintes hipóteses:"""
    h = draw_paragraph(c, texto_rescisao, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 3*mm
    
    hipoteses = [
        "Descumprimento de cláusulas contratuais;",
        "Impossibilidade técnica de execução comprovada;",
        "Inadimplemento por parte do CONTRATANTE."
    ]
    
    for hipotese in hipoteses:
        c.drawString(margin_left + 5*mm, y_pos, f"• {hipotese}")
        y_pos -= 5*mm
    
    y_pos -= 3*mm
    
    texto_multa = """7.2. Em caso de desistência imotivada por parte do CONTRATANTE após o início dos serviços, será devida à CONTRATADA multa compensatória correspondente a 15% (quinze por cento) do valor do contrato."""
    h = draw_paragraph(c, texto_multa, margin_left, y_pos, text_width, style_normal)
    y_pos -= h + 10*mm
    
    # 8. DAS DISPOSIÇÕES FINAIS
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y_pos, "8. DAS DISPOSIÇÕES FINAIS")
    y_pos -= 7*mm
    
    disposicoes = [
        "8.1. Este contrato é celebrado em caráter irrevogável e irretratável, obrigando as partes e seus sucessores a qualquer título.",
        "8.2. Qualquer alteração neste instrumento somente será válida se feita por escrito e assinada por ambas as partes.",
        "8.3. Fica eleito o foro da Comarca de Juiz de Fora – MG para dirimir quaisquer dúvidas ou controvérsias decorrentes do presente contrato, com renúncia de qualquer outro, por mais privilegiado que seja."
    ]
    
    for disposicao in disposicoes:
        h = draw_paragraph(c, disposicao, margin_left, y_pos, text_width, style_normal)
        y_pos -= h + 5*mm
    
    y_pos -= 10*mm
    
    # Data e assinaturas
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y_pos, f"Juiz de Fora – MG, {data['data_contrato']}.")
    y_pos -= 25*mm
    
    # Linha do contratante
    c.drawString(margin_left, y_pos, "CONTRATANTE: _______________________________________")
    y_pos -= 20*mm
    
    # Linha da contratada
    c.drawString(margin_left, y_pos, "CONTRATADA: ________________________________________")
    
    c.save()
    buffer.seek(0)
    return buffer
