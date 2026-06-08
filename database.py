from sqlalchemy import create_engine # Cria a conexão com o banco em nuvem
from sqlalchemy.ext.declarative import declarative_base
#base para criar os modelos
from sqlalchemy.orm import sessionmaker 
#usada pra executar as linhas

# URL de conexão oficial do seu banco Supabase
# Nota: O '@' da senha foi trocado por '%40' para evitar erros de leitura na URL
DATABASE_URL = "postgresql://postgres:WERNECK123%40@db.zifezehamdnhwohnvtbq.supabase.co:5432/postgres"


engine = create_engine(DATABASE_URL)
 #a conexão em si com o PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() s

def get_db():
    db = SessionLocal()
    try:
        yield db
        # entregar um valor, pausar e depois continuar de onde ela parou
    finally:
        #garante que a sessão sempre feche
        db.close()
    #Abre uma sessão
    
    
