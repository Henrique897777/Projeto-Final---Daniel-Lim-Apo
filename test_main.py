import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, timedelta

from main import app
from database import Base, get_db

# Cria um banco de dados temporário na memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Substitui a conexão oficial do sistema pelo banco de teste
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_banco():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    # Cria um usuário e faz login automaticamente antes de cada teste
    client.post("/registro", json={"username": "tester", "password": "123"})
    resp = client.post("/token", data={"username": "tester", "password": "123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_registro_usuario_sucesso():
    response = client.post("/registro", json={"username": "novo_user", "password": "abc"})
    assert response.status_code == 200

def test_registro_usuario_duplicado():
    client.post("/registro", json={"username": "clone", "password": "123"})
    response = client.post("/registro", json={"username": "clone", "password": "123"})
    assert response.status_code == 400

def test_criar_tarefa_data_retroativa_bloqueada(auth_headers):
    ontem = (date.today() - timedelta(days=1)).isoformat()
    response = client.post(
        "/tarefas",
        headers=auth_headers,
        data={"titulo": "Falha", "descricao": "...", "data_entrega": ontem}
    )
    assert response.status_code == 400
    assert "retroativa" in response.json()["detail"]

def test_bloqueio_concluir_tarefa_com_subtarefa(auth_headers):
    # 1. Cria tarefa pai
    resp_pai = client.post("/tarefas", headers=auth_headers, data={"titulo": "Pai", "descricao": "..."})
    pai_id = resp_pai.json()["tarefa"]["id"]
    
    # 2. Cria sub-tarefa vinculada
    client.post("/tarefas", headers=auth_headers, data={"titulo": "Filho", "descricao": "...", "tarefa_pai_id": pai_id})
    
    # 3. Tenta concluir a tarefa pai (deve ser bloqueado pelo RNF01)
    resp_concluir = client.put(f"/tarefas/{pai_id}/concluir", headers=auth_headers)
    assert resp_concluir.status_code == 400
    assert "sub-tarefas pendentes" in resp_concluir.json()["detail"]

def test_concluir_tarefa_sucesso(auth_headers):
    resp_pai = client.post("/tarefas", headers=auth_headers, data={"titulo": "Solitária", "descricao": "..."})
    pai_id = resp_pai.json()["tarefa"]["id"]
    
    resp_concluir = client.put(f"/tarefas/{pai_id}/concluir", headers=auth_headers)
    assert resp_concluir.status_code == 200