import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração da página
st.set_page_config(page_title="Produção - Técnico", page_icon="📈", layout="wide")
local_storage = LocalStorage()

# 2. Tabela de Pesos (Organizada do maior para o menor)
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

# Organiza a lista de atividades por valor de ponto (decrescente) para o selectbox
atividades_ordenadas = dict(sorted(TABELA_PESOS.items(), key=lambda item: item[1], reverse=True))

def contar_dias_sem_domingo(inicio, fim):
    dias = 0
    atual = inicio
    while atual <= fim:
        if atual.weekday() != 6: # 6 = Domingo
            dias += 1
        atual += timedelta(days=1)
    return dias

# --- SISTEMA DE IDENTIFICAÇÃO ---
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

# --- BARRA LATERAL ---
st.sidebar.title("👤 Perfil")
st.sidebar.write(f"**Técnico:** {nome_usuario}")
if st.sidebar.button("Alterar Nome / Sair"):
    local_storage.setItem("nome_tecnico", None)
    st.rerun()

# --- CONTEÚDO PRINCIPAL ---
st.title(f"Olá, {nome_usuario.split()[0]}! 📈")

dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_salvos = []

for item in dados_brutos:
    ponto_valor = item.get("Pontos") if item.get("Pontos") is not None else item.get("Points", 0)
    item["Pontos_Padrao"] = ponto_valor
    dados_salvos.append(item)

with st.expander("➕ Registrar Nova Atividade", expanded=True):
    # Aqui a lista já aparece do maior ponto para o menor
    atividade_sel = st.selectbox("Selecione o serviço realizado:", list(atividades_ordenadas.keys()))
    
    if st.button("Salvar Registro", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Pontos": TABELA_PESOS[atividade_sel]
        }
        
        lista_atualizada = dados_brutos.copy()
        lista_atualizada.append(novo)
        local_storage.setItem("pontos_tecnico", lista_atualizada)
        
        st.success("🎯 Salvo com sucesso!")
        st.toast("Pode fechar a aba se desejar!", icon='🔒')
        time.sleep(1.2)
        st.rerun()

st.divider()

if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    df['Points_Num'] = pd.to_numeric(df['Pontos_Padrao'])
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    
    total_acumulado = df['Points_Num'].sum()
    data_inicio = df['Data_dt'].min()
    dias_uteis = contar_dias_sem_domingo(data_inicio, datetime.now())
    media_diaria = total_acumulado / (dias_uteis if dias_uteis > 0 else 1)

    st.subheader("🎯 Status de Performance")
    if media_diaria >= 3.2:
        st.success(f"✅ **MÉDIA EXCELENTE: {media_diaria:.2f}**")
    elif media_diaria >= 2.8:
        st.warning(f"⚡ **QUASE LÁ: {media_diaria:.2f}**")
    else:
        st.error(f"🚨 **ALERTA: {media_diaria:.2f}**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Acumulado", f"{total_acumulado:.2f}")
    c2.metric("Média/Dia", f"{media_diaria:.2f}", delta=round(media_diaria - 3.2, 2))
    c3.metric("Dias Úteis", f"{dias_uteis}")

    st.divider()
    
    df_export = df[['Data', 'Hora', 'Atividade', 'Pontos_Padrao']].copy()
    df_export.columns = ['Data', 'Hora', 'Atividade', 'Pontos']
    df_export['Tecnico'] = nome_usuario
    csv = df_export.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 BAIXAR RELATÓRIO",
        data=csv,
        file_name=f"producao_{nome_usuario.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.subheader("📋 Histórico")
    for i, item in enumerate(reversed(dados_salvos)):
        with st.container():
            col_t, col_d = st.columns([5, 1])
            col_t.write(f"📅 {item['Data']} | **{item['Atividade']}** | {item['Pontos_Padrao']} pts")
            if col_d.button("🗑️", key=f"del_{item['ID']}"):
                dados_brutos.pop(len(dados_brutos) - 1 - i)
                local_storage.setItem("pontos_tecnico", dados_brutos)
                st.rerun()

    st.divider()
    if st.checkbox("Habilitar limpeza (Zerar Ciclo)"):
        if st.button("🔴 APAGAR TUDO"):
            local_storage.deleteItem("pontos_tecnico")
            st.rerun()
else:
    st.info("Aguardando lançamentos...")
