import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage

# Configuração da página
st.set_page_config(page_title="Contador de Pontos Seguro", page_icon="🛡️")

# Inicializa o armazenamento local
local_storage = LocalStorage()

# Tabela de pesos
TABELA_PESOS = {
    "INSTALAÇÃO": 1.00, "MUDANÇA DE ENDEREÇO": 1.00, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "SUPORTE": 0.70, "SOLICITAÇÃO DE SERVIÇO": 0.60, "MIGRAÇÃO DE PLANO": 0.50,
    "Mesh": 0.40, "Repetidor": 0.40, "Roku": 0.40, "RETIRADA": 0.38, "Outros": 0.00
}

st.title("🛡️ Contador de Pontos (Modo Seguro)")

# 1. Tenta recuperar dados já salvos no celular
dados_salvos = local_storage.getItem("pontos_tecnico") or []

# Formulário
with st.expander("➕ Lançar Atividade", expanded=True):
    atividade_sel = st.selectbox("Atividade:", list(TABELA_PESOS.keys()))
    if st.button("Confirmar", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": TABELA_PESOS[atividade_sel]
        }
        dados_salvos.append(novo)
        # SALVA NO DISCO DO CELULAR
        local_storage.setItem("pontos_tecnico", dados_salvos)
        st.success("Salvo no aparelho!")
        st.rerun()

st.divider()

# Exibição
if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    st.metric("Total Acumulado", f"{df['Pontos'].sum():.2f}")
    
    for i, item in enumerate(dados_salvos):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{item['Atividade']}** - {item['Pontos']} pts")
        with col2:
            if st.button("🗑️", key=f"del_{item['ID']}"):
                dados_salvos.pop(i)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    # Botão para limpar tudo (Final do dia)
    if st.button("🔴 LIMPAR TUDO (Novo Dia)", use_container_width=True):
        local_storage.deleteAll()
        st.rerun()
else:
    st.info("Nenhum dado salvo no aparelho.")
