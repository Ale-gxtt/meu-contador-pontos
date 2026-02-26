import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para Celular
st.set_page_config(page_title="Contador de Pontos Profissional", page_icon="📊")

# Dicionário com todas as atividades e pesos da sua imagem
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
st.write("Selecione a atividade realizada abaixo:")

# Inicializa a memória do navegador se não existir
if 'meus_pontos' not in st.session_state:
    st.session_state.meus_pontos = []

# Formulário de lançamento
with st.container():
    # Carrega as opções diretamente da tabela de pesos
    atividade_sel = st.selectbox("Atividade:", list(TABELA_PESOS.keys()))
    
    if st.button("Salvar Ponto", use_container_width=True):
        valor_ponto = TABELA_PESOS[atividade_sel]
        novo_registro = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": valor_ponto
        }
        st.session_state.meus_pontos.append(novo_registro)
        st.success(f"Registrado: {atividade_sel} ({valor_ponto} pts)")

st.divider()

# Histórico e Resumo
if st.session_state.meus_pontos:
    df = pd.DataFrame(st.session_state.meus_pontos)
    
    # Mostra o total acumulado para o técnico
    total_dia = df['Pontos'].sum()
    st.metric("Total de Pontos acumulados", f"{total_dia:.2f}")
    
    st.subheader("📜 Detalhes do Dia")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Botão para gerar o arquivo para enviar no WhatsApp
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório para Enviar",
        data=csv,
        file_name=f"pontos_{datetime.now().strftime('%d_%m')}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("Nenhum ponto lançado. As atividades aparecerão aqui após o primeiro registro.")
