import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração e Estilo
st.set_page_config(page_title="Sistema de Produtividade Técnica", page_icon="📈", layout="wide")
local_storage = LocalStorage()

# Estilização para as métricas ficarem maiores
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 35px; }
    </style>
    """, unsafe_allow_html=True)

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
        if dia_corrente.weekday() != 6:
            dias_uteis += 1
        dia_corrente += timedelta(days=1)
    return dias_uteis

# --- ACESSO ---
nome_usuario = local_storage.getItem("nome_tecnico")
if not nome_usuario:
    st.title("🚀 Sistema de Gestão Regional")
    nome_input = st.text_input("Digite seu nome completo para começar:")
    if st.button("Entrar no Sistema"):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.rerun()
    st.stop()

# --- TELA PRINCIPAL ---
st.title(f"📈 Desempenho: {nome_usuario}")

dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_validados = []
for item in dados_brutos:
    dados_validados.append({
        "ID": item.get("ID", str(time.time())),
        "Data": item.get("Data", "00/00/0000"),
        "Hora": item.get("Hora", "00:00:00"),
        "Atividade": item.get("Atividade", "Registro"),
        "Pontos": item.get("Pontos", 0.0)
    })

# Registro
with st.expander("➕ REGISTRAR ATIVIDADE EM CAMPO", expanded=True):
    servico = st.selectbox("Selecione o serviço finalizado:", list(TABELA_PESOS.keys()))
    if st.button("SALVAR REGISTRO", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": servico,
            "Pontos": TABELA_PESOS[servico]
        }
        local_storage.setItem("pontos_tecnico", dados_validados + [novo])
        st.success(f"🎯 {servico} registrado!")
        time.sleep(0.5)
        st.rerun()

# --- RESULTADOS INTERATIVOS ---
if dados_validados:
    df = pd.DataFrame(dados_validados)
    df['Pontos'] = pd.to_numeric(df['Pontos'])
    total_pts = df['Pontos'].sum()
    
    dias_uteis = contar_dias_uteis_mes_completo()
    meta_mensal = dias_uteis * 3.2
    produtividade = (total_pts / meta_mensal) * 100
    comissao = calcular_valor_comissao(produtividade)

    # Cálculo de Performance Diária (Seta Verde/Vermelha)
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    pontos_hoje = df[df['Data'] == hoje_str]['Pontos'].sum()
    desvio_hoje = pontos_hoje - 3.2

    st.divider()

    # Painel Visual de Métricas
    c1, c2, c3 = st.columns(3)
    
    # Seta Verde/Vermelha baseada na meta diária de 3.2
    c1.metric("Produção Hoje", f"{pontos_hoje:.2f} pts", delta=f"{desvio_hoje:.2f} vs Meta 3.2", delta_color="normal")
    
    # Produtividade com cor dinâmica
    cor_prod = "green" if produtividade >= 100 else "orange" if produtividade >= 75 else "red"
    c2.markdown(f"**Produtividade Mensal** \n <h2 style='color:{cor_prod};'>{produtividade:.1f}%</h2>", unsafe_allow_html=True)
    
    c3.metric("Estimativa de Comissão", f"R$ {comissao:.2f}")

    # Gráfico de Evolução Diária
    st.subheader("📊 Evolução da Pontuação no Mês")
    df_grafico = df.groupby('Data')['Pontos'].sum().reset_index()
    st.line_chart(df_grafico.set_index('Data'), color="#29b5e8")

    st.divider()

    # --- BARRA LATERAL ---
    st.sidebar.title("⚙️ Painel de Controle")
    if st.sidebar.button("🗑️ Limpar Tudo (Segurança)"):
        st.session_state.confirmar = True

    if st.session_state.get("confirmar"):
        st.sidebar.error("Confirmar limpeza total?")
        if st.sidebar.button("✅ SIM, APAGAR"):
            local_storage.setItem("pontos_tecnico", [])
            st.session_state.confirmar = False
            st.rerun()
        if st.sidebar.button("❌ CANCELAR"):
            st.session_state.confirmar = False
            st.rerun()

    # Histórico detalhado
    st.subheader("📋 Detalhamento dos Serviços")
    st.dataframe(df[['Data', 'Hora', 'Atividade', 'Pontos']].iloc[::-1], use_container_width=True)

else:
    st.info("👋 Bem-vindo! Registre seu primeiro serviço para ativar o gráfico de desempenho.")
