import streamlit as st
#É a biblioteca responsável por toda a interface visual. 
# Com ela você cria botões, formulários, colunas, métricas, textos
import requests
# É a biblioteca que faz chamadas HTTP para a API FastAPI. 
# Sem ela, o Streamlit não consegue se comunicar com o backend.

# URL da sua API FastAPI
API_URL = "http://localhost:8000"

# configurações visuais da página
st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="📝", layout="centered")

# Gerenciamento de sessão (Token JWT)
if "token" not in st.session_state:
    #memória temporária do streamlit sem ele qualquer clique apagaria tudo
    st.session_state.token = None

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}
# Monta o cabeçalho HTTP com o token JWT. 
# Toda requisição autenticada precisa disso para a API identificar quem está fazendo a chamada.

# --- TELA DE LOGIN ---
if st.session_state.token is None:
    # Se não há token, exibe as abas de login e cadastro. 
    # Quando o login é bem-sucedido:
    st.title("🔐 Login no Sistema")
    
    aba_login, aba_cadastro = st.tabs(["Entrar", "Cadastrar"])
    
    with aba_login:
        with st.form("form_login"):#garante que os forms faz com que a página só reccaregue e envie os dados após enviar
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                res = requests.post(f"{API_URL}/token", data={"username": usuario, "password": senha})
                #se a API retornar 200, ela salva e recarrega a página, como o token existe ela vai pular o if e else
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.rerun()
                    # Salva o token e recarrega a página. 
                    # Como agora o token existe, o if é ignorado e o dashboard aparece.
                else:
                    st.error("Usuário ou senha incorretos.")
                    
    with aba_cadastro:
        with st.form("form_cadastro"):
            novo_usuario = st.text_input("Novo Usuário")
            nova_senha = st.text_input("Nova Senha", type="password")
            submit_cadastro = st.form_submit_button("Cadastrar")
            
            if submit_cadastro:
                res = requests.post(f"{API_URL}/registro", json={"username": novo_usuario, "password": nova_senha})
                #envia os dados com JSON para criar o usuário no banco de dados
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
        #o código garante que tudo o que for renderizado abaixo só aparecerá se o 
        # usuário tiver um Token válido na sessão.

        # Quando o botão "Sair" é clicado, você limpa o token (None) 
        # e força o recarregamento da página (st.rerun())

    # RF07: Dashboard de Métricas
    # Faz uma requisição ao endpoint 
    # /tarefas/relatorio e exibe os números em 3 colunas lado a lado.
    res_relatorio = requests.get(f"{API_URL}/tarefas/relatorio", headers=get_headers())
    if res_relatorio.status_code == 200:
        dados = res_relatorio.json()
        st.write("---")
        m1, m2, m3 = st.columns(3) #tamanhos iguais
        m1.metric("Total de Tarefas", dados["total"])
        m2.metric("✔ Concluídas", dados["concluidas"])
        m3.metric("⏳ Pendentes", dados["pendentes"])
        st.write("---")
        #Busca o relatório na API e exibe os npumeros em 3 colinas lado a lado
    #

    # RF04, RF03, RF08, RF09: Formulário de Criação
    with st.expander("➕ Adicionar Nova Tarefa", expanded=False):
        #esconde o formulário, até o usuário clicar
        #deixando a tela menos poluida
        with st.form("nova_tarefa"):
            #agrupa os campos e sóenvia após o botão clicado
            titulo = st.text_input("Título *")
            descricao = st.text_area("Descrição *")
            
            c1, c2 = st.columns(2)
            categoria = c1.text_input("Categoria", value="Geral")
            data_entrega = c2.date_input("Data de Entrega", value=None)
            
            submit_tarefa = st.form_submit_button("Criar Tarefa")
            
            if submit_tarefa:
                if not titulo or not descricao: #impede dados vazios 
                    st.warning("Título e Descrição são obrigatórios!")
                else:
                    payload = {
                        # você monta um dicionário com ps dados digitados e envia como data e 
                        # request
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
    #request.get faz uma chamada pro endpoint /tarefas
    
    if res_tarefas.status_code == 200: #quando o servidor responder com sucesso
        tarefas = res_tarefas.json()
        if not tarefas: # avalia se a lista retornada está vazia 
            st.info("Você ainda não possui tarefas.")
            
        for t in tarefas:
            # loop dinâmico 
            status = "✅" if t["concluida"] else "⏳"
            cor_borda = "green" if t["concluida"] else ("red" if "Atrasada" in str(t) else "gray") # Simplificado para o Streamlit
            
            with st.container(border=True):
                col_info, col_acoes = st.columns([3, 1])
                
                with col_info:
                    # tratamento de valores nulos, evitando que a tela exiba valores nulos feios 
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
                        #O código intercepta o clique dentro do if e dispara uma requisição 
                        # HTTP DELETE apontando exatamente para o endpoint daquela tarefa:
                        #A API FastAPI recebe a chamada, remove o registro do banco de dados e devolve 200 OK.

                        res_del = requests.delete(f"{API_URL}/tarefas/{t['id']}", headers=get_headers())
                        # cada butão dispara uma requisição HTTP diferente 
                        # apontando para o id específico da tarefa
                        if res_del.status_code == 200:
                            st.rerun()
                        else:
                            st.error(res_del.json().get("detail", "Erro"))
    elif res_tarefas.status_code == 401:
        # Se a API retornar 401 (não autorizado), limpa o token e redireciona para o login automaticamente.
        st.session_state.token = None
        st.rerun()
