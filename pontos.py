import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage

# Configuração da página
st.set_page_config(page_title="Contador de Pontos Seguro", page_icon="🛡️")

# Inicializa o armazenamento local
local_storage = LocalStorage()

# Tabela oficial de pesos
TABELA_PESOS = {
    "INSTALAÇÃO": 1.00, "MUDANÇA DE ENDEREÇO": 1.00, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "SUPORTE": 0.70, "SOLICITAÇÃO DE SERVIÇO": 0.60, "MIGRAÇÃO DE PLANO": 0.50,
    "Mesh": 0.40, "Repetidor": 0.40, "Roku": 0.40, "CAPEX de Retirada": 0.38, 
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38, 
    "Retirada Roku": 0.38, "Outros": 0.00
}

st.title("🛡️ Contador de Pontos")

# Recupera dados salvos no aparelho
dados_salvos = local_storage.getItem("pontos_tecnico") or []

# Formulário de lançamento
with st.expander("➕ Lançar Atividade", expanded=True):
    atividade_sel = st.selectbox("Selecione a Atividade:", list(TABELA_PESOS.keys()))
    if st.button("Confirmar Lançamento", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": TABELA_PESOS[atividade_sel]
        }
        dados_salvos.append(novo)
        local_storage.setItem("pontos_tecnico", dados_salvos)
        st.success("Salvo com sucesso!")
        st.rerun()

st.divider()

# Exibição do histórico e resultados
if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    
    # Métrica de Total
    total_dia = df['Pontos'].sum()
    st.metric("Total Acumulado", f"{total_dia:.2f} pts")
    
    # Botão de Download (Voltou para cá!)
    csv = df.drop(columns=['ID']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 BAIXAR RELATÓRIO DO DIA",
        data=csv,
        file_name=f"pontos_{datetime.now().strftime('%d_%m')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.subheader("📜 Detalhes salvos no aparelho")
    
    # Lista de atividades com opção de excluir individual
    for i, item in enumerate(dados_salvos):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{item['Atividade']}** ({item['Hora']}) - {item['Pontos']} pts")
        with col2:
            if st.button("🗑️", key=f"del_{item['ID']}"):
                dados_salvos.pop(i)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    st.divider()

    # Botão para Limpar com Confirmação
    if st.checkbox("Habilitar limpeza de dados (Novo Dia)"):
        if st.button("🔴 APAGAR TUDO E RECOMEÇAR", use_container_width=True):
            local_storage.deleteAll()
            st.rerun()
else:
    st.info("Nenhum dado salvo no aparelho.")
