# imagem base Python leve
FROM python:3.11

# diretório de trabalho dentro do container
WORKDIR /app

# instala cliente MySQL (necessário para mysqldump)
RUN apt-get update && apt-get install -y mysql-client

# copia ficheiros do backup para o container
COPY . .

# instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# comando de arranque do serviço de backup
CMD ["python", "mudar_aqui.py"]