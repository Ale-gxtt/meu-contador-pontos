import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para Celular
st.set_page_config(page_title="Contador de Pontos Profissional", page_icon="📊")

# Tabela oficial de pesos
TABELA_PESOS = {
    "INSTALAÇÃO": 1.00,
    "MUDANÇA DE ENDEREÇO": 1.00,
    "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "SUPORTE": 0.70,
    "SOLICITAÇÃO DE SERVIÇO": 0.60,
    "MIGRAÇÃO DE PLANO": 0.50,
    "Mesh": 0.40,
    "Repetidor": 0.40,
    "Roku": 0.40,
    "CAPEX de Retirada": 0.38,
    "RETIRADA": 0.38,
    "Retirada de Repetidor": 0.38,
    "Retirada MESH": 0.38,
    "Retirada Roku": 0.38,
    "Outros": 0.00
}

st.title("📊 Contador de Pontos")

# Inicializa a memória do navegador se não existir
if 'meus_pontos' not in st.session_state:
    st.session_state.meus_pontos = []

# Formulário de lançamento
with st.expander("➕ Lançar Nova Atividade", expanded=True):
    atividade_sel = st.selectbox("Selecione a Atividade:", list(TABELA_PESOS.keys()))
    
    if st.button("Confirmar Lançamento", use_container_width=True):
        valor_ponto = TABELA_PESOS[atividade_sel]
        novo_registro = {
            "ID": datetime.now().strftime("%H%M%S%f"), # ID único para exclusão
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": valor_ponto
        }
        st.session_state.meus_pontos.append(novo_registro)
        st.success(f"Registrado: {atividade_sel}!")
        st.rerun()

st.divider()

# Histórico e Opção de Apagar
if st.session_state.meus_pontos:
    df = pd.DataFrame(st.session_state.meus_pontos)
    
    # Resumo de Pontos
    total_dia = df['Pontos'].sum()
    st.metric("Total Acumulado", f"{total_dia:.2f} pts")
    
    st.subheader("📜 Histórico (Toque no 🗑️ para excluir)")
    
    # Criamos uma lista de itens para poder excluir individualmente
    for i, item in enumerate(st.session_state.meus_pontos):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{item['Atividade']}** ({item['Hora']}) - {item['Pontos']} pts")
        with col2:
            # Botão de excluir para cada linha
            if st.button("🗑️", key=f"del_{item['ID']}"):
                st.session_state.meus_pontos.pop(i)
                st.warning("Atividade removida!")
                st.rerun()

    st.divider()
    
    # Botão para baixar relatório
    csv = df.drop(columns=['ID']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório",
        data=csv,
        file_name=f"pontos_{datetime.now().strftime('%d_%m')}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("Nenhuma atividade lançada no momento.")
