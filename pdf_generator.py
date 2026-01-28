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
    header_height = 20*mm
    
    c.setFillColor(AZUL_HEADER)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10*mm, height - 13*mm, "CONTRATO DE PRESTAÇÃO DE SERVIÇO")
    
    c.setFillColor(white)
    c.rect(width - 60*mm, height - header_height, 60*mm, header_height, fill=1, stroke=0)
    
    logo_path = get_asset_path('logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width - 55*mm, height - 18*mm, width=50*mm, height=15*mm, 
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


def draw_paragraph(c, text, x, y, width, style):
    """Desenha um parágrafo com quebra de linha automática"""
    p = Paragraph(text, style)
    w, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return h


def generate_contract_pdf(data):
    """Gera o PDF do contrato"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    style_normal = ParagraphStyle(
        'Normal',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    margin_left = 20*mm
    margin_bottom = 20*mm
    text_width = width - margin_left - 20*mm
    
    # Espaçamentos REDUZIDOS
    LH = 4*mm  # Line height padrão
    
    # ================== PÁGINA 1 - CAPA ==================
    capa_path = get_asset_path('capa.png')
    if os.path.exists(capa_path):
        c.drawImage(capa_path, 0, 0, width=width, height=height)
    else:
        capa_path = get_asset_path('capa.jpg')
        if os.path.exists(capa_path):
            c.drawImage(capa_path, 0, 0, width=width, height=height)
        else:
            c.setFillColor(white)
            c.rect(0, 0, width, height, fill=1, stroke=0)
    
    c.setFillColor(AZUL_ESCURO)
    c.setFont("Helvetica", 12)
    c.drawString(50*mm, height - 235*mm, "CLIENTE:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50*mm, height - 245*mm, data['nome'].upper())
    
    c.showPage()
    
    # ================== PÁGINA 2 ==================
    draw_header(c, width, height)
    y = height - 28*mm
    
    # CONTRATANTE
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "CONTRATANTE:")
    y -= LH
    
    endereco = f"{data['endereco']}, {data['bairro']} - CEP {data['cep']}, {data['cidade']}-{data['estado']}"
    txt = f"<b>{data['nome']}</b>, inscrito no <b>CPF nº {format_cpf(data['cpf'])}</b>, residente na {endereco}"
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH
    
    # CONTRATADA
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "CONTRATADA:")
    y -= LH
    
    txt = """<b>LEVEL 5 ENGENHARIA ELÉTRICA LTDA</b>, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº <b>57.946.157/0001-21</b>, com sede em Juiz de Fora – MG, doravante denominada "CONTRATADA"."""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    txt = """As partes acima identificadas celebram o presente Contrato de Compra e Instalação de Sistema de Energia Solar Fotovoltaica, mediante as cláusulas e condições seguintes:"""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH
    
    # 1. DO OBJETO
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "1. DO OBJETO")
    y -= LH
    
    txt = """1.1. O presente contrato tem por objeto a entrega e instalação, pela CONTRATADA, de um sistema de geração de energia solar fotovoltaica, conforme especificações técnicas definidas em proposta previamente aprovada pelo CONTRATANTE."""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "1.2. A instalação incluirá, dentre outros serviços:")
    y -= LH
    
    for s in ["Elaboração de projeto com emissão de ART;", "Montagem das estruturas e módulos;", 
              "Instalação e conexão dos inversores e cabeamentos;", "Configuração do sistema e testes operacionais;",
              "Solicitação de acesso junto à distribuidora local."]:
        c.drawString(margin_left + 5*mm, y, f"• {s}")
        y -= LH
    
    y -= LH * 0.5
    
    # 2. DAS GARANTIAS
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "2. DAS GARANTIAS")
    y -= LH
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "2.1. Os componentes fornecidos possuem as seguintes garantias diretas dos fabricantes:")
    y -= LH
    
    for g in ["Módulos Fotovoltaicos: 15 anos contra defeitos de fabricação e 25 anos quanto à performance;",
              "Inversores: 12 anos;", "Estruturas Metálicas: 5 anos contra corrosão e falhas estruturais."]:
        c.drawString(margin_left + 5*mm, y, f"• {g}")
        y -= LH
    
    txt = """2.2. A CONTRATADA oferece garantia de 12 (doze) meses sobre os serviços de instalação, abrangendo vícios de execução e falhas técnicas."""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "2.3. Estão excluídos da garantia:")
    y -= LH
    
    for e in ["Danos causados por mau uso, sobrecarga ou alterações não autorizadas;",
              "Intervenções de terceiros não autorizados;",
              "Ocorrências naturais como raios, enchentes, ventos extremos e tempestades;",
              "Obras civis não executadas pela CONTRATADA."]:
        c.drawString(margin_left + 5*mm, y, f"• {e}")
        y -= LH
    
    c.showPage()
    
    # ================== PÁGINA 3 ==================
    draw_header(c, width, height)
    y = height - 28*mm
    
    # 3. DO PREÇO
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "3. DO PREÇO E DAS CONDIÇÕES DE PAGAMENTO")
    y -= LH
    
    valor_ext = valor_por_extenso(data['valor_total'])
    txt = f"""3.1. O valor total do presente contrato é de {format_currency(data['valor_total'])} ({valor_ext}), referentes aos projetos e instalação do sistema fotovoltaico com {data['qtd_modulos']:02d} módulos fotovoltaicos de {data['potencia_modulo']} - {data['marca_modulo']} e 1 inversor de {data['potencia_inversor']} - {data['marca_inversor']}."""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "3.2. O pagamento será realizado, conforme se segue:")
    y -= LH
    
    c.drawString(margin_left + 5*mm, y, f"• Material: {format_currency(data['valor_material'])};")
    y -= LH
    c.drawString(margin_left + 5*mm, y, f"• Mão de obra: {format_currency(data['valor_mao_obra'])} sendo {data['percentual_entrada']}% na assinatura do contrato e o restante ao final da instalação.")
    y -= LH * 1.2
    
    # 4. DO PRAZO
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "4. DO PRAZO DE EXECUÇÃO")
    y -= LH
    
    prazo_ext = valor_por_extenso(data['prazo_execucao']).replace(' reais', '').replace(' real', '')
    txt = f"""4.1. O prazo estimado para a execução dos serviços é de até {data['prazo_execucao']} ({prazo_ext}) dias corridos, contados a partir da assinatura deste contrato e da liberação de acesso ao local."""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "4.2. O prazo poderá ser prorrogado em caso de:")
    y -= LH
    
    for p in ["Condições climáticas adversas;", "Atrasos de responsabilidade do CONTRATANTE;",
              "Fatores externos fora do controle da CONTRATADA."]:
        c.drawString(margin_left + 5*mm, y, f"• {p}")
        y -= LH
    
    y -= LH * 0.5
    
    # 5. DAS OBRIGAÇÕES
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "5. DAS OBRIGAÇÕES DO CONTRATANTE")
    y -= LH
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "5.1. São obrigações do CONTRATANTE:")
    y -= LH
    
    for o in ["Disponibilizar acesso livre e seguro ao local de instalação;",
              "Garantir infraestrutura elétrica e civil compatível com o projeto;",
              "Providenciar rede de internet, se exigida para monitoramento remoto;",
              "Fornecer documentos e autorizações quando necessário para homologação junto à concessionária."]:
        c.drawString(margin_left + 5*mm, y, f"• {o}")
        y -= LH
    
    y -= LH * 0.5
    
    # 6. DAS LIMITAÇÕES
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "6. DAS LIMITAÇÕES DE RESPONSABILIDADE")
    y -= LH
    
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, "6.1. A CONTRATADA não se responsabiliza por:")
    y -= LH
    
    for l in ["Alterações normativas ou exigências adicionais impostas pela concessionária local;",
              "Obras civis, reforços estruturais ou adequações não previstas;",
              "Atrasos provenientes de instituições financeiras, cartórios ou terceiros."]:
        c.drawString(margin_left + 5*mm, y, f"• {l}")
        y -= LH
    
    c.showPage()
    
    # ================== PÁGINA 4 ==================
    draw_header(c, width, height)
    y = height - 28*mm
    
    # 7. DA RESCISÃO
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "7. DA RESCISÃO CONTRATUAL")
    y -= LH
    
    txt = """7.1. Este contrato poderá ser rescindido por qualquer das partes, mediante comunicação formal, nas seguintes hipóteses:"""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.3
    
    c.setFont("Helvetica", 10)
    for item in ["Descumprimento de cláusulas contratuais;", "Impossibilidade técnica de execução comprovada;",
              "Inadimplemento por parte do CONTRATANTE."]:
        c.drawString(margin_left + 5*mm, y, f"• {item}")
        y -= LH
    
    y -= LH * 0.3
    
    txt = """7.2. Em caso de desistência imotivada por parte do CONTRATANTE após o início dos serviços, será devida à CONTRATADA multa compensatória correspondente a 15% (quinze por cento) do valor do contrato."""
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH
    
    # 8. DISPOSIÇÕES FINAIS
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_left, y, "8. DAS DISPOSIÇÕES FINAIS")
    y -= LH
    
    txt = "8.1. Este contrato é celebrado em caráter irrevogável e irretratável, obrigando as partes e seus sucessores a qualquer título."
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    txt = "8.2. Qualquer alteração neste instrumento somente será válida se feita por escrito e assinada por ambas as partes."
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 0.5
    
    txt = "8.3. Fica eleito o foro da Comarca de Juiz de Fora – MG para dirimir quaisquer dúvidas ou controvérsias decorrentes do presente contrato, com renúncia de qualquer outro, por mais privilegiado que seja."
    h = draw_paragraph(c, txt, margin_left, y, text_width, style_normal)
    y -= h + LH * 1.5
    
    # Data e assinaturas
    c.setFont("Helvetica", 10)
    c.drawString(margin_left, y, f"Juiz de Fora – MG, {data['data_contrato']}.")
    y -= LH * 3
    
    c.drawString(margin_left, y, "CONTRATANTE: _______________________________________")
    y -= LH * 3
    
    c.drawString(margin_left, y, "CONTRATADA: ________________________________________")
    
    c.save()
    buffer.seek(0)
    return buffer
