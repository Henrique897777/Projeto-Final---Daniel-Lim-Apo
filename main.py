import time #usada pra dar pausas entre tentativas
from fastapi import FastAPI, Request
#núcleo do framework, a classe que cria a API
from fastapi.templating import Jinja2Templates
#renderiza arquivos HTML com variáveis dinâmicas
from fastapi.responses import HTMLResponse
#diz ao FastAPI que a resposta será HTML em vez de JSON
from database import engine, Base
#necessário pra criar tabelas
from rotas import router as tarefas_router
# rotas separadas em outros arquivos
from rotas_auth import router as auth_router
import models
#importado para registrar os modelos antes de criar as tabelas

# Tenta criar as tabelas com retry. Se falhar, espera 3 segundos e tenta de novo.
retries = 5
while retries > 0:
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        break
    except Exception:
        retries -= 1
        time.sleep(3)

app # instãncia principal da API, todo endpoint é registrado nele # = FastAPI(title="API - Gerenciador de Tarefas com Autenticação")
templates = Jinja2Templates(directory="templates")

# Rota para a página principal
@app.get("/", response_class=HTMLResponse)
def rota_inicial(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Rota para a página de login
@app.get("/login", response_class=HTMLResponse)#visa o FastAPI que a resposta será HTML, não JSON
def rota_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")
#ê o arquivo HTML da pasta templates/ e devolve para o navegador

# Registrando os roteadores
app.include_router(tarefas_router)
app.include_router(auth_router)
