import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração e Estilo
st.set_page_config(page_title="Produtividade Técnica", page_icon="📈", layout="wide")
local_storage = LocalStorage()

# 2. Tabela de Pesos
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

def contar_dias_uteis_mes_completo():
    hoje = datetime.now()
    temp_dia = hoje.replace(day=1)
    if hoje.month == 12:
        proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
    else:
        proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
    ultimo_dia = proximo_mes - timedelta(days=1)
    dias_uteis = 0
    dia_corrente = temp_dia
    while dia_corrente <= ultimo_dia:
        if dia_corrente.weekday() != 6: # Domingo não conta
            dias_uteis += 1
        dia_corrente += timedelta(days=1)
    return dias_uteis

# --- ACESSO ---
nome_usuario = local_storage.getItem("nome_tecnico")
if not nome_usuario:
    st.title("🚀 Sistema de Gestão")
    nome_input = st.text_input("Seu nome completo:")
    if st.button("Entrar"):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.rerun()
    st.stop()

# --- TELA PRINCIPAL ---
st.title(f"📊 Painel: {nome_usuario}")

dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_validados = []
for item in dados_brutos:
    if isinstance(item, dict):
        dados_validados.append({
            "ID": item.get("ID", str(time.time())),
            "Data": item.get("Data", "00/00/0000"),
            "Pontos": float(item.get("Pontos", 0.0))
        })

# Registro Simples
with st.expander("➕ LANÇAR SERVIÇO", expanded=True):
    servico = st.selectbox("O que você finalizou?", list(TABELA_PESOS.keys()))
    if st.button("SALVAR", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Atividade": servico,
            "Pontos": TABELA_PESOS[servico]
        }
        dados_validados.append(novo)
        local_storage.setItem("pontos_tecnico", dados_validados)
        st.success("🎯 Salvo!")
        time.sleep(0.4)
        st.rerun()

if dados_validados:
    df = pd.DataFrame(dados_validados)
    total_pts_mes = df['Pontos'].sum()
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    pts_hoje = df[df['Data'] == hoje_str]['Pontos'].sum()
    
    dias_uteis = contar_dias_uteis_mes_completo()
    meta_mensal = dias_uteis * 3.2
    produtividade = (total_pts_mes / meta_mensal) * 100
    comissao = calcular_valor_comissao(produtividade)

    st.divider()

    # --- MÉTRICAS SIMPLES ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Hoje", f"{pts_hoje:.2f} pts", delta=f"{pts_hoje - 3.2:.2f}")
    c2.metric("Mês", f"{produtividade:.1f}%")
    c3.metric("Comissão", f"R$ {comissao:.2f}")

    # --- BARRA DE PROGRESSO (MAIS SIMPLES QUE GRÁFICO) ---
    st.write(f"**Progresso da Meta Mensal ({total_pts_mes:.1f} de {meta_mensal:.1f} pts)**")
    progresso = min(produtividade / 100, 1.0)
    st.progress(progresso)

    # Mensagens de Apoio
    if pts_hoje < 3.2:
        st.info(f"Faltam **{(3.2 - pts_hoje):.2f} pontos** para a meta de hoje.")
    if produtividade < 100:
        st.write(f"Faltam **{(meta_mensal - total_pts_mes):.2f} pontos** para atingir 100% no mês.")

    st.divider()

    # Histórico Simplificado
    st.subheader("📋 Últimos Lançamentos")
    st.table(df[['Data', 'Pontos']].tail(5)) # Mostra só os últimos 5 de forma simples

    # Barra Lateral
    if st.sidebar.button("🗑️ Limpar Mês"):
        local_storage.setItem("pontos_tecnico", [])
        st.rerun()
else:
    st.info("Aguardando lançamentos.")
