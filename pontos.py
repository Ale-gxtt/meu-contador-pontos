import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Produtividade", layout="centered")

# 1. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. LOGIN SIMPLES
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acesso ao Sistema")
    usuario = st.text_input("Digite seu Nome ou Matrícula:").strip().upper()
    senha = st.text_input("Senha:", type="password")  # Você pode definir uma senha padrão

    if st.button("Entrar"):
        if usuario != "" and senha == "123":  # Senha simples para teste
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")
    st.stop()

# --- ÁREA LOGADA ---
st.sidebar.write(f"👤 Usuário: **{st.session_state.usuario}**")
if st.sidebar.button("Sair"):
    st.session_state.autenticado = False
    st.rerun()

# Tabela de Atividades
atividades = {
    "INSTALAÇÃO": 1.00, "MIGRAÇÃO DE TECNOLOGIA": 1.00, "MUDANÇA DE ENDEREÇO": 1.00,
    "SUPORTE": 0.70, "SOLICITAÇÃO DE SERVIÇO": 0.60, "MIGRAÇÃO DE PLANO": 0.50,
    "Mesh": 0.40, "Repetidor": 0.40, "Roku": 0.40, "CAPEX de Retirada": 0.38,
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38,
    "Retirada Roku": 0.38, "Outros": 0.00
}

st.title("📊 Meus Pontos")

# FORMULÁRIO DE LANÇAMENTO
with st.form("lancamento"):
    servico = st.selectbox("Atividade Realizada:", list(atividades.keys()))
    if st.form_submit_button("Salvar"):
        df_geral = conn.read(worksheet="Sheet1")

        novo_ponto = pd.DataFrame([{
            "Usuario": st.session_state.usuario,
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": servico,
            "Pontos": atividades[servico]
        }])

        df_final = pd.concat([df_geral, novo_ponto], ignore_index=True)
        conn.update(worksheet="Sheet1", data=df_final)
        st.success("Registrado com sucesso!")

st.divider()

# VISUALIZAÇÃO (AQUI ESTÁ O FILTRO DE PRIVACIDADE)
st.subheader("📅 Meu Histórico")
data_sel = st.date_input("Filtrar por data:", datetime.now()).strftime("%d/%m/%Y")

# Lemos todos os dados, mas SÓ MOSTRAMOS os do usuário logado
df_todos = conn.read(worksheet="Sheet1")
df_filtrado = df_todos[(df_todos["Usuario"] == st.session_state.usuario) & (df_todos["Data"] == data_sel)]

if not df_filtrado.empty:
    st.metric("Meus Pontos no Dia", f"{df_filtrado['Pontos'].sum():.2f}")
    st.table(df_filtrado[["Hora", "Atividade", "Pontos"]])
else:
    st.info("Você não tem registros para este dia.")