# imagem base Python
FROM python:3.11

# diretório interno do container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar dependências primeiro (cache Docker)
COPY requirements.txt .

# instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# TODO é preciso inserir rockyou zipado e fazer unzip

# copiar código da aplicação
COPY . .

# expor porta Flask
EXPOSE 5003

# arrancar API
CMD ["python", "app.py"]