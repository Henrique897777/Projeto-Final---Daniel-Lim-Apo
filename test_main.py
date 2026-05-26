from fastapi.testclient import TestClient
from main import app

# Cria um "navegador falso" para testar nossa API
client = TestClient(app)

# Teste 1: Verifica se a API está no ar
def test_rota_inicial():
    response = client.get("/")
    assert response.status_code == 200

# Teste 2: Verifica se conseguimos criar uma tarefa
def test_criar_tarefa():
    nova_tarefa = {"id": 1, "titulo": "Estudar Python", "descricao": "Fazer testes", "concluida": False}
    response = client.post("/tarefas", json=nova_tarefa)
    assert response.status_code == 200
    assert response.json()["titulo"] == "Estudar Python"

# Teste 3: Verifica se a lista de tarefas é retornada corretamente
def test_listar_tarefas():
    response = client.get("/tarefas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Teste 4: Verifica se conseguimos atualizar a tarefa criada
def test_atualizar_tarefa():
    tarefa_atualizada = {"id": 1, "titulo": "Estudar Python", "descricao": "Fazer testes", "concluida": True}
    response = client.put("/tarefas/1", json=tarefa_atualizada)
    assert response.status_code == 200
    assert response.json()["concluida"] == True

# Teste 5: Verifica se conseguimos deletar a tarefa
def test_deletar_tarefa():
    response = client.delete("/tarefas/1")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa deletada com sucesso"}