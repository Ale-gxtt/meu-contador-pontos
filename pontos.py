import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Contador de Pontos", page_icon="📱")

# Título e Estilo
st.title("📊 Meu Contador de Pontos")
st.write("Os dados são salvos apenas neste aparelho.")

# Inicializa a lista de pontos na sessão (memória do navegador)
if 'meus_pontos' not in st.session_state:
    st.session_state.meus_pontos = []

# Formulário simples para celular
with st.container():
    atividade = st.selectbox("Selecione a Atividade:", ["INSTALAÇÃO", "REPARO", "MUDANÇA", "RETIRADA"])
    
    if st.button("Salvar Ponto", use_container_width=True):
        pontos = 10 if atividade == "INSTALAÇÃO" else 5
        novo_registro = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade,
            "Pontos": pontos
        }
        st.session_state.meus_pontos.append(novo_registro)
        st.success(f"Registrado: {atividade} (+{pontos} pts)")

st.divider()

# Exibição do Histórico
st.subheader("📜 Histórico de Hoje")
if st.session_state.meus_pontos:
    df = pd.DataFrame(st.session_state.meus_pontos)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Botão para o usuário não perder os dados se fechar o site
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório (Excel/CSV)",
        data=csv,
        file_name=f"pontos_{datetime.now().strftime('%d_%m')}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("Nenhum ponto lançado ainda.")
