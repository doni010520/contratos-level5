# 📄 Level5 - API de Propostas e Contratos Solares

API para geração automática de propostas comerciais e contratos para sistemas fotovoltaicos.

## 🚀 Features

✅ Geração de Propostas em PDF (4 páginas)  
✅ Geração de Contratos em PDF (4 páginas)  
✅ Design profissional com branding Level5  
✅ Retorno em Base64 para integração  
✅ API REST com FastAPI  
✅ Pronto para n8n/RPA  

## 📋 Requisitos

- Python 3.11+
- pip ou poetry
- Docker (opcional)

## 🔧 Instalação

### Opção 1: Local (sem Docker)

```bash
# 1. Clone o repositório
git clone <seu-repo>
cd level5-contratos

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie a API
uvicorn app.main:app --reload --port 3493
```

### Opção 2: Docker

```bash
# 1. Construa a imagem
docker-compose build

# 2. Inicie os containers
docker-compose up

# A API estará disponível em: http://localhost:3493
```

## 📚 Uso da API

### Health Check

```bash
curl http://localhost:3493/api/v1/health
```

Resposta:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-28T10:30:00"
}
```

### Gerar Contrato

```bash
curl -X POST http://localhost:3493/api/v1/contrato/gerar \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Paulo Roberto Barreto",
    "cliente_cpf": "198.585.316-72",
    "cliente_endereco": "Rua I, Granja 32F, Parque das Colinas",
    "cliente_cep": "36120-000",
    "descricao_objeto": "Sistema fotovoltaico com 6 módulos",
    "itens_tecnicos": [
      {"numero": 1, "quantidade": "6", "descricao": "Módulos 610Wp - DMEGC"},
      {"numero": 2, "quantidade": "1", "descricao": "Inversor 3,1 kW - Sofar"}
    ],
    "valor_material": 6311.53,
    "valor_mao_obra": 4200.00
  }'
```

Resposta:
```json
{
  "success": true,
  "message": "Contrato gerado com sucesso",
  "pdf_filename": "contrato_paulo_roberto_barreto_xxxxx.pdf",
  "pdf_url": "/api/v1/download/...",
  "pdf_base64": "JVBERi0x...",
  "dados_contrato": {
    "numero_contrato": "LEVEL5-XXXXX",
    "investimento_total": 10511.53,
    ...
  }
}
```

### Download de PDF

```bash
curl http://localhost:3493/api/v1/download/contrato_xxxxx.pdf > contrato.pdf
```

## 🔗 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Info da API |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/contrato/gerar` | Gerar contrato |
| GET | `/api/v1/contrato/template` | Obter template de requisição |
| GET | `/api/v1/download/{filename}` | Download de PDF |

## 📊 Estrutura do Projeto

```
level5-contratos/
├── app/
│   ├── models/
│   │   ├── proposta.py
│   │   └── contrato.py
│   ├── services/
│   │   ├── pdf_generator.py
│   │   ├── graficos.py
│   │   └── calculos.py
│   ├── utils/
│   │   └── formatters.py
│   ├── assets/
│   │   ├── background_capa_full.jpg
│   │   └── logo-level5.png
│   └── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔑 Campos Disponíveis (Contrato)

### Obrigatórios
- `cliente_nome` - Nome do cliente
- `cliente_cpf` - CPF (formato: xxx.xxx.xxx-xx)
- `cliente_endereco` - Endereço completo
- `cliente_cep` - CEP
- `descricao_objeto` - O que será feito
- `itens_tecnicos` - Lista de equipamentos
- `valor_material` - Valor dos materiais
- `valor_mao_obra` - Valor mão de obra

### Opcionais
- `numero_contrato` - Auto-gerado se omitido
- `data_contrato` - Hoje se omitida
- `percentual_entrada_mao_obra` - Padrão: 30%
- `prazo_execucao_dias` - Padrão: 40 dias
- `garantia_modulos_anos` - Padrão: 15
- `garantia_performance_anos` - Padrão: 25
- `garantia_inversores_anos` - Padrão: 12
- `garantia_estrutura_anos` - Padrão: 5
- `garantia_instalacao_meses` - Padrão: 12
- `observacoes` - Notas adicionais

## 🔐 Segurança

- Validação de dados com Pydantic
- CORS habilitado (customizar conforme necessário)
- Rate limiting recomendado para produção
- Use variáveis de ambiente para configurações sensíveis

## 🚀 Deploy

### Heroku
```bash
git push heroku main
```

### AWS / Digital Ocean / DigitalOcean
```bash
docker-compose up -d
```

### Easypanel
1. Conecte seu repositório GitHub
2. Crie novo container
3. Selecione este repositório
4. Configure porta: 3493
5. Deploy!

## 📝 Exemplos de Uso

### Python
```python
import requests
import base64

response = requests.post(
    "http://localhost:3493/api/v1/contrato/gerar",
    json={
        "cliente_nome": "João Silva",
        "cliente_cpf": "123.456.789-00",
        "cliente_endereco": "Rua A, 123",
        "cliente_cep": "00000-000",
        "descricao_objeto": "Sistema solar",
        "itens_tecnicos": [
            {"numero": 1, "quantidade": "6", "descricao": "Módulos 610Wp"}
        ],
        "valor_material": 10000,
        "valor_mao_obra": 3000
    }
)

resultado = response.json()
pdf_bytes = base64.b64decode(resultado['pdf_base64'])
with open("contrato.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## 🆘 Troubleshooting

**Erro: "Módulo não encontrado"**
```bash
pip install -r requirements.txt
```

**Erro: "Porta 3493 já em uso"**
```bash
# Mudar porta no main.py ou usar:
uvicorn app.main:app --port 5000
```

**Erro ao gerar PDF**
- Verifique se assets existem em `app/assets/`
- Verifique permissões de escrita em `/tmp/`

## 📞 Suporte

Para dúvidas, abra uma issue no repositório.

## 📄 Licença

Proprietary - Level5 Engenharia Elétrica

---

**Desenvolvido com ❤️ para Level5 Engenharia Elétrica**
