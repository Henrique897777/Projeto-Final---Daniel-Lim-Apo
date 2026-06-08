from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão oficial do seu banco Supabase
# Nota: O '@' da senha foi trocado por '%40' para evitar erros de leitura na URL
DATABASE_URL = "postgresql://postgres:WERNECK123%40@db.zifezehamdnhwohnvtbq.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()