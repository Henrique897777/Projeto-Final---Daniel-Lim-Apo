from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from database import get_db
from models import Usuario
from pydantic import BaseModel

# --- 1. DEFINIÇÃO DO ROUTER ---
router = APIRouter()

# --- 2. CONFIGURAÇÕES DE SEGURANÇA ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPER_SECRETA_MUDAR_EM_PRODUCAO"
ALGORITHM = "HS256"

# Modelo para o registro
class UserCreate(BaseModel):
    username: str
    password: str

# --- 3. ROTAS (AGORA O 'router' JÁ EXISTE) ---

@router.post("/registro")
def registrar(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == user.username).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    # Truncar para 72 bytes para evitar erro do bcrypt
    senha_segura = user.password[:72] 
    
    hashed_password = pwd_context.hash(senha_segura)
    new_user = Usuario(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"status": "usuario criado"}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    
    # Truncar a senha recebida no login
    senha_login = form_data.password[:72]
    
    if not user or not pwd_context.verify(senha_login, user.password):
        raise HTTPException(status_code=400, detail="Credenciais incorretas")
    
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}