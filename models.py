from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    
    # RF06: Define se o usuário é "comum" ou "gestor"
    perfil = Column(String, default="comum") 

    # Relacionamentos para facilitar buscas
    tarefas_criadas = relationship("Tarefa", foreign_keys='Tarefa.criador_id', back_populates="criador")
    tarefas_atribuidas = relationship("Tarefa", foreign_keys='Tarefa.responsavel_id', back_populates="responsavel")


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)           # RF02: Nome da Tarefa
    descricao = Column(String)                    # RF02: Descrição
    categoria = Column(String, index=True)        # RF04: Categorização
    data_entrega = Column(Date, nullable=True)    # RF03: Data de entrega (Prazo)
    concluida = Column(Boolean, default=False)
    
    # RF06: Controle de quem criou a tarefa
    criador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # RF08: Atribuição de responsável (Gestor designa para alguém)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    # RF09: Gestão de sub-tarefas (Uma tarefa pode ter uma "tarefa_pai")
    tarefa_pai_id = Column(Integer, ForeignKey("tarefas.id"), nullable=True)
    
    # Mapeamento dos relacionamentos no banco
    criador = relationship("Usuario", foreign_keys=[criador_id], back_populates="tarefas_criadas")
    responsavel = relationship("Usuario", foreign_keys=[responsavel_id], back_populates="tarefas_atribuidas")
    sub_tarefas = relationship("Tarefa", backref="tarefa_pai", remote_side=[id])