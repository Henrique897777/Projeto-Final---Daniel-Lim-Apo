from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models import Tarefa, Usuario
from rotas_auth import get_current_user

router = APIRouter()

# Rota NOVA: Busca a lista de usuários para o Dropdown (RF08)
@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    usuarios = db.query(Usuario).all()
    # Retornamos apenas o básico por segurança
    return [{"id": u.id, "username": u.username, "perfil": u.perfil} for u in usuarios]

@router.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    # Retorna tarefas onde ele é o criador ou o responsável
    return db.query(Tarefa).filter(
        (Tarefa.criador_id == usuario_logado.id) | (Tarefa.responsavel_id == usuario_logado.id)
    ).all()

@router.post("/tarefas")
def criar_tarefa(
    titulo: str = Form(...), 
    descricao: str = Form(...), 
    categoria: str = Form("Geral"),
    data_entrega: date = Form(None),
    tarefa_pai_id: int = Form(None),   # RF09: ID da tarefa principal
    responsavel_id: int = Form(None),  # RF08: ID de quem vai executar
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_current_user)
):
    if data_entrega and data_entrega < date.today():
        raise HTTPException(status_code=400, detail="A data de entrega não pode ser retroativa.")
        
    # Regra de Segurança: Apenas gestores podem atribuir tarefas para OUTRAS pessoas
    if responsavel_id and responsavel_id != usuario_logado.id and usuario_logado.perfil != 'gestor':
        raise HTTPException(status_code=403, detail="Apenas gestores podem delegar tarefas para a equipe.")

    nova_tarefa = Tarefa(
        titulo=titulo, 
        descricao=descricao,
        categoria=categoria,
        data_entrega=data_entrega,
        criador_id=usuario_logado.id,
        tarefa_pai_id=tarefa_pai_id,
        # Se não designar ninguém, a tarefa é da própria pessoa que criou
        responsavel_id=responsavel_id or usuario_logado.id 
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return {"status": "sucesso", "tarefa": nova_tarefa}

@router.get("/tarefas/relatorio")
def relatorio_tarefas(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    # Relatório agora se baseia nas tarefas sob responsabilidade do usuário
    total = db.query(Tarefa).filter(Tarefa.responsavel_id == usuario_logado.id).count()
    concluidas = db.query(Tarefa).filter(Tarefa.responsavel_id == usuario_logado.id, Tarefa.concluida == True).count()
    pendentes = total - concluidas
    
    return {"total": total, "concluidas": concluidas, "pendentes": pendentes}

@router.put("/tarefas/{tarefa_id}/concluir")
def concluir_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
    # RN01: O bloqueio! Se houver sub-tarefa pendente, a principal não conclui.
    sub_pendentes = db.query(Tarefa).filter(Tarefa.tarefa_pai_id == tarefa_id, Tarefa.concluida == False).count()
    if sub_pendentes > 0:
        raise HTTPException(status_code=400, detail="Não é possível concluir: existem sub-tarefas pendentes vinculadas a esta.")

    tarefa.concluida = True
    db.commit()
    return {"status": "concluída"}

@router.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
    if tarefa.criador_id != usuario_logado.id and usuario_logado.perfil != 'gestor':
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar esta tarefa")

    db.delete(tarefa)
    db.commit()
    return {"status": "removido"}