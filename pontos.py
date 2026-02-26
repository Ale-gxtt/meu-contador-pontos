import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Contador de Pontos Local", page_icon="📊")

# Nome do arquivo de banco de dados local
ARQUIVO_DADOS = "meus_pontos.csv"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=["Data", "Hora", "Atividade", "Pontos"])

# Interface
st.title("📂 Meu Controle de Pontos Local")

# Formulário de entrada
with st.form("form_pontos", clear_on_submit=True):
    atividade = st.selectbox("Atividade Realizada:", ["INSTALAÇÃO", "REPARO", "MUDANÇA", "RETIRADA"])
    submit = st.form_submit_button("Salvar no Dispositivo")

    if submit:
        # Criar nova linha
        novo_ponto = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade,
            "Pontos": 10 if atividade == "INSTALAÇÃO" else 5
        }
        
        # Salvar no arquivo local
        df_atual = carregar_dados()
        df_novo = pd.concat([df_atual, pd.DataFrame([novo_ponto])], ignore_index=True)
        df_novo.to_csv(ARQUIVO_DADOS, index=False)
        st.success("Ponto salvo localmente!")

# Exibir Histórico
st.divider()
st.subheader("📜 Histórico Salvo")
df_historico = carregar_dados()
st.dataframe(df_historico, use_container_width=True)

# Botão para baixar os dados (Backup)
if not df_historico.empty:
    csv = df_historico.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Excel (CSV)", csv, "meus_pontos.csv", "text/csv")
