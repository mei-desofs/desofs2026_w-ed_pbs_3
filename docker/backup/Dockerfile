# imagem base Python leve
FROM python:3.11

# diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências de compilação e o cliente MySQL 
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# copia ficheiros do backup para o container
COPY . .

# instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# comando de arranque do serviço de backup
CMD ["python", "mudar_aqui.py"]