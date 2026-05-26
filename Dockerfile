# Imagem base
FROM python:3.12-slim

# Define a pasta de trabalho
WORKDIR /app

# Cria um usuário sem privilégios de root (chamado 'appuser')
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos códigos
COPY . .

# Altera a propriedade da pasta /app para o novo usuário
RUN chown -R appuser:appuser /app

# Define o usuário que rodará o processo como 'appuser'
USER appuser

# Expõe a porta
EXPOSE 8000

# Comando de execução
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]