import streamlit as st
import requests

# URL da sua API FastAPI
API_URL = "https://gerenciador-tarefas-api-cory.onrender.com"

# Configuração da página
st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="📝", layout="centered")

# Gerenciamento de sessão (Token JWT)
if "token" not in st.session_state:
    st.session_state.token = None

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# --- TELA DE LOGIN ---
if st.session_state.token is None:
    st.title("🔐 Login no Sistema")
    
    aba_login, aba_cadastro = st.tabs(["Entrar", "Cadastrar"])
    
    with aba_login:
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                res = requests.post(f"{API_URL}/token", data={"username": usuario, "password": senha})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
                    
    with aba_cadastro:
        with st.form("form_cadastro"):
            novo_usuario = st.text_input("Novo Usuário")
            nova_senha = st.text_input("Nova Senha", type="password")
            submit_cadastro = st.form_submit_button("Cadastrar")
            
            if submit_cadastro:
                res = requests.post(f"{API_URL}/registro", json={"username": novo_usuario, "password": nova_senha})
                if res.status_code == 200:
                    st.success("Cadastro realizado! Agora faça o login.")
                else:
                    st.error(res.json().get("detail", "Erro no cadastro."))

# --- TELA PRINCIPAL (DASHBOARD) ---
else:
    col_titulo, col_sair = st.columns([4, 1])
    col_titulo.title("📝 Minhas Tarefas")
    if col_sair.button("Sair"):
        st.session_state.token = None
        st.rerun()

    # RF07: Dashboard de Métricas
    res_relatorio = requests.get(f"{API_URL}/tarefas/relatorio", headers=get_headers())
    if res_relatorio.status_code == 200:
        dados = res_relatorio.json()
        st.write("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Tarefas", dados["total"])
        m2.metric("✔ Concluídas", dados["concluidas"])
        m3.metric("⏳ Pendentes", dados["pendentes"])
        st.write("---")

    # RF04, RF03, RF08, RF09: Formulário de Criação
    with st.expander("➕ Adicionar Nova Tarefa", expanded=False):
        with st.form("nova_tarefa"):
            titulo = st.text_input("Título *")
            descricao = st.text_area("Descrição *")
            
            c1, c2 = st.columns(2)
            categoria = c1.text_input("Categoria", value="Geral")
            data_entrega = c2.date_input("Data de Entrega", value=None)
            
            submit_tarefa = st.form_submit_button("Criar Tarefa")
            
            if submit_tarefa:
                if not titulo or not descricao:
                    st.warning("Título e Descrição são obrigatórios!")
                else:
                    payload = {
                        "titulo": titulo,
                        "descricao": descricao,
                        "categoria": categoria,
                        "data_entrega": str(data_entrega) if data_entrega else ""
                    }
                    res_post = requests.post(f"{API_URL}/tarefas", headers=get_headers(), data=payload)
                    
                    if res_post.status_code == 200:
                        st.success("Tarefa criada com sucesso!")
                        st.rerun()
                    else:
                        st.error(res_post.json().get("detail", "Erro ao criar tarefa."))

    # Listagem de Tarefas
    st.subheader("Suas Tarefas")
    res_tarefas = requests.get(f"{API_URL}/tarefas", headers=get_headers())
    
    if res_tarefas.status_code == 200:
        tarefas = res_tarefas.json()
        if not tarefas:
            st.info("Você ainda não possui tarefas.")
            
        for t in tarefas:
            # Estilização visual (status)
            status = "✅" if t["concluida"] else "⏳"
            cor_borda = "green" if t["concluida"] else ("red" if "Atrasada" in str(t) else "gray") # Simplificado para o Streamlit
            
            with st.container(border=True):
                col_info, col_acoes = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"**{status} {t['titulo']}**")
                    st.caption(f"{t['descricao']} | 🏷️ {t['categoria']} | 📅 {t['data_entrega'] or 'Sem data'}")
                
                with col_acoes:
                    if not t["concluida"]:
                        if st.button("✔ Concluir", key=f"conc_{t['id']}", use_container_width=True):
                            res_put = requests.put(f"{API_URL}/tarefas/{t['id']}/concluir", headers=get_headers())
                            if res_put.status_code == 200:
                                st.rerun()
                            else:
                                st.error(res_put.json().get("detail", "Erro"))
                                
                    if st.button("🗑 Excluir", key=f"del_{t['id']}", type="primary", use_container_width=True):
                        res_del = requests.delete(f"{API_URL}/tarefas/{t['id']}", headers=get_headers())
                        if res_del.status_code == 200:
                            st.rerun()
                        else:
                            st.error(res_del.json().get("detail", "Erro"))
    elif res_tarefas.status_code == 401:
        # Token expirado ou inválido
        st.session_state.token = None
        st.rerun()