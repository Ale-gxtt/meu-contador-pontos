import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

st.set_page_config(page_title="Controle de Produção", page_icon="📈")
local_storage = LocalStorage()

TABELA_PESOS = {
    "CAPEX de Retirada": 0.38, "INSTALAÇÃO": 1.00, "Mesh": 0.40,
    "MIGRAÇÃO DE PLANO": 0.50, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "MUDANÇA DE ENDEREÇO": 1.00, "Outros": 0.00, "Repetidor": 0.40,
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38,
    "Retirada Roku": 0.38, "Roku": 0.40, "SOLICITAÇÃO DE SERVIÇO": 0.60, "SUPORTE": 0.70
}

def contar_dias_sem_domingo(inicio, fim):
    dias = 0
    atual = inicio
    while atual <= fim:
        if atual.weekday() != 6: dias += 1
        atual += timedelta(days=1)
    return dias

# Título com selo de segurança
st.title("📈 Controle de Produção")
st.caption("✅ Armazenamento Local Ativo: Seus dados estão salvos neste aparelho.")

dados_salvos = local_storage.getItem("pontos_tecnico") or []

with st.expander("➕ Registrar Nova Atividade", expanded=True):
    atividade_sel = st.selectbox("Selecione o serviço:", list(TABELA_PESOS.keys()))
    if st.button("Salvar Registro", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Points": TABELA_PESOS[atividade_sel]
        }
        
        # Lógica de salvamento
        lista_atualizada = dados_salvos.copy()
        lista_atualizada.append(novo)
        local_storage.setItem("pontos_tecnico", lista_atualizada)
        
        # MENSAGEM DE CONFIRMAÇÃO PARA FECHAR
        st.success("🎯 Informações salvas com sucesso no seu celular!")
        st.toast("Pode fechar a aba se desejar!", icon='🔒')
        time.sleep(1.5) # Pausa rápida para o técnico ler
        st.rerun()

st.divider()

if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    df['Points'] = pd.to_numeric(df['Points'])
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    
    total_acumulado = df['Points'].sum()
    data_inicio = df['Data_dt'].min()
    dias_uteis = contar_dias_sem_domingo(data_inicio, datetime.now())
    media_diaria = total_acumulado / (dias_uteis if dias_uteis > 0 else 1)

    # Status de Performance
    if media_diaria >= 3.2:
        st.success(f"✅ **MÉDIA EXCELENTE: {media_diaria:.2f}**")
    elif media_diaria >= 2.8:
        st.warning(f"⚡ **QUASE LÁ: {media_diaria:.2f}**")
    else:
        st.error(f"🚨 **ALERTA: {media_diaria:.2f}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Acumulado", f"{total_acumulado:.2f}")
    col2.metric("Média", f"{media_diaria:.2f}")
    col3.metric("Dias Úteis", f"{dias_uteis}")

    st.divider()
    
    # Histórico e Botões
    st.subheader("📋 Histórico")
    for i, item in enumerate(reversed(dados_salvos)):
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.write(f"📅 {item['Data']} | **{item['Atividade']}** | {item.get('Points', 0)} pts")
            if c2.button("🗑️", key=f"del_{item['ID']}"):
                dados_salvos.pop(len(dados_salvos) - 1 - i)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    st.info("💡 Dica: Seus dados estão gravados na memória do navegador. Pode sair e voltar quando quiser.")

    if st.checkbox("Habilitar limpeza"):
        if st.button("🔴 ZERAR TUDO"):
            local_storage.deleteAll()
            st.rerun()
else:
    st.info("Aguardando lançamentos...")
