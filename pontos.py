import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração da página
st.set_page_config(page_title="Produção - Técnico", page_icon="📈", layout="wide")
local_storage = LocalStorage()

# 2. Tabela de Pesos Oficial
TABELA_PESOS = {
    "CAPEX de Retirada": 0.38, "INSTALAÇÃO": 1.00, "Mesh": 0.40,
    "MIGRAÇÃO DE PLANO": 0.50, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "MUDANÇA DE ENDEREÇO": 1.00, "Outros": 0.00, "Repetidor": 0.40,
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38,
    "Retirada Roku": 0.38, "Roku": 0.40, "SOLICITAÇÃO DE SERVIÇO": 0.60, "SUPORTE": 0.70
}

# Função para contar dias úteis (Segunda a Sábado)
def contar_dias_sem_domingo(inicio, fim):
    dias = 0
    atual = inicio
    while atual <= fim:
        if atual.weekday() != 6: # 6 = Domingo
            dias += 1
        atual += timedelta(days=1)
    return dias

# --- SISTEMA DE IDENTIFICAÇÃO (NOME DO TÉCNICO) ---
nome_usuario = local_storage.getItem("nome_tecnico")

if not nome_usuario:
    st.title("🚀 Bem-vindo!")
    st.subheader("Para começar, precisamos te identificar.")
    nome_input = st.text_input("Digite seu nome completo:")
    if st.button("Acessar Sistema"):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.rerun()
        else:
            st.error("Por favor, digite seu nome.")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("👤 Perfil")
st.sidebar.write(f"**Técnico:** {nome_usuario}")
if st.sidebar.button("Alterar Nome / Sair"):
    local_storage.setItem("nome_tecnico", None)
    st.rerun()
st.sidebar.divider()
st.sidebar.caption("Versão 2.0 - 2026")

# --- CONTEÚDO PRINCIPAL ---
st.title(f"Olá, {nome_usuario.split()[0]}! 📈")
st.caption("Armazenamento local ativo. Seus dados estão protegidos neste aparelho.")

dados_salvos = local_storage.getItem("pontos_tecnico") or []

# Formulário de Registro
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
        
        lista_atualizada = dados_salvos.copy()
        lista_atualizada.append(novo)
        local_storage.setItem("pontos_tecnico", lista_atualizada)
        
        st.success("🎯 Informações salvas com sucesso!")
        st.toast("Pode fechar a aba se desejar!", icon='🔒')
        time.sleep(1.2)
        st.rerun()

st.divider()

if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    df['Points_Num'] = pd.to_numeric(df['Pontos'])
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    
    # Cálculos
    total_acumulado = df['Points_Num'].sum()
    data_inicio = df['Data_dt'].min()
    dias_uteis = contar_dias_sem_domingo(data_inicio, datetime.now())
    media_diaria = total_acumulado / (dias_uteis if dias_uteis > 0 else 1)

    # --- STATUS DE PERFORMANCE ---
    st.subheader("🎯 Status de Performance")
    if media_diaria >= 3.2:
        st.success(f"✅ **MÉDIA EXCELENTE: {media_diaria:.2f}**\n\nMeta batida! Mantenha o ritmo.")
    elif media_diaria >= 2.8:
        st.warning(f"⚡ **QUASE LÁ: {media_diaria:.2f}**\n\nFalta pouco para os 3.2. Você consegue!")
    else:
        st.error(f"🚨 **ALERTA: {media_diaria:.2f}**\n\nMédia abaixo do esperado. Foco na produtividade!")

    # Métricas Visuais
    c1, c2, c3 = st.columns(3)
    c1.metric("Acumulado", f"{total_acumulado:.2f}")
    c2.metric("Média/Dia", f"{media_diaria:.2f}", delta=round(media_diaria - 3.2, 2))
    c3.metric("Dias Úteis", f"{dias_uteis}")

    st.divider()
    
    # Preparação do Relatório para Exportação
    df_export = df.drop(columns=['ID', 'Data_dt', 'Points_Num'])
    df_export['Tecnico'] = nome_usuario # Adiciona o nome do técnico em cada linha do CSV
    csv = df_export.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 BAIXAR RELATÓRIO PARA ENVIO",
        data=csv,
        file_name=f"producao_{nome_usuario.replace(' ', '_')}_{datetime.now().strftime('%m_%Y')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Histórico
    st.subheader("📋 Histórico Recente")
    for i, item in enumerate(reversed(dados_salvos)):
        with st.container():
            col_text, col_del = st.columns([5, 1])
            col_text.write(f"📅 {item['Data']} | **{item['Atividade']}** | {item['Pontos']} pts")
            if col_del.button("🗑️", key=f"del_{item['ID']}"):
                dados_salvos.pop(len(dados_salvos) - 1 - i)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    st.divider()
    # Trava de Segurança
    if st.checkbox("Habilitar limpeza (Zerar Mês)"):
        if st.button("🔴 APAGAR TODOS OS DADOS"):
            local_storage.deleteItem("pontos_tecnico")
            st.rerun()
else:
    st.info(f"Olá {nome_usuario}, inicie seus lançamentos para ver sua média.")
