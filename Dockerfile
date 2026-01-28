FROM python:3.11-slim

WORKDIR /app

# Instalar apenas pacotes essenciais e que existem
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3493

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3493"]
