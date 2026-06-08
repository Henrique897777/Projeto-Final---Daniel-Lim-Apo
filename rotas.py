from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models import Tarefa, Usuario
from rotas_auth import get_current_user

router = APIRouter()

#BUSCA OS USUARIOS, LIMITA OS CAMPOS DE ATRIBUIÇÃO, OCULTA INFORMAÇÕES DE USUARIO PARA USUARIO, FILTROS DE TAREFA
@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    usuarios = db.query(Usuario).all()
    return [{"id": u.id, "username": u.username, "perfil": u.perfil} for u in usuarios]

@router.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    return db.query(Tarefa).filter(
        (Tarefa.criador_id == usuario_logado.id) | (Tarefa.responsavel_id == usuario_logado.id)
    ).all()

# DATAS,CONTROLE DE NIVEIS DE ATRIBUIÇÃO HIERARQUICA
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
        
    if responsavel_id and responsavel_id != usuario_logado.id and usuario_logado.perfil != 'gestor':
        raise HTTPException(status_code=403, detail="Apenas gestores podem delegar tarefas para a equipe.")

    nova_tarefa = Tarefa(
        titulo=titulo, 
        descricao=descricao,
        categoria=categoria,
        data_entrega=data_entrega,
        criador_id=usuario_logado.id,
        tarefa_pai_id=tarefa_pai_id,
        responsavel_id=responsavel_id or usuario_logado.id 
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return {"status": "sucesso", "tarefa": nova_tarefa}

#DEPENDEICAS DE SUBTAREFAS, RELATORIO DE TAREFAS, ROTA CALCULA SE HA TAREFA PENDENTES 
@router.get("/tarefas/relatorio")
def relatorio_tarefas(db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    total = db.query(Tarefa).filter(Tarefa.responsavel_id == usuario_logado.id).count()
    concluidas = db.query(Tarefa).filter(Tarefa.responsavel_id == usuario_logado.id, Tarefa.concluida == True).count()
    pendentes = total - concluidas
    
    return {"total": total, "concluidas": concluidas, "pendentes": pendentes}

@router.put("/tarefas/{tarefa_id}/concluir")
def concluir_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario_logado: Usuario = Depends(get_current_user)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
    sub_pendentes = db.query(Tarefa).filter(Tarefa.tarefa_pai_id == tarefa_id, Tarefa.concluida == False).count()
    if sub_pendentes > 0:
        raise HTTPException(status_code=400, detail="Não é possível concluir: existem sub-tarefas pendentes vinculadas a esta.")

    tarefa.concluida = True
    db.commit()
    return {"status": "concluída"}

#SERVE PARA EXCLUIR AS TAREFAS, VALIDA SE EXISTE, TRAVA DE SEGURANÇA - REMOVER TAREFA DO USUARIO
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