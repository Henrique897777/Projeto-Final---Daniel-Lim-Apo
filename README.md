<h1 align="center"> 📝 Gerenciador de Tarefas </h1>

<p align="center">  
  <img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">  
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">  
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">  
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
</p>

<p align="center"> Uma aplicação Full-Stack robusta e intuitiva para o gerenciamento de atividades diárias, organização de equipes e controle de produtividade.</p>

---

## 🎯 Objetivos e Praticidade
O sistema foi pensado para ser prático, seguro e direto ao ponto:
- **🔐 Autenticação Segura:** Sistema de login protegido por Token JWT. Cada usuário acessa apenas o que lhe compete.
- **✨ Gestão Completa (CRUD):** Capacidade total para criar, ler, concluir e excluir tarefas.
- **📊 Dashboard Integrado:** Métricas em tempo real sobre tarefas totais, concluídas e pendentes.
- **🚦 Alertas Visuais:** Destaca automaticamente prazos atrasados e bloqueia a criação de tarefas com datas retroativas.
- **🔗 Sub-tarefas e Delegação:** Permite atribuir tarefas a outros membros da equipe e bloqueia a conclusão de grandes projetos caso existam sub-tarefas pendentes.

---

## 🛠️ Tecnologias e Armazenamento
Este projeto foi construído unindo o poder de um backend moderno com um frontend leve e dinâmico:
* **🐍 Python (FastAPI):** O motor assíncrono da nossa aplicação, garantindo rotas rápidas e validadas.
* **🌐 HTML / CSS / JS Vanilla:** Interface construída sem frameworks pesados, consumindo a API de forma dinâmica com `fetch`.
* **☁️ Supabase (PostgreSQL):** Banco de dados relacional hospedado na nuvem, garantindo disponibilidade, segurança e dispensando a necessidade de containers locais complexos.
* **🗄️ SQLAlchemy & Pytest:** Framework ORM para mapeamento de tabelas e suíte de testes automatizados garantindo a qualidade do código.

---

## ⚙️ Como executar o projeto localmente

Siga os passos abaixo para rodar o projeto na sua máquina:

**1. Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
cd NOME_DO_REPOSITORIO

2. Instale as dependências:
Bash
pip install -r requirements.txt

3. Inicie o servidor web:
Bash
python -m uvicorn main:app --reload
