import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_local_storage import LocalStorage

# Configuração da página para Celular
st.set_page_config(page_title="Controle de Produção Mensal", page_icon="📈")

# Inicializa o armazenamento no disco do navegador
local_storage = LocalStorage()

# Tabela oficial de pesos e atividades
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

st.title("📈 Controle de Produção")

# 1. Recupera dados salvos permanentemente no aparelho
dados_salvos = local_storage.getItem("pontos_tecnico") or []

# Formulário de lançamento
with st.expander("➕ Registrar Nova Atividade", expanded=True):
    atividade_sel = st.selectbox("Selecione o serviço realizado:", list(TABELA_PESOS.keys()))
    
    if st.button("Salvar Registro", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": TABELA_PESOS[atividade_sel]
        }
        dados_salvos.append(novo)
        # Salva no disco rígido do navegador
        local_storage.setItem("pontos_tecnico", dados_salvos)
        st.success("✅ Registro salvo com sucesso!")
        st.rerun()

st.divider()

# Exibição dos resultados acumulados
if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    
    # Cálculos Dinâmicos
    total_acumulado = df['Pontos'].sum()
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    total_hoje = df[df['Data'] == hoje_str]['Pontos'].sum()
    dias_trabalhados = df['Data'].nunique()

    # Painel de Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Hoje", f"{total_hoje:.2f}")
    col2.metric("Acumulado", f"{total_acumulado:.2f}")
    col3.metric("Dias Ativos", f"{dias_trabalhados}")

    # Botão de Exportação para o WhatsApp/E-mail
    csv = df.drop(columns=['ID']).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 BAIXAR FECHAMENTO COMPLETO",
        data=csv,
        file_name=f"producao_acumulada_{datetime.now().strftime('%m_%Y')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.subheader("📋 Histórico Registrado")
    st.caption("Os registros mais recentes aparecem primeiro.")
    
    # Exibição do histórico com os mais recentes no topo
    for i, item in enumerate(reversed(dados_salvos)):
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.write(f"📅 {item['Data']} | **{item['Atividade']}** | {item['Pontos']} pts")
            # Botão de excluir item específico
            if c2.button("🗑️", key=f"del_{item['ID']}"):
                idx_real = len(dados_salvos) - 1 - i
                dados_salvos.pop(idx_real)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    st.divider()

    # Trava de Segurança para Zerar o Ciclo
    st.warning("⚠️ Ação Irreversível: Use apenas após enviar o relatório.")
    if st.checkbox("Li e quero
