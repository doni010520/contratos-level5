# 🚀 SETUP - Level5 Contratos API

Guia passo a passo para colocar o projeto funcionando.

## ✅ Pré-requisitos

- Python 3.11+ instalado
- Git instalado
- (Opcional) Docker instalado

## 📋 Opção 1: Setup Local (Recomendado para Desenvolvimento)

### Passo 1: Clonar o repositório

```bash
git clone <seu-repo-url>
cd level5-contratos
```

### Passo 2: Criar ambiente virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env conforme necessário
```

### Passo 5: Criar diretório de output

```bash
mkdir -p tmp/propostas
```

### Passo 6: Iniciar a API

```bash
uvicorn app.main:app --reload --port 3493
```

A API estará disponível em: **http://localhost:3493**

### Passo 7: Testar

```bash
# Em outro terminal
curl http://localhost:3493/api/v1/health
```

Deve retornar:
```json
{"status": "healthy", "timestamp": "..."}
```

---

## 📋 Opção 2: Setup com Docker

### Passo 1: Clonar o repositório

```bash
git clone <seu-repo-url>
cd level5-contratos
```

### Passo 2: Construir a imagem

```bash
docker-compose build
```

### Passo 3: Iniciar os containers

```bash
docker-compose up
```

A API estará disponível em: **http://localhost:3493**

### Passo 4: Testar

```bash
curl http://localhost:3493/api/v1/health
```

---

## 🧪 Testar Geração de Contrato

### Minimal

```bash
curl -X POST http://localhost:3493/api/v1/contrato/gerar \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Teste Silva",
    "cliente_cpf": "123.456.789-00",
    "cliente_endereco": "Rua Teste, 123",
    "cliente_cep": "00000-000",
    "descricao_objeto": "Sistema solar",
    "itens_tecnicos": [{"numero": 1, "quantidade": "1", "descricao": "Teste"}],
    "valor_material": 1000,
    "valor_mao_obra": 500
  }' > resposta.json

cat resposta.json
```

### Com Python

```python
import requests
import json

dados = {
    "cliente_nome": "João Silva",
    "cliente_cpf": "111.222.333-44",
    "cliente_endereco": "Rua A, 100",
    "cliente_cep": "12345-678",
    "descricao_objeto": "Sistema solar 6kWp",
    "itens_tecnicos": [
        {"numero": 1, "quantidade": "6", "descricao": "Módulos 610Wp"}
    ],
    "valor_material": 10000.00,
    "valor_mao_obra": 3000.00
}

response = requests.post(
    "http://localhost:3493/api/v1/contrato/gerar",
    json=dados
)

resultado = response.json()
print(json.dumps(resultado, indent=2))
```

---

## 📚 Próximos Passos

1. ✅ Testar a API localmente
2. ✅ Customizar dados da empresa (se necessário)
3. ✅ Integrar com n8n
4. ✅ Deploy em produção

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'app'"

**Solução:**
```bash
# Verifique se está no diretório correto
pwd  # Deve estar em /path/to/level5-contratos

# Reative o venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

### "Port 3493 already in use"

**Solução:**
```bash
# Encontre o processo usando a porta
lsof -i :3493  # Linux/Mac
netstat -ano | findstr :3493  # Windows

# Ou use uma porta diferente
uvicorn app.main:app --port 5000
```

### "ImportError: No module named 'reportlab'"

**Solução:**
```bash
pip install --upgrade -r requirements.txt
```

### "FileNotFoundError: app/assets/logo-level5.png"

**Solução:**
```bash
# Você precisa adicionar as imagens em app/assets/
# ou descomente a verificação de arquivo em pdf_generator.py

# As imagens devem estar em:
# - app/assets/logo-level5.png
# - app/assets/background_capa_full.jpg
```

---

## 📝 Estrutura de Pastas

```
level5-contratos/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── proposta.py
│   │   └── contrato.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_generator.py
│   │   ├── graficos.py
│   │   └── calculos.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── formatters.py
│   ├── assets/
│   │   ├── logo-level5.png
│   │   └── background_capa_full.jpg
│   └── main.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── tmp/
│   └── propostas/  (criado automaticamente)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── SETUP.md (este arquivo)
```

---

## ✅ Checklist de Setup

- [ ] Python 3.11+ instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] .env configurado
- [ ] Diretório tmp/propostas criado
- [ ] API iniciada com sucesso
- [ ] Health check respondendo
- [ ] Contrato gerado com sucesso
- [ ] Pronto para integração!

---

## 🚀 Próximo: Integração com n8n

Veja o arquivo `INTEGRACAO_N8N.md` para instruções de integração.

---

**Sucesso! 🎉**
