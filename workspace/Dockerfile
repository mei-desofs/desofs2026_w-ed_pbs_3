# imagem base Python
FROM python:3.11

# diretório interno do container
WORKDIR /app

# copiar dependências primeiro (cache Docker)
COPY requirements.txt .

# instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# copiar código da aplicação
COPY . .

# expor porta
EXPOSE 8000

CMD ["python", "mudar_aqui.py"]