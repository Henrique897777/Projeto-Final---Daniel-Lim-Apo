from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from database import get_db
from models import Usuario
from pydantic import BaseModel

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPER_SECRETA_MUDAR_EM_PRODUCAO"
ALGORITHM = "HS256"

# ROTADOR QUE FAZ ACOPLAMENTO MAIN,CRIPTOGRAFIA, ADULTERAÇÃO DE TOLKEN ?, ASSINATURA DIGITAL DA API
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    username: str
    password: str

# INJESTOR DE DEPENDECIAS, INTERCEPTADO DE SEGURANÇA, TOLKEN CRIPTOGRAFADO, VERIFICAÇÃO DE USUARIO
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    excecao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise excecao
    except JWTError:
        raise excecao
        
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise excecao
    return user

# ROTAS DE CADRASTRO, ENDPOINT HHTP POST, VERIFICAÇÃO DE USUARIO, CRIPTOGRAFIA DE USUARIO
@router.post("/registro")
def registrar(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == user.username).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    senha_segura = user.password[:72] 
    hashed_password = pwd_context.hash(senha_segura)
    new_user = Usuario(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"status": "usuario criado"}

# AUTENTICAÇÃO DE LOGIN, RECEBE A TENTATIVA DE LOGIN, FAZ VERIFICAÇÃO E COMPARA, ASSINATURA OK ?
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    senha_login = form_data.password[:72]
    
    if not user or not pwd_context.verify(senha_login, user.password):
        raise HTTPException(status_code=400, detail="Credenciais incorretas")
    
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}