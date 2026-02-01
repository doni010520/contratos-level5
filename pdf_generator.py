"""
Gerador de Contratos PDF - Level 5 Engenharia Elétrica
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY
from io import BytesIO

AZUL_ESCURO = HexColor("#1a3a4a")
AZUL_HEADER = HexColor("#3a8a9a")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')


def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)


def draw_header(c, width, height):
    header_height = 20*mm
    c.setFillColor(AZUL_HEADER)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10*mm, height - 13*mm, "CONTRATO DE PRESTAÇÃO DE SERVIÇO")
    logo_path = get_asset_path('logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width - 55*mm, height - 18*mm, width=50*mm, height=15*mm,
                    preserveAspectRatio=True, mask='auto')


def format_cpf(cpf):
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    if len(cpf_clean) == 11:
        return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
    return cpf


def format_currency(value):
    try:
        valor = float(value)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {value}"


def valor_por_extenso(valor):
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
        if n == 0: return ''
        elif n == 100: return 'cem'
        elif n < 10: return unidades[n]
        elif n < 20: return dez_a_dezenove[n - 10]
        elif n < 100:
            d, u = divmod(n, 10)
            return dezenas[d] if u == 0 else f"{dezenas[d]} e {unidades[u]}"
        else:
            c, resto = divmod(n, 100)
            if resto == 0: return 'cem' if c == 1 else centenas[c]
            return f"{centenas[c]} e {converte_grupo(resto)}"

    resultado = []
    if inteiro >= 1000:
        milhares, resto = divmod(inteiro, 1000)
        resultado.append("mil" if milhares == 1 else f"{converte_grupo(milhares)} mil")
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


class PDFWriter:
    """Escrita do PDF com quebra de página automática e espaçamento uniforme"""

    # Espaçamento único entre QUALQUER linha
    LINE_GAP = 5.0*mm

    def __init__(self, canvas_obj, width, height):
        self.c = canvas_obj
        self.width = width
        self.height = height
        self.margin_left = 20*mm
        self.margin_right = 20*mm
        self.margin_bottom = 25*mm
        self.text_width = width - self.margin_left - self.margin_right
        self.top_start = height - 30*mm
        self.y = self.top_start
        # Estilo de parágrafo: leading = tamanho da fonte + espaço entre linhas DENTRO do parágrafo
        self.style_normal = ParagraphStyle(
            'Normal', fontName='Helvetica', fontSize=10,
            leading=14.5, alignment=TA_JUSTIFY
        )
        self.style_bullet = ParagraphStyle(
            'Bullet', fontName='Helvetica', fontSize=10,
            leading=14.5, alignment=TA_JUSTIFY, leftIndent=5*mm
        )

    def _needs_page(self, needed):
        """Retorna True se precisa de nova página"""
        return (self.y - needed) < self.margin_bottom

    def new_page(self):
        self.c.showPage()
        draw_header(self.c, self.width, self.height)
        self.y = self.top_start
        self.c.setFillColor(black)

    def _advance(self):
        """Avança exatamente LINE_GAP após qualquer elemento"""
        self.y -= self.LINE_GAP

    def title(self, text):
        """Título de seção em bold - com espaço extra ANTES e DEPOIS"""
        needed = self.LINE_GAP * 3
        if self._needs_page(needed):
            self.new_page()
        else:
            # Espaço extra antes do título (separação entre seções)
            self.y -= self.LINE_GAP * 0.6
        self.c.setFillColor(black)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(self.margin_left, self.y, text)
        # Espaço após título igual ao espaço entre linhas normais
        self._advance()

    def text(self, text):
        """Linha de texto simples"""
        if self._needs_page(self.LINE_GAP * 2):
            self.new_page()
        self.c.setFillColor(black)
        self.c.setFont("Helvetica", 10)
        self.c.drawString(self.margin_left, self.y, text)
        self._advance()

    def paragraph(self, text):
        """Parágrafo com wrap automático"""
        p = Paragraph(text, self.style_normal)
        w, h = p.wrap(self.text_width, 1000)
        if self._needs_page(h + self.LINE_GAP):
            self.new_page()
        self.c.setFillColor(black)
        p.drawOn(self.c, self.margin_left, self.y - h)
        self.y -= h
        self._advance()

    def bullet(self, text):
        """Item com bullet - usa parágrafo se texto longo"""
        bullet_text = f"• {text}"
        p = Paragraph(bullet_text, self.style_bullet)
        w, h = p.wrap(self.text_width - 5*mm, 1000)
        if self._needs_page(h + self.LINE_GAP):
            self.new_page()
        self.c.setFillColor(black)
        p.drawOn(self.c, self.margin_left, self.y - h)
        self.y -= h
        self._advance()

    def label(self, text):
        """Label como CONTRATANTE:"""
        if self._needs_page(self.LINE_GAP * 2):
            self.new_page()
        self.c.setFillColor(black)
        self.c.setFont("Helvetica", 10)
        self.c.drawString(self.margin_left, self.y, text)
        self._advance()

    def signatures(self, data_contrato):
        """Bloco de data e assinaturas"""
        needed = self.LINE_GAP * 10
        if self._needs_page(needed):
            self.new_page()
        self.y -= self.LINE_GAP
        self.c.setFillColor(black)
        self.c.setFont("Helvetica", 10)
        self.c.drawString(self.margin_left, self.y, f"Juiz de Fora – MG, {data_contrato}.")
        self.y -= self.LINE_GAP * 2.5
        self.c.drawString(self.margin_left, self.y, "CONTRATANTE: _______________________________________")
        self.y -= self.LINE_GAP * 2.5
        # Assinatura da CONTRATADA (imagem PNG)
        assinatura_path = get_asset_path('assinatura.png')
        if os.path.exists(assinatura_path):
            self.c.drawImage(assinatura_path, self.margin_left + 20*mm, self.y - 3*mm,
                           width=55*mm, height=20*mm,
                           preserveAspectRatio=True, mask='auto')
        self.c.drawString(self.margin_left, self.y, "CONTRATADA: ________________________________________")


def generate_contract_pdf(data):
    """Gera o PDF do contrato"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # CAPA
    capa_path = get_asset_path('capa.png')
    if not os.path.exists(capa_path):
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

    # PÁGINAS DO CONTRATO
    draw_header(c, width, height)
    pdf = PDFWriter(c, width, height)

    # CONTRATANTE
    pdf.label("CONTRATANTE:")
    endereco = f"{data['endereco']}, {data['bairro']} - CEP {data['cep']}, {data['cidade']}-{data['estado']}"
    pdf.paragraph(f"<b>{data['nome']}</b>, inscrito no <b>CPF nº {format_cpf(data['cpf'])}</b>, residente na {endereco}")

    # CONTRATADA
    pdf.label("CONTRATADA:")
    pdf.paragraph("""<b>LEVEL 5 ENGENHARIA ELÉTRICA LTDA</b>, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº <b>57.946.157/0001-21</b>, com sede em Juiz de Fora – MG, doravante denominada "CONTRATADA".""")
    pdf.paragraph("""As partes acima identificadas celebram o presente Contrato de Compra e Instalação de Sistema de Energia Solar Fotovoltaica, mediante as cláusulas e condições seguintes:""")

    # 1
    pdf.title("1. DO OBJETO")
    pdf.paragraph("""1.1. O presente contrato tem por objeto a entrega e instalação, pela CONTRATADA, de um sistema de geração de energia solar fotovoltaica, conforme especificações técnicas definidas em proposta previamente aprovada pelo CONTRATANTE.""")
    pdf.text("1.2. A instalação incluirá, dentre outros serviços:")
    for s in ["Elaboração de projeto com emissão de ART;",
              "Montagem das estruturas e módulos;",
              "Instalação e conexão dos inversores e cabeamentos;",
              "Configuração do sistema e testes operacionais;",
              "Solicitação de acesso junto à distribuidora local."]:
        pdf.bullet(s)

    # 2
    pdf.title("2. DAS GARANTIAS")
    pdf.text("2.1. Os componentes fornecidos possuem as seguintes garantias diretas dos fabricantes:")
    for g in ["Módulos Fotovoltaicos: 15 anos contra defeitos de fabricação e 25 anos quanto à performance;",
              "Inversores: 12 anos;",
              "Estruturas Metálicas: 5 anos contra corrosão e falhas estruturais."]:
        pdf.bullet(g)
    pdf.paragraph("""2.2. A CONTRATADA oferece garantia de 12 (doze) meses sobre os serviços de instalação, abrangendo vícios de execução e falhas técnicas.""")
    pdf.text("2.3. Estão excluídos da garantia:")
    for e in ["Danos causados por mau uso, sobrecarga ou alterações não autorizadas;",
              "Intervenções de terceiros não autorizados;",
              "Ocorrências naturais como raios, enchentes, ventos extremos e tempestades;",
              "Obras civis não executadas pela CONTRATADA."]:
        pdf.bullet(e)

    # 3
    pdf.title("3. DO PREÇO E DAS CONDIÇÕES DE PAGAMENTO")
    valor_ext = valor_por_extenso(data['valor_total'])
    pdf.paragraph(f"""3.1. O valor total do presente contrato é de {format_currency(data['valor_total'])} ({valor_ext}), referentes aos projetos e instalação do sistema fotovoltaico com {data['qtd_modulos']:02d} módulos fotovoltaicos de {data['potencia_modulo']} - {data['marca_modulo']} e 1 inversor de {data['potencia_inversor']} - {data['marca_inversor']}.""")
    pdf.text("3.2. O pagamento será realizado conforme se segue:")
    pdf.bullet(f"Material: {format_currency(data['valor_material'])}")
    pdf.bullet(f"Mão de obra: {format_currency(data['valor_mao_obra'])}")
    if data.get('forma_pagamento'):
        pdf.text("Forma de pagamento:")
        # Cada linha do texto livre vira um item
        for linha in data['forma_pagamento'].split('\n'):
            linha = linha.strip()
            if linha:
                pdf.paragraph(linha)

    # 4
    pdf.title("4. DO PRAZO DE EXECUÇÃO")
    prazo_ext = valor_por_extenso(data['prazo_execucao']).replace(' reais', '').replace(' real', '')
    pdf.paragraph(f"""4.1. O prazo estimado para a execução dos serviços é de até {data['prazo_execucao']} ({prazo_ext}) dias corridos, contados a partir da assinatura deste contrato e da liberação de acesso ao local.""")
    pdf.text("4.2. O prazo poderá ser prorrogado em caso de:")
    for p in ["Condições climáticas adversas;",
              "Atrasos de responsabilidade do CONTRATANTE;",
              "Fatores externos fora do controle da CONTRATADA."]:
        pdf.bullet(p)

    # 5
    pdf.title("5. DAS OBRIGAÇÕES DO CONTRATANTE")
    pdf.text("5.1. São obrigações do CONTRATANTE:")
    for o in ["Disponibilizar acesso livre e seguro ao local de instalação;",
              "Garantir infraestrutura elétrica e civil compatível com o projeto;",
              "Providenciar rede de internet, se exigida para monitoramento remoto;",
              "Fornecer documentos e autorizações quando necessário para homologação junto à concessionária."]:
        pdf.bullet(o)

    # 6
    pdf.title("6. DAS LIMITAÇÕES DE RESPONSABILIDADE")
    pdf.text("6.1. A CONTRATADA não se responsabiliza por:")
    for l in ["Alterações normativas ou exigências adicionais impostas pela concessionária local;",
              "Obras civis, reforços estruturais ou adequações não previstas;",
              "Atrasos provenientes de instituições financeiras, cartórios ou terceiros."]:
        pdf.bullet(l)

    # 7
    pdf.title("7. DA RESCISÃO CONTRATUAL")
    pdf.paragraph("""7.1. Este contrato poderá ser rescindido por qualquer das partes, mediante comunicação formal, nas seguintes hipóteses:""")
    for item in ["Descumprimento de cláusulas contratuais;",
                 "Impossibilidade técnica de execução comprovada;",
                 "Inadimplemento por parte do CONTRATANTE."]:
        pdf.bullet(item)
    pdf.paragraph("""7.2. Em caso de desistência imotivada por parte do CONTRATANTE após o início dos serviços, será devida à CONTRATADA multa compensatória correspondente a 15% (quinze por cento) do valor do contrato.""")

    # 8
    pdf.title("8. DAS DISPOSIÇÕES FINAIS")
    pdf.paragraph("8.1. Este contrato é celebrado em caráter irrevogável e irretratável, obrigando as partes e seus sucessores a qualquer título.")
    pdf.paragraph("8.2. Qualquer alteração neste instrumento somente será válida se feita por escrito e assinada por ambas as partes.")
    pdf.paragraph("8.3. Fica eleito o foro da Comarca de Juiz de Fora – MG para dirimir quaisquer dúvidas ou controvérsias decorrentes do presente contrato, com renúncia de qualquer outro, por mais privilegiado que seja.")

    # ASSINATURAS
    pdf.signatures(data['data_contrato'])

    c.save()
    buffer.seek(0)
    return buffer
