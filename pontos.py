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
        # CORREÇÃO AQUI: era 'hoy', agora é 'hoje'
        proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
    ultimo_dia = proximo_mes - timedelta(days=1)
    dias_uteis = 0
    dia_corrente = temp_dia
    while dia_corrente <= ultimo_dia:
        if dia_corrente.weekday() != 6: # Domingo (6) não conta
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
st.title(f"📈 Dashboard: {nome_usuario}")

# RECUPERAÇÃO SEGURA DOS DADOS (Evita KeyError)
dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_validados = []
for item in dados_brutos:
    if isinstance(item, dict):
        dados_validados.append({
            "ID": item.get("ID", str(time.time())),
            "Data": item.get("Data", "00/00/0000"),
            "Hora": item.get("Hora", "00:00:00"),
            "Atividade": item.get("Atividade", "Registro"),
            "Pontos": float(item.get("Pontos", 0.0))
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
        # Adiciona e salva
        dados_validados.append(novo)
        local_storage.setItem("pontos_tecnico", dados_validados)
        st.success(f"🎯 {servico} registrado!")
        time.sleep(0.5)
        st.rerun()

# --- RESULTADOS INTERATIVOS ---
if dados_validados:
    df = pd.DataFrame(dados_validados)
    total_pts_mes = df['Pontos'].sum()
    
    # Meta Diária
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    pontos_hoje = df[df['Data'] == hoje_str]['Pontos'].sum()
    
    # Meta Mensal
    dias_uteis = contar_dias_uteis_mes_completo()
    meta_mensal_total = dias_uteis * 3.2
    produtividade_mes = (total_pts_mes / meta_mensal_total) * 100
    comissao = calcular_valor_comissao(produtividade_mes)

    st.divider()

    # --- MENSAGENS DE METAS (DIÁRIA E MENSAL) ---
    col_msg1, col_msg2 = st.columns(2)
    
    with col_msg1:
        if pontos_hoje < 3.2:
            st.warning(f"🚩 **Hoje:** Faltam **{(3.2 - pontos_hoje):.2f} pts** para a meta diária.")
        else:
            st.success(f"✅ **Hoje:** Meta de 3.2 batida! ({pontos_hoje:.2f} pts)")

    with col_msg2:
        if total_pts_mes < meta_mensal_total:
            st.info(f"📅 **Mês:** Faltam **{(meta_mensal_total - total_pts_mes):.2f} pts** para o objetivo mensal.")
        else:
            st.success(f"🏆 **Mês:** Meta mensal atingida!")

    # Painel Visual
    c1, c2, c3 = st.columns(3)
    c1.metric("Pontos Hoje", f"{pontos_hoje:.2f}", delta=f"{pontos_hoje - 3.2:.2f}")
    c2.metric("Produtividade Mês", f"{produtividade_mes:.1f}%")
    c3.metric("Estimativa Comissão", f"R$ {comissao:.2f}")

    # Gráfico de Evolução
    st.subheader("📊 Evolução da Pontuação")
    df_grafico = df.groupby('Data')['Pontos'].sum().reset_index()
    st.line_chart(df_grafico.set_index('Data'))

    st.divider()

    # --- BARRA LATERAL (CONFIGURAÇÕES) ---
    st.sidebar.title("⚙️ Painel de Controle")
    if "confirmar_limpeza" not in st.session_state:
        st.session_state.confirmar_limpeza = False

    if not st.session_state.confirmar_limpeza:
        if st.sidebar.button("🗑️ Limpar Histórico do Mês"):
            st.session_state.confirmar_limpeza = True
            st.rerun()
    else:
        st.sidebar.error("⚠️ Apagar tudo?")
        if st.sidebar.button("✅ SIM"):
            local_storage.setItem("pontos_tecnico", [])
            st.session_state.confirmar_limpeza = False
            st.rerun()
        if st.sidebar.button("❌ NÃO"):
            st.session_state.confirmar_limpeza = False
            st.rerun()

    # Histórico detalhado com opção de apagar um por um
    st.subheader("📋 Detalhamento dos Serviços")
    for i, item in enumerate(reversed(dados_validados)):
        with st.container():
            col_info, col_del = st.columns([6, 1])
            col_info.write(f"📅 {item['Data']} às {item['Hora']} - **{item['Atividade']}** ({item['Pontos']} pts)")
            if col_del.button("🗑️", key=f"del_{item['ID']}"):
                idx_original = len(dados_validados) - 1 - i
                dados_validados.pop(idx_original)
                local_storage.setItem("pontos_tecnico", dados_validados)
                st.rerun()
else:
    st.info("👋 Inicie seus lançamentos para ativar o acompanhamento de metas e o gráfico.")
