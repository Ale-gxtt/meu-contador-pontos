import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração e Estilo
st.set_page_config(page_title="Sistema de Produtividade Técnica", page_icon="💰", layout="wide")
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

# PONTO CRUCIAL: Contagem de dias úteis (Segunda a Sábado)
def contar_dias_uteis_mes_completo():
    hoje = datetime.now()
    # Primeiro dia do mês atual
    temp_dia = hoje.replace(day=1)
    # Primeiro dia do próximo mês
    if hoje.month == 12:
        proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
    else:
        proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
    
    ultimo_dia = proximo_mes - timedelta(days=1)
    
    dias_uteis = 0
    dia_corrente = temp_dia
    while dia_corrente <= ultimo_dia:
        if dia_corrente.weekday() != 6: # 6 é Domingo. Se for diferente de 6, conta.
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
st.title(f"Painel de Produtividade: {nome_usuario}")

# Recuperação de dados
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
with st.expander("➕ REGISTRAR ATIVIDADE", expanded=True):
    servico = st.selectbox("Selecione o serviço:", list(TABELA_PESOS.keys()))
    if st.button("SALVAR REGISTRO", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": servico,
            "Pontos": TABELA_PESOS[servico]
        }
        lista = dados_validados + [novo]
        local_storage.setItem("pontos_tecnico", lista)
        st.success("✅ Atividade salva com sucesso!")
        time.sleep(0.5)
        st.rerun()

# --- RESULTADOS ---
if dados_validados:
    df = pd.DataFrame(dados_validados)
    total_pts = pd.to_numeric(df['Pontos']).sum()
    
    dias_uteis = contar_dias_uteis_mes_completo()
    meta_total = dias_uteis * 3.2
    produtividade = (total_pts / meta_total) * 100
    comissao = calcular_valor_comissao(produtividade)

    st.divider()
    st.subheader("💰 Estimativa de Comissão")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Pontos Totais", f"{total_pts:.2f}")
    c2.metric("Produtividade", f"{produtividade:.1f}%")
    c3.metric("Bônus Previsto", f"R$ {comissao:.2f}")

    st.caption(f"ℹ️ Baseado em **{dias_uteis} dias úteis** neste mês (Meta: {meta_total:.2f} pts). Domingos não contabilizados.")

    # --- BARRA LATERAL (CONFIGURAÇÕES) ---
    st.sidebar.title("⚙️ Opções")
    if "limpar_clicado" not in st.session_state:
        st.session_state.limpar_clicado = False

    if not st.session_state.limpar_clicado:
        if st.sidebar.button("🗑️ Limpar Histórico do Mês"):
            st.session_state.limpar_clicado = True
            st.rerun()
    else:
        st.sidebar.warning("⚠️ VOCÊ TEM CERTEZA? Isso apagará todos os seus registros deste mês.")
        if st.sidebar.button("✅ SIM, APAGAR TUDO"):
            local_storage.setItem("pontos_tecnico", [])
            st.session_state.limpar_clicado = False
            st.rerun()
        if st.sidebar.button("❌ Cancelar"):
            st.session_state.limpar_clicado = False
            st.rerun()

    # Histórico
    st.subheader("📋 Histórico Mensal")
    for i, item in enumerate(reversed(dados_validados)):
        with st.container():
            col_txt, col_del = st.columns([6, 1])
            col_txt.write(f"📅 {item['Data']} | **{item['Atividade']}** ({item['Pontos']} pts)")
            if col_del.button("🗑️", key=f"del_{item['ID']}"):
                idx = len(dados_validados) - 1 - i
                dados_validados.pop(idx)
                local_storage.setItem("pontos_tecnico", dados_validados)
                st.rerun()
else:
    st.info("Aguardando lançamentos para calcular produtividade.")
