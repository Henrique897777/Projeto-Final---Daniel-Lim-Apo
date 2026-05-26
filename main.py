import time
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import engine, Base
from rotas import router as tarefas_router
from rotas_auth import router as auth_router
import models

# Tenta criar as tabelas com retry
retries = 5
while retries > 0:
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        break
    except Exception:
        retries -= 1
        time.sleep(3)

app = FastAPI(title="API - Gerenciador de Tarefas com Autenticação")
templates = Jinja2Templates(directory="templates")

# Rota para a página principal
@app.get("/", response_class=HTMLResponse)
def rota_inicial(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Rota para a página de login
@app.get("/login", response_class=HTMLResponse)
def rota_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# Registrando os roteadores
app.include_router(tarefas_router)
app.include_router(auth_router)