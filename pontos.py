import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração e Estilo
st.set_page_config(page_title="Sistema de Produtividade Técnica", page_icon="📈", layout="wide")
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
        proximo_mes = hoy.replace(month=hoje.month + 1, day=1)
    ultimo_dia = proximo_mes - timedelta(days=1)
    dias_uteis = 0
    dia_corrente = temp_dia
    while dia_corrente <= ultimo_dia:
        if dia_corrente.weekday() != 6:
            dias_uteis += 1
        dia_corrente += timedelta(days=1)
    return dias_uteis

# --- ACESSO ---
nome_usuario = local_storage.getItem("nome_tecnico")
if not nome_usuario:
    st.title("🚀 Sistema de Gestão Regional")
    nome_input = st.text_input("Digite seu nome completo:")
    if st.button("Entrar no Sistema"):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.rerun()
    st.stop()

# --- TELA PRINCIPAL ---
st.title(f"📈 Dashboard: {nome_usuario}")

dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_validados = []
for item in dados_brutos:
    dados_validados.append({
        "ID": item.get("ID", str(time.time())),
        "Data": item.get("Data", "00/00/0000"),
        "Hora": item.get("Hora", "00:00:00"),
        "Atividade": item.get("Atividade", "Registro"),
        "Pontos": float(item.get("Pontos", 0.0))
    })

# Registro
with st.expander("➕ REGISTRAR ATIVIDADE", expanded=True):
    servico = st.selectbox("Serviço realizado:", list(TABELA_PESOS.keys()))
    if st.button("SALVAR REGISTRO", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": servico,
            "Pontos": TABELA_PESOS[servico]
        }
        local_storage.setItem("pontos_tecnico", dados_validados + [novo])
        st.success("✅ Salvo!")
        time.sleep(0.5)
        st.rerun()

# --- CÁLCULOS DE METAS ---
if dados_validados:
    df = pd.DataFrame(dados_validados)
    total_pts_mes = df['Pontos'].sum()
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    pontos_hoje = df[df['Data'] == hoje_str]['Pontos'].sum()
    
    dias_uteis_mes = contar_dias_uteis_mes_completo()
    meta_total_mes = dias_uteis_mes * 3.2
    produtividade_mes = (total_pts_mes / meta_total_mes) * 100
    comissao = calcular_valor_comissao(produtividade_mes)

    st.divider()

    # --- FEEDBACK DIÁRIO ---
    if pontos_hoje < 3.2:
        falta_hoje = 3.2 - pontos_hoje
        st.warning(f"🚩 **Meta Diária:** Faltam **{falta_hoje:.2f} pontos** para atingir sua meta de hoje (3.20).")
    else:
        st.success(f"✅ **Meta Diária batida!** Você já fez {pontos_hoje:.2f} pontos hoje.")

    # --- FEEDBACK MENSAL ---
    if total_pts_mes < meta_total_mes:
        falta_mes = meta_total_mes - total_pts_mes
        st.info(f"📅 **Meta Mensal:** Faltam **{falta_mes:.2f} pontos** para fechar o mês com média 3.20.")
    else:
        st.balloons()
        st.success(f"🏆 **Incrível!** Você já superou a meta mensal de {meta_total_mes:.2f} pontos!")

    # Painel de Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Pontos Hoje", f"{pontos_hoje:.2f}", delta=f"{pontos_hoje - 3.2:.2f}")
    c2.metric("Produtividade Mês", f"{produtividade_mes:.1f}%")
    c3.metric("Estimativa Comissão", f"R$ {comissao:.2f}")

    # Gráfico
    st.subheader("📊 Evolução Diária")
    df_grafico = df.groupby('Data')['Pontos'].sum().reset_index()
    st.line_chart(df_grafico.set_index('Data'))

    # Barra Lateral
    if st.sidebar.button("🗑️ Limpar Histórico"):
        st.session_state.confirmar = True
    if st.session_state.get("confirmar"):
        if st.sidebar.button("CONFIRMAR LIMPEZA"):
            local_storage.setItem("pontos_tecnico", [])
            st.session_state.confirmar = False
            st.rerun()
        if st.sidebar.button("Cancelar"):
            st.session_state.confirmar = False
            st.rerun()
else:
    st.info("Inicie seus lançamentos para ver o cálculo das metas.")
