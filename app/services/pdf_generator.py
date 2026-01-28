from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, 
    PageTemplate, 
    Frame, 
    Paragraph, 
    Spacer, 
    Image, 
    Table, 
    TableStyle, 
    PageBreak,
    NextPageTemplate
)
from reportlab.graphics.shapes import Drawing, Line
import os
from PIL import Image as PILImage

# Certifique-se de que este import existe no seu projeto ou ajuste conforme necessário
from app.utils.formatters import formatar_moeda_br

class PDFGenerator:
    
    # Paleta de Cores Level5
    COR_AZUL_ESCURO = HexColor('#336777')
    COR_TEAL = HexColor('#16A085')
    COR_LARANJA = HexColor('#F39C12')
    COR_CINZA = HexColor('#7F8C8D')
    COR_CINZA_CLARO = HexColor('#ECF0F1')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
        
        # CAMINHOS DAS IMAGENS
        self.background_capa = 'app/assets/background_capa_full.jpg' 
        self.logo_path = 'app/assets/logo-level5.png'
    
    def _criar_estilos_customizados(self):
        self.styles.add(ParagraphStyle(
            name='LabelClienteCapa',
            fontSize=14,
            textColor=self.COR_AZUL_ESCURO,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))

        self.styles.add(ParagraphStyle(
            name='NomeClienteCapa',
            fontSize=26,
            textColor=self.COR_TEAL,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=28
        ))

        self.styles.add(ParagraphStyle(
            name='SecaoTitulo',
            fontSize=16,
            textColor=self.COR_AZUL_ESCURO,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceBefore=15,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Corpo',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceBefore=3,
            spaceAfter=6,
            leading=16
        ))
        
        # O bulletText usará o firstLineIndent negativo para posicionar o marcador
        self.styles.add(ParagraphStyle(
            name='CorpoBullet',
            parent=self.styles['Corpo'],
            leftIndent=0.6*cm,       # Todo o bloco de texto recuado
            firstLineIndent=-0.6*cm, # O marcador volta para a esquerda
            spaceBefore=3,
            spaceAfter=3
        ))

    def _draw_cover(self, canvas, doc):
        """Desenha APENAS a imagem de fundo da capa na página inteira"""
        canvas.saveState()
        page_width, page_height = A4
        
        if os.path.exists(self.background_capa):
            canvas.drawImage(self.background_capa, 0, 0, width=page_width, height=page_height)
        
        canvas.restoreState()

    def _draw_header_footer(self, canvas, doc):
        """Cabeçalho e Rodapé das páginas internas"""
        canvas.saveState()
        page_width, page_height = A4
        
        # --- CABEÇALHO (Fundo Azul para logo branca) ---
        header_height = 3.0 * cm
        
        # Retângulo Azul
        canvas.setFillColor(self.COR_AZUL_ESCURO)
        canvas.rect(0, page_height - header_height, page_width, header_height, fill=1, stroke=0)
        
        # Linha Laranja Decorativa
        canvas.setFillColor(self.COR_LARANJA)
        canvas.rect(0, page_height - header_height, page_width, 0.1*cm, fill=1, stroke=0)
        
        # Logo (Superior Direito)
        if os.path.exists(self.logo_path):
            max_width = 8.0 * cm
            max_height = 2.5 * cm 
            margin_right = 1.0 * cm
            
            try:
                with PILImage.open(self.logo_path) as img:
                    img_w, img_h = img.size
                    aspect = img_w / float(img_h)
            except:
                aspect = 1
            
            draw_height = max_height
            draw_width = draw_height * aspect
            
            if draw_width > max_width:
                draw_width = max_width
                draw_height = draw_width / aspect

            y_pos = page_height - (header_height / 2) - (draw_height / 2)
            
            canvas.drawImage(
                self.logo_path, 
                page_width - draw_width - margin_right, 
                y_pos, 
                width=draw_width, 
                height=draw_height, 
                mask='auto'
            )
            
        # Texto do Cabeçalho (Esquerda)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(white)
        canvas.drawString(2 * cm, page_height - 1.8 * cm, "PROPOSTA TÉCNICA E COMERCIAL")
        
        # --- RODAPÉ ---
        canvas.setStrokeColor(self.COR_CINZA_CLARO)
        canvas.line(2*cm, 1.5*cm, page_width - 2*cm, 1.5*cm)
        
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(self.COR_CINZA)
        canvas.drawString(2*cm, 1*cm, "Level5 Engenharia Elétrica")
        canvas.drawRightString(page_width - 2*cm, 1*cm, f"Página {doc.page}")
        
        canvas.restoreState()

    def _get_image_height_for_width(self, image_path, target_width):
        """Calcula a altura proporcional de uma imagem dada uma largura alvo"""
        try:
            with PILImage.open(image_path) as img:
                width, height = img.size
                aspect = height / float(width)
                return target_width * aspect
        except Exception:
            return 10 * cm

    def gerar_proposta_plana(self, nome_cliente, modulos_quantidade, especificacoes_modulo, 
                           inversores_quantidade, especificacoes_inversores, investimento_kit, 
                           investimento_mao_de_obra, investimento_total, grafico_producao_path, 
                           tabela_retorno_path, ano_payback, valor_payback, economia_25_anos, output_path):
        
        # Configuração do Documento
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3.5*cm, 
            bottomMargin=2*cm
        )
        
        frame_normal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        
        template_capa = PageTemplate(id='Capa', frames=[frame_normal], onPage=self._draw_cover)
        template_conteudo = PageTemplate(id='Conteudo', frames=[frame_normal], onPage=self._draw_header_footer)
        
        doc.addPageTemplates([template_capa, template_conteudo])
        
        story = []
        
        # --- PÁGINA 1: CAPA ---
        story.append(Spacer(1, 22*cm)) 
        story.append(Paragraph("CLIENTE:", self.styles['LabelClienteCapa']))
        story.append(Paragraph(nome_cliente.upper(), self.styles['NomeClienteCapa']))
        
        story.append(NextPageTemplate('Conteudo'))
        story.append(PageBreak())
        
        # --- PÁGINA 2 ---
        story.append(Paragraph("QUEM SOMOS?", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        texto_quem_somos = """Somos uma empresa especializada no segmento de engenharia elétrica, com foco no desenvolvimento de projetos elétricos e na instalação de sistemas fotovoltaicos. Desde 2019, temos trabalhado para oferecer soluções eficientes e sustentáveis, sempre com alto padrão de qualidade. Ao longo de nossa trajetória, já realizamos mais de 700 projetos fotovoltaicos, contribuindo para a geração de energia limpa e a redução de custos energéticos de nossos clientes. Nosso compromisso é entregar excelência em cada etapa do processo, desde o planejamento até a execução, garantindo resultados que superam expectativas."""
        story.append(Paragraph(texto_quem_somos, self.styles['Corpo']))
        
        story.append(Paragraph("FUNCIONAMENTO DO SISTEMA FOTOVOLTAICO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        texto_func = """O sistema fotovoltaico é composto principalmente por três componentes: painéis solares, inversor e medidor bidirecional. Os painéis captam a energia solar e a convertem em energia elétrica de corrente contínua (CC). Em seguida, o inversor transforma essa corrente contínua em corrente alternada (CA), que pode ser utilizada pelos equipamentos elétricos. O medidor bidirecional desempenha um papel essencial ao monitorar a energia produzida pelo sistema. Ele controla o fluxo de energia, permitindo o uso da eletricidade da concessionária quando necessário e acumulando créditos para a energia excedente gerada pelo sistema solar. Isso elimina a necessidade de baterias para armazenar a energia excedente, tornando o sistema mais econômico e eficiente."""
        story.append(Paragraph(texto_func, self.styles['Corpo']))

        story.append(Paragraph("DESCRIÇÃO DOS ITENS:", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        # CORREÇÃO AQUI: Uso de bulletText
        story.append(Paragraph(f"{modulos_quantidade} {especificacoes_modulo}", self.styles['CorpoBullet'], bulletText='•'))
        story.append(Paragraph(f"{inversores_quantidade} Inversor(es) {especificacoes_inversores}", self.styles['CorpoBullet'], bulletText='•'))
        
        story.append(Paragraph("GARANTIA", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        story.append(Paragraph("A garantia do sistema fotovoltaico é composta por:", self.styles['Corpo']))
        
        garantias = [
            "<b>Módulos Fotovoltaicos:</b>&nbsp;Garantia de desempenho linear de 25 anos e garantia contra defeitos de fabricação de 15 anos, fornecida pelo fabricante.",
            "<b>Inversor:</b>&nbsp;Garantia de 10 anos contra defeitos de fabricação, conforme especificado pelo fabricante.",
            "<b>Estrutura de Fixação:</b>&nbsp;Garantia contra corrosão e defeitos de fabricação, de acordo com as especificações do fabricante.",
            "<b>Serviço de Instalação:</b>&nbsp;Garantia de 1 ano, cobrindo a qualidade e a execução técnica do serviço realizado."
        ]
        
        # CORREÇÃO AQUI: Uso de bulletText
        for g in garantias:
            story.append(Paragraph(g, self.styles['CorpoBullet'], bulletText='•'))

        story.append(PageBreak())
        
        # --- PÁGINA 3 ---
        story.append(Paragraph("INVESTIMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        dados_inv = [
            ['DESCRIÇÃO', 'VALOR'],
            ['Kit Fotovoltaico', formatar_moeda_br(investimento_kit)],
            ['Mão de Obra e Projetos', formatar_moeda_br(investimento_mao_de_obra)],
            ['INVESTIMENTO TOTAL', formatar_moeda_br(investimento_total)]
        ]
        
        t_inv = Table(dados_inv, colWidths=[11*cm, 5*cm])
        t_inv.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,-1), (-1,-1), white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (1,1), (-1,-2), [white, self.COR_CINZA_CLARO]),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(t_inv)
        
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("FORMAS DE PAGAMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        story.append(Paragraph("Oferecemos diversas formas de pagamento para facilitar a aquisição do seu sistema fotovoltaico. Entre as opções disponíveis estão:", self.styles['Corpo']))
        
        pagamentos = [
            "<b>Pagamento à Vista:</b>&nbsp;Desconto especial para pagamentos realizados à vista.",
            "<b>Financiamento Bancário:</b>&nbsp;Parcerias com instituições financeiras que permitem financiar o sistema em até 120 meses, com condições acessíveis e taxas competitivas.",
            "<b>Pagamento Parcelado:</b>&nbsp;Possibilidade de parcelamento direto no cartão."
        ]
        
        # CORREÇÃO AQUI: Uso de bulletText
        for p in pagamentos:
            story.append(Paragraph(p, self.styles['CorpoBullet'], bulletText='•'))
        
        story.append(Paragraph("Todas as opções são planejadas para proporcionar flexibilidade e viabilizar o investimento em energia solar de forma prática e acessível.", self.styles['Corpo']))

        story.append(Spacer(1, 0.2*cm))

        # --- SEÇÃO DIFERENCIAL (COMPACTADA) ---
        story.append(Paragraph("DIFERENCIAL!", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        texto_diferencial_compacto = """
        Em parceria com a Yelum Seguradora, oferecemos seguro para seu sistema fotovoltaico (1% a 1,5% do valor total/ano). 
        <b>Cobertura completa para:</b>&nbsp;Danos acidentais, Vendavais, Granizo, Incêndios, Raios, Explosões e Roubo/Furto.
        Essa parceria reforça nosso compromisso com sua segurança. Realizamos a simulação e contratação diretamente no fechamento do projeto.
        """
        story.append(Paragraph(texto_diferencial_compacto, self.styles['Corpo']))

        story.append(PageBreak())
        
        # --- PÁGINA 4 ---
        story.append(Paragraph("CUSTO X BENEFÍCIO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        story.append(Paragraph("O gráfico abaixo ilustra a produção estimada de energia mês a mês. Essa estimativa considera a variação de irradiância solar ao longo do ano, garantindo uma visão realista do desempenho do sistema em diferentes períodos.", self.styles['Corpo']))
        
        if os.path.exists(grafico_producao_path):
            story.append(Image(grafico_producao_path, width=16*cm, height=8*cm))
            
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("RETORNO DO INVESTIMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        story.append(Paragraph("Uma das etapas mais importantes para avaliar o custo-benefício do sistema fotovoltaico é o cálculo do retorno sobre o investimento. Com base na tarifa atual de energia elétrica, considerando um reajuste médio ao ano, projetamos os seguintes resultados:", self.styles['Corpo']))
        
        # CORREÇÃO AQUI: Uso de bulletText nos itens de retorno
        if ano_payback:
            # Item 1
            texto_lucro = f"<b>Lucro a partir do {ano_payback}º ano:</b>&nbsp;O sistema começará a gerar um retorno acumulado de <b>{formatar_moeda_br(valor_payback)}</b>"
            story.append(Paragraph(texto_lucro, self.styles['CorpoBullet'], bulletText='•'))
            
            # Item 2 (Highlight)
            texto_economia = f"<b>Retorno significativo em 25 anos:</b>&nbsp;Economia acumulada de <b>{formatar_moeda_br(economia_25_anos)}</b>"
            
            # Criamos o estilo e passamos bulletText explicitamente
            estilo_highlight = ParagraphStyle('Highlight', parent=self.styles['CorpoBullet'], textColor=self.COR_TEAL, fontSize=14)
            story.append(Paragraph(texto_economia, estilo_highlight, bulletText='•'))
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Com essas premissas, o investimento no sistema fotovoltaico se mostra altamente vantajoso, garantindo economia no curto prazo e uma valorização significativa no longo prazo.", self.styles['Corpo']))
        story.append(Spacer(1, 0.3*cm))

        if os.path.exists(tabela_retorno_path):
            tabela_width = 16*cm
            tabela_height = self._get_image_height_for_width(tabela_retorno_path, tabela_width)
            
            img_tabela = Image(tabela_retorno_path, width=tabela_width, height=tabela_height)
            img_tabela.hAlign = 'CENTER'
            story.append(img_tabela)

        doc.build(story)

    def gerar_contrato(
        self,
        cliente_nome: str,
        cliente_cpf: str,
        cliente_endereco: str,
        cliente_cep: str,
        numero_contrato: str,
        data_contrato: str,
        itens_tecnicos: list,
        descricao_objeto: str,
        valor_material: float,
        valor_mao_obra: float,
        percentual_entrada_mao_obra: float,
        prazo_execucao_dias: int,
        garantia_modulos_anos: int,
        garantia_performance_anos: int,
        garantia_inversores_anos: int,
        garantia_estrutura_anos: int,
        garantia_instalacao_meses: int,
        observacoes: str = None,
        local_execucao: str = None,
        output_path: str = None
    ):
        """
        Gera um contrato de prestação de serviço fotovoltaico
        """
        
        investimento_total = valor_material + valor_mao_obra
        valor_entrada_mao_obra = valor_mao_obra * (percentual_entrada_mao_obra / 100)
        valor_saldo_mao_obra = valor_mao_obra - valor_entrada_mao_obra
        
        # Configuração do Documento
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3.5*cm,
            bottomMargin=2*cm
        )
        
        frame_normal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        
        template_capa = PageTemplate(id='Capa', frames=[frame_normal], onPage=self._draw_cover)
        template_conteudo = PageTemplate(id='Conteudo', frames=[frame_normal], onPage=self._draw_header_footer)
        
        doc.addPageTemplates([template_capa, template_conteudo])
        
        story = []
        
        # --- PÁGINA 1: CAPA ---
        story.append(Spacer(1, 22*cm))
        story.append(Paragraph("CLIENTE:", self.styles['LabelClienteCapa']))
        story.append(Paragraph(cliente_nome.upper(), self.styles['NomeClienteCapa']))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"Contrato nº {numero_contrato}", self.styles['LabelClienteCapa']))
        
        story.append(NextPageTemplate('Conteudo'))
        story.append(PageBreak())
        
        # --- PÁGINA 2: DADOS DO CONTRATO ---
        story.append(Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        # Dados do Contratante
        story.append(Paragraph("CONTRATANTE:", self.styles['SecaoTitulo']))
        endereco_formatado = f"{cliente_nome}, inscrito no CPF nº {cliente_cpf}<br/>Endereço: {cliente_endereco} - CEP {cliente_cep}"
        story.append(Paragraph(endereco_formatado, self.styles['Corpo']))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Dados da Contratada
        story.append(Paragraph("CONTRATADA:", self.styles['SecaoTitulo']))
        contratada_text = "LEVEL 5 ENGENHARIA ELÉTRICA LTDA<br/>CNPJ: 57.946.157/0001-21<br/>Sede: Juiz de Fora – MG"
        story.append(Paragraph(contratada_text, self.styles['Corpo']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # DO OBJETO
        story.append(Paragraph("1. DO OBJETO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        story.append(Paragraph(f"<b>1.1</b> O presente contrato tem por objeto: {descricao_objeto}", self.styles['Corpo']))
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("<b>1.2 ESPECIFICAÇÕES TÉCNICAS:</b>", self.styles['Corpo']))
        
        # Tabela de itens técnicos
        dados_itens = [['Item', 'Quantidade', 'Descrição']]
        for item in itens_tecnicos:
            dados_itens.append([
                str(item.get('numero', '')),
                str(item.get('quantidade', '')),
                item.get('descricao', '')
            ])
        
        t_itens = Table(dados_itens, colWidths=[1.5*cm, 2.5*cm, 12*cm])
        t_itens.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, self.COR_CINZA_CLARO]),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#CCCCCC')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))
        story.append(t_itens)
        
        story.append(Spacer(1, 0.5*cm))
        
        # DAS GARANTIAS
        story.append(Paragraph("2. DAS GARANTIAS", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        garantias_text = f"""
        <b>2.1 Garantias dos Componentes:</b><br/>
        • Módulos Fotovoltaicos: {garantia_modulos_anos} anos contra defeitos e {garantia_performance_anos} anos de performance<br/>
        • Inversores: {garantia_inversores_anos} anos contra defeitos<br/>
        • Estruturas Metálicas: {garantia_estrutura_anos} anos contra corrosão e falhas estruturais<br/>
        <br/>
        <b>2.2 Garantia da Instalação:</b><br/>
        A CONTRATADA oferece garantia de {garantia_instalacao_meses} meses sobre os serviços de instalação, 
        abrangendo vícios de execução e falhas técnicas.<br/>
        <br/>
        <b>2.3 Exclusões de Garantia:</b><br/>
        • Danos causados por mau uso, sobrecarga ou alterações não autorizadas<br/>
        • Intervenções de terceiros não autorizados<br/>
        • Ocorrências naturais (raios, enchentes, ventos extremos, tempestades)<br/>
        • Obras civis não executadas pela CONTRATADA
        """
        story.append(Paragraph(garantias_text, self.styles['Corpo']))
        
        story.append(PageBreak())
        
        # --- PÁGINA 3: VALORES E PRAZOS ---
        story.append(Paragraph("3. DO PREÇO E CONDIÇÕES DE PAGAMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        # Tabela de investimento
        dados_inv = [
            ['DESCRIÇÃO', 'VALOR'],
            ['Material/Equipamentos', formatar_moeda_br(valor_material)],
            ['Mão de Obra', formatar_moeda_br(valor_mao_obra)],
            ['INVESTIMENTO TOTAL', formatar_moeda_br(investimento_total)]
        ]
        
        t_inv = Table(dados_inv, colWidths=[11*cm, 5*cm])
        t_inv.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,-1), (-1,-1), white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (1,1), (-1,-2), [white, self.COR_CINZA_CLARO]),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(t_inv)
        
        story.append(Spacer(1, 0.5*cm))
        
        # Condições de pagamento
        dados_pag = [
            ['DESCRIÇÃO', 'VALOR', '%'],
            ['Entrada (Mão de Obra)', formatar_moeda_br(valor_entrada_mao_obra), f'{percentual_entrada_mao_obra:.0f}%'],
            ['Saldo (Mão de Obra)', formatar_moeda_br(valor_saldo_mao_obra), f'{100-percentual_entrada_mao_obra:.0f}%'],
        ]
        
        t_pag = Table(dados_pag, colWidths=[10*cm, 4*cm, 2*cm])
        t_pag.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.COR_TEAL),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, self.COR_CINZA_CLARO]),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(t_pag)
        
        story.append(Spacer(1, 0.5*cm))
        
        # PRAZO
        story.append(Paragraph("4. DO PRAZO DE EXECUÇÃO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        prazo_text = f"""
        <b>4.1</b> O prazo estimado para execução dos serviços é de até <b>{prazo_execucao_dias} dias corridos</b>, 
        contados a partir da assinatura deste contrato e da liberação de acesso ao local.<br/>
        <br/>
        <b>4.2</b> O prazo poderá ser prorrogado em caso de:<br/>
        • Condições climáticas adversas<br/>
        • Atrasos de responsabilidade do CONTRATANTE<br/>
        • Fatores externos fora do controle da CONTRATADA
        """
        story.append(Paragraph(prazo_text, self.styles['Corpo']))
        
        story.append(Spacer(1, 0.3*cm))
        
        # OBRIGAÇÕES
        story.append(Paragraph("5. DAS OBRIGAÇÕES DO CONTRATANTE", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        obrigacoes_text = """
        <b>5.1</b> São obrigações do CONTRATANTE:<br/>
        • Disponibilizar acesso livre e seguro ao local de instalação<br/>
        • Garantir infraestrutura elétrica e civil compatível com o projeto<br/>
        • Providenciar rede de internet, se exigida para monitoramento remoto<br/>
        • Fornecer documentos e autorizações quando necessário para homologação junto à concessionária
        """
        story.append(Paragraph(obrigacoes_text, self.styles['Corpo']))
        
        story.append(Spacer(1, 0.3*cm))
        
        # LIMITAÇÕES
        story.append(Paragraph("6. DAS LIMITAÇÕES DE RESPONSABILIDADE", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        limitacoes_text = """
        <b>6.1</b> A CONTRATADA não se responsabiliza por:<br/>
        • Alterações normativas ou exigências adicionais impostas pela concessionária local<br/>
        • Obras civis, reforços estruturais ou adequações não previstas<br/>
        • Atrasos provenientes de instituições financeiras, cartórios ou terceiros
        """
        story.append(Paragraph(limitacoes_text, self.styles['Corpo']))
        
        story.append(Spacer(1, 0.3*cm))
        
        # RESCISÃO
        story.append(Paragraph("7. DA RESCISÃO CONTRATUAL", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        rescisao_text = """
        <b>7.1</b> Este contrato poderá ser rescindido por qualquer das partes, mediante comunicação formal, nas seguintes hipóteses:<br/>
        • Descumprimento de cláusulas contratuais<br/>
        • Impossibilidade técnica de execução comprovada<br/>
        • Inadimplemento por parte do CONTRATANTE<br/>
        <br/>
        <b>7.2</b> Em caso de desistência imotivada por parte do CONTRATANTE após o início dos serviços, 
        será devida à CONTRATADA multa compensatória correspondente a <b>15% (quinze por cento)</b> do valor do contrato.
        """
        story.append(Paragraph(rescisao_text, self.styles['Corpo']))
        
        story.append(PageBreak())
        
        # --- PÁGINA 4: DISPOSIÇÕES FINAIS E ASSINATURAS ---
        story.append(Paragraph("8. DAS DISPOSIÇÕES FINAIS", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        disposicoes_text = """
        <b>8.1</b> Este contrato é celebrado em caráter irrevogável e irretratável, obrigando as partes e seus sucessores a qualquer título.<br/>
        <br/>
        <b>8.2</b> Qualquer alteração neste instrumento somente será válida se feita por escrito e assinada por ambas as partes.<br/>
        <br/>
        <b>8.3</b> Fica eleito o foro da Comarca de Juiz de Fora – MG para dirimir quaisquer dúvidas ou controvérsias 
        decorrentes do presente contrato, com renúncia de qualquer outro, por mais privilegiado que seja.
        """
        story.append(Paragraph(disposicoes_text, self.styles['Corpo']))
        
        if observacoes:
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph("9. OBSERVAÇÕES ADICIONAIS", self.styles['SecaoTitulo']))
            story.append(self._criar_linha_divisoria())
            story.append(Paragraph(observacoes, self.styles['Corpo']))
        
        story.append(Spacer(1, 1*cm))
        
        # Local e Data
        story.append(Paragraph(f"Juiz de Fora – MG, {data_contrato}", self.styles['Corpo']))
        
        story.append(Spacer(1, 1*cm))
        
        # Assinaturas
        story.append(Paragraph("<b>CONTRATANTE:</b>", self.styles['Corpo']))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("_" * 50, self.styles['Corpo']))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(cliente_nome, self.styles['Corpo']))
        
        story.append(Spacer(1, 1*cm))
        
        story.append(Paragraph("<b>CONTRATADA:</b>", self.styles['Corpo']))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("_" * 50, self.styles['Corpo']))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("LEVEL 5 ENGENHARIA ELÉTRICA LTDA", self.styles['Corpo']))
        
        doc.build(story)

    def _criar_linha_divisoria(self):
        d = Drawing(400, 5)
        d.add(Line(0, 0, 460, 0, strokeColor=self.COR_LARANJA, strokeWidth=2))
        return d
