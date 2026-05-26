from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Tarefa

router = APIRouter()

@router.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db)):
    return db.query(Tarefa).all()

@router.post("/tarefas")
def criar_tarefa(titulo: str = Form(...), descricao: str = Form(...), db: Session = Depends(get_db)):
    nova_tarefa = Tarefa(titulo=titulo, descricao=descricao)
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return {"status": "sucesso", "tarefa": nova_tarefa}

@router.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    db.delete(tarefa)
    db.commit()
    return {"status": "removido"}