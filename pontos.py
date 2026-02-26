import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Controle de Produção", page_icon="📈")
local_storage = LocalStorage()

TABELA_PESOS = {
    "CAPEX de Retirada": 0.38, "INSTALAÇÃO": 1.00, "Mesh": 0.40,
    "MIGRAÇÃO DE PLANO": 0.50, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "MUDANÇA DE ENDEREÇO": 1.00, "Outros": 0.00, "Repetidor": 0.40,
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38,
    "Retirada Roku": 0.38, "Roku": 0.40, "SOLICITAÇÃO DE SERVIÇO": 0.60, "SUPORTE": 0.70
}

st.title("📈 Controle de Produção")

dados_salvos = local_storage.getItem("pontos_tecnico") or []

with st.expander("➕ Registrar Nova Atividade", expanded=True):
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
        st.rerun()

st.divider()

if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    
    # 1. Total Acumulado
    total_acumulado = df['Pontos'].sum()
    
    # 2. Cálculo de Dias Corridos (Considerando dias com 0)
    data_inicio = df['Data_dt'].min()
    data_hoje = datetime.now()
    # Diferença de dias + 1 para contar o dia atual
    dias_corridos = (data_hoje - data_inicio).days + 1
    
    # 3. Média (Total dividido por todos os dias desde o início)
    media_diaria = total_acumulado / dias_corridos

    # Painel de Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Acumulado", f"{total_acumulado:.2f}")
    col2.metric("Média Real", f"{media_diaria:.2f}")
    col3.metric("Dias no Ciclo", f"{dias_corridos}")

    st.caption(f"A média considera todos os {dias_corridos} dias desde o seu primeiro lançamento ({data_inicio.strftime('%d/%m')}).")

    # Botão de Exportação
    csv = df.drop(columns=['ID', 'Data_dt']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 BAIXAR RELATÓRIO",
        data=csv,
        file_name=f"producao_{datetime.now().strftime('%m_%Y')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.subheader("📋 Histórico")
    for i, item in enumerate(reversed(dados_salvos)):
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.write(f"📅 {item['Data']} | **{item['Atividade']}** | {item['Pontos']} pts")
            if c2.button("🗑️", key=f"del_{item['ID']}"):
                idx_real = len(dados_salvos) - 1 - i
                dados_salvos.pop(idx_real)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    st.divider()
    if st.checkbox("Habilitar limpeza (Zerar Ciclo)"):
        if st.button("🔴 APAGAR TUDO", use_container_width=True):
            local_storage.deleteAll()
            st.rerun()
else:
    st.info("Aguardando lançamentos...")
