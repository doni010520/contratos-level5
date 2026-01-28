FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    libxrender1 \
    fonts-liberation \
    libappindicator3-1 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3493

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3493"]
