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

# copiar código da aplicação
COPY . .

# expor porta
EXPOSE 8000

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

# copiar código da aplicação
COPY . .

ENV PYTHONPATH=/app

# expor porta
EXPOSE 8000

CMD ["python", "-m", "src.workspace_api.workspace_app"]