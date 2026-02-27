import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração da página
st.set_page_config(page_title="Gestão de Produtividade", page_icon="💰", layout="wide")
local_storage = LocalStorage()

# 2. Tabelas Base
TABELA_PESOS = {
    "INSTALAÇÃO": 1.00, "MUDANÇA DE ENDEREÇO": 1.00, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "SUPORTE": 0.70, "SOLICITAÇÃO DE SERVIÇO": 0.60, "MIGRAÇÃO DE PLANO": 0.50,
    "Mesh": 0.40, "Repetidor": 0.40, "Roku": 0.40,
    "CAPEX de Retirada": 0.38, "RETIRADA": 0.38, "Retirada de Repetidor": 0.38,
    "Retirada MESH": 0.38, "Retirada Roku": 0.38, "Outros": 0.00
}

def calcular_valor_comissao(porcentagem):
    if porcentagem < 75: return 0.0
    if porcentagem < 80: return 180.0
    if porcentagem < 85: return 210.0
    if porcentagem < 90: return 240.0
    if porcentagem < 95: return 270.0
    if porcentagem < 100: return 300.0
    if porcentagem < 105: return 420.0
    if porcentagem < 110: return 540.0
    if porcentagem < 115: return 660.0
    if porcentagem < 120: return 780.0
    return 900.0

def contar_dias_uteis_mes_atual():
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1)
    if hoje.month == 12:
        ultimo_dia = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
    dias_uteis = 0
    temp_dia = primeiro_dia
    while temp_dia <= ultimo_dia:
        if temp_dia.weekday() != 6: 
            dias_uteis += 1
        temp_dia += timedelta(days=1)
    return dias_uteis

# --- IDENTIFICAÇÃO ---
nome_usuario = local_storage.getItem("nome_tecnico")
if not nome_usuario:
    st.title("🚀 Sistema de Produtividade")
    nome_input = st.text_input("Digite seu nome completo:")
    if st.button("Acessar"):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.rerun()
    st.stop()

# --- INTERFACE ---
st.title(f"Painel de Produtividade: {nome_usuario.split()[0]}")

# Recuperação e Tratamento
dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_validados = []
for item in dados_brutos:
    dados_validados.append({
        "ID": item.get("ID", str(time.time())),
        "Data": item.get("Data", "00/00/0000"),
        "Hora": item.get("Hora", "00:00:00"),
        "Atividade": item.get("Atividade", "Registro"),
        "Pontos": item.get("Pontos", item.get("Points", 0.0))
    })

with st.expander("➕ REGISTRAR SERVIÇO AGORA", expanded=True):
    servico = st.selectbox("O que você finalizou?", list(TABELA_PESOS.keys()))
    if st.button("SALVAR REGISTRO", use_container_width=True):
        novo = {"ID": datetime.now().strftime("%H%M%S%f"), "Data": datetime.now().strftime("%d/%m/%Y"),
                "Hora": datetime.now().strftime("%H:%M:%S"), "Atividade": servico, "Pontos": TABELA_PESOS[servico]}
        dados_validados.append(novo)
        local_storage.setItem("pontos_tecnico", dados_validados)
        st.success("✅ Registrado!")
        time.sleep(0.5)
        st.rerun()

if dados_validados:
    df = pd.DataFrame(dados_validados)
    total_pts = pd.to_numeric(df['Pontos']).sum()
    dias_uteis_mes = contar_dias_uteis_mes_atual()
    percentual = (total_pts / (dias_uteis_mes * 3.2)) * 100
    valor_comissao = calcular_valor_comissao(percentual)

    st.divider()
    st.subheader("💰 Estimativa de Comissão")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pontos Acumulados", f"{total_pts:.2f} pts")
    c2.metric("Produtividade Atual", f"{percentual:.1f}%")
    c3.metric("Bônus Previsto", f"R$ {valor_comissao:.2f}")

    # --- BOTÃO DE APAGAR HISTÓRICO COM SEGURANÇA ---
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Configurações de Dados")
    
    if "confirmar_limpeza" not in st.session_state:
        st.session_state.confirmar_limpeza = False

    if not st.session_state.confirmar_limpeza:
        if st.sidebar.button("🗑️ Limpar Histórico Mensal"):
            st.session_state.confirmar_limpeza = True
            st.rerun()
    else:
        st.sidebar.warning("⚠️ ATENÇÃO: Ao aceitar, todo o seu histórico de lançamentos será apagado permanentemente.")
        if st.sidebar.button("✅ CONFIRMAR E APAGAR TUDO"):
            local_storage.setItem("pontos_tecnico", [])
            st.session_state.confirmar_limpeza = False
            st.success("Histórico apagado!")
            time.sleep(1)
            st.rerun()
        if st.sidebar.button("❌ Cancelar"):
            st.session_state.confirmar_limpeza = False
            st.rerun()

    st.subheader("📋 Histórico")
    for i, item in enumerate(reversed(dados_validados)):
        with st.container():
            col_i, col_b = st.columns([6, 1])
            col_i.write(f"📅 {item['Data']} - **{item['Atividade']}** ({item['Pontos']} pts)")
            if col_b.button("🗑️", key=f"del_{item['ID']}"):
                indice = len(dados_validados) - 1 - i
                dados_validados.pop(indice)
                local_storage.setItem("pontos_tecnico", dados_validados)
                st.rerun()
else:
    st.warning("Nenhum serviço registrado.")
