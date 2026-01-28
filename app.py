"""
Gerador de Contratos - Level 5 Engenharia Elétrica
Aplicação Flask para geração de contratos em PDF
"""
import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify
from pdf_generator import generate_contract_pdf
import inspect

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


@app.route('/')
def index():
    """Página principal com formulário"""
    return render_template('index.html')


@app.route('/gerar-contrato', methods=['POST'])
def gerar_contrato():
    """Endpoint para gerar o PDF do contrato"""
    try:
        # Função para converter valor BR (1.234,56) para float
        def parse_currency(value):
            if not value:
                return 0.0
            # Remove R$ e espaços
            value = str(value).replace('R$', '').strip()
            # Remove pontos de milhar e troca vírgula por ponto
            value = value.replace('.', '').replace(',', '.')
            return float(value)
        
        # Coletar dados do formulário
        data = {
            'nome': request.form.get('nome', '').strip(),
            'cpf': request.form.get('cpf', '').strip(),
            'endereco': request.form.get('endereco', '').strip(),
            'bairro': request.form.get('bairro', '').strip(),
            'cep': request.form.get('cep', '').strip(),
            'cidade': request.form.get('cidade', '').strip(),
            'estado': request.form.get('estado', 'MG').strip(),
            'valor_material': parse_currency(request.form.get('valor_material', '0')),
            'valor_mao_obra': parse_currency(request.form.get('valor_mao_obra', '0')),
            'qtd_modulos': int(request.form.get('qtd_modulos', 1)),
            'potencia_modulo': request.form.get('potencia_modulo', '610 Wp').strip(),
            'marca_modulo': request.form.get('marca_modulo', 'DMEGC').strip(),
            'potencia_inversor': request.form.get('potencia_inversor', '3,1 kW').strip(),
            'marca_inversor': request.form.get('marca_inversor', 'Sofar').strip(),
            'prazo_execucao': int(request.form.get('prazo_execucao', 40)),
            'percentual_entrada': int(request.form.get('percentual_entrada', 30)),
            'data_contrato': request.form.get('data_contrato', datetime.now().strftime('%d de %B de %Y'))
        }
        
        # Calcular valor total
        data['valor_total'] = data['valor_material'] + data['valor_mao_obra']
        
        # Formatar data se vier no formato yyyy-mm-dd
        if '-' in data['data_contrato']:
            try:
                date_obj = datetime.strptime(data['data_contrato'], '%Y-%m-%d')
                meses = {
                    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                }
                data['data_contrato'] = f"{date_obj.day} de {meses[date_obj.month]} de {date_obj.year}"
            except:
                pass
        
        # Gerar PDF
        pdf_buffer = generate_contract_pdf(data)
        
        # Nome do arquivo
        nome_arquivo = f"Contrato_Comercial_-{data['nome'].replace(' ', '_')}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nome_arquivo
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/debug')
def debug():
    """Debug - verificar versão do código"""
    import pdf_generator
    source = inspect.getsource(pdf_generator.generate_contract_pdf)
    has_42 = "4.2. O prazo" in source
    has_5 = "5. DAS OBRIGAÇÕES" in source
    has_6 = "6. DAS LIMITAÇÕES" in source
    return jsonify({
        'tem_4.2': has_42,
        'tem_secao_5': has_5,
        'tem_secao_6': has_6,
        'versao': 'v2_completa' if (has_42 and has_5 and has_6) else 'v1_antiga'
    })


@app.route('/health')
def health():
    """Health check para o Easypanel"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'false').lower() == 'true')
