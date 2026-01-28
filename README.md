# Gerador de Contratos - Level 5 Engenharia Elétrica

Sistema web para geração automática de contratos de prestação de serviço para instalação de sistemas de energia solar fotovoltaica.

## 📋 Funcionalidades

- Formulário completo para dados do cliente e sistema
- Geração automática de PDF com layout profissional
- Busca automática de endereço por CEP
- Cálculo automático do valor total
- Máscaras para CPF e CEP
- Design responsivo para desktop e mobile

## 🚀 Deploy no Easypanel

### 1. Criar repositório no GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/contrato-generator.git
git push -u origin main
```

### 2. Configurar no Easypanel

1. Acesse o Easypanel e vá em **Apps** → **+ Create**
2. Escolha **App** → **GitHub**
3. Conecte seu repositório
4. Configure:
   - **Build**: Dockerfile
   - **Port**: 5000
   - **Domain**: Seu domínio ou use o gerado automaticamente

### 3. Configurar Assets

Antes do deploy, adicione os arquivos na pasta `assets/`:

- `capa.png` - Imagem da capa do contrato (A4, ~595x842 pixels)
- `logo.png` - Logo da empresa (para header das páginas internas)

## 🔧 Desenvolvimento Local

### Com Docker

```bash
docker-compose up --build
```

### Sem Docker

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar
python app.py
```

Acesse: http://localhost:5000

## 📁 Estrutura do Projeto

```
contrato-generator/
├── app.py              # Aplicação Flask
├── pdf_generator.py    # Lógica de geração do PDF
├── requirements.txt    # Dependências Python
├── Dockerfile          # Config Docker
├── docker-compose.yml  # Config desenvolvimento
├── .gitignore
├── assets/             # Imagens (capa e logo)
│   ├── capa.png
│   └── logo.png
├── templates/
│   └── index.html      # Formulário web
└── static/
    └── logo.png        # Logo para o formulário (opcional)
```

## 📝 Campos do Formulário

### Dados do Cliente
- Nome completo
- CPF
- CEP (busca automática de endereço)
- Endereço completo
- Bairro
- Cidade
- Estado

### Sistema Fotovoltaico
- Quantidade de módulos
- Potência do módulo (ex: 610 Wp)
- Marca do módulo
- Potência do inversor (ex: 3,1 kW)
- Marca do inversor

### Valores e Pagamento
- Valor total
- Valor do material
- Valor da mão de obra
- Percentual de entrada

### Prazos
- Prazo de execução (dias)
- Data do contrato

## 🔒 Segurança

- Aplicação roda com usuário não-root no container
- Health check configurado
- Limite de upload de 16MB
- Sem persistência de dados sensíveis

## 📄 Licença

Projeto privado - Level 5 Engenharia Elétrica
