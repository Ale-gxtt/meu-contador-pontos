import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage

# Configuração da página
st.set_page_config(page_title="Produção Mensal - 26 Dias", page_icon="📈")

local_storage = LocalStorage()

# Tabela oficial de pesos
TABELA_PESOS = {
    "INSTALAÇÃO": 1.00, "MUDANÇA DE ENDEREÇO": 1.00, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "SUPORTE": 0.70, "SOLICITAÇÃO DE SERVIÇO": 0.60, "MIGRAÇÃO DE PLANO": 0.50,
    "Mesh": 0.40, "Repetidor": 0.40, "Roku": 0.40, "CAPEX de Retirada": 0.38, 
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38, 
    "Retirada Roku": 0.38, "Outros": 0.00
}

st.title("📈 Controle de Produção")

# Recupera dados salvos
dados_salvos = local_storage.getItem("pontos_tecnico") or []

# Formulário de lançamento
with st.expander("➕ Registrar Atividade", expanded=True):
    atividade_sel = st.selectbox("Selecione o serviço:", list(TABELA_PESOS.keys()))
    if st.button("Salvar Registro", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": TABELA_PESOS[atividade_sel]
        }
        dados_salvos.append(novo)
        local_storage.setItem("pontos_tecnico", dados_salvos)
        st.success("Salvo no histórico mensal!")
        st.rerun()

st.divider()

if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    
    # Cálculos de Produção
    total_acumulado = df['Pontos'].sum()
    hoje = datetime.now().strftime("%d/%m/%Y")
    total_hoje = df[df['Data'] == hoje]['Pontos'].sum()
    dias_trabalhados = df['Data'].nunique()

    # Painel de Resumo
    col1, col2, col3 = st.columns(3)
    col1.metric("Hoje", f"{total_hoje:.2f}")
    col2.metric("Acumulado", f"{total_acumulado:.2f}")
    col3.metric("Dias Ativos", f"{dias_trabalhados}/26")

    # Botão de Download do Fechamento
    csv = df.drop(columns=['ID']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 BAIXAR FECHAMENTO (CSV)",
        data=csv,
        file_name=f"producao_mensal_{datetime.now().strftime('%m_%Y')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.subheader("📋 Histórico Completo")
    
    # Exibição compacta para muitos dias
    for i, item in enumerate(reversed(dados_salvos)): # Mostra os mais recentes primeiro
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{item['Data']}** - {item['Atividade']} ({item['Pontos']} pts)")
            if c2.button("🗑️", key=f"del_{item['ID']}"):
                # Localiza o índice original para deletar
                idx_to_del = len(dados_salvos) - 1 - i
                dados_salvos.pop(idx_to_del)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    st.divider()

    # Trava para zerar o mês
    st.warning("Atenção: A opção abaixo apaga todos os 26 dias de uma vez.")
    if st.checkbox("Confirmar encerramento do período mensal"):
        if st.button("🔴 ZERAR TUDO E RECOMEÇAR MÊS", use_container_width=True):
            local_storage.deleteAll()
            st.rerun()
else:
    st.info("Inicie seus lançamentos. Os dados ficarão salvos por todo o mês neste aparelho.")
