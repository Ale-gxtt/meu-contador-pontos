import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração e Estilo
st.set_page_config(page_title="Controle de Pontos & Comissão", page_icon="💰", layout="wide")
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
    temp_dia = hoy = hoje.replace(day=1)
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

# --- ACESSO PERSISTENTE ---
if "nome_tecnico" not in st.session_state:
    st.session_state.nome_tecnico = local_storage.getItem("nome_tecnico")

if not st.session_state.nome_tecnico:
    st.title("🚀 Sistema de Controle de Pontos & Comissão")
    st.markdown("### Bem-vindo à sua ferramenta de produtividade!")
    nome_input = st.text_input("Para começar, digite seu nome completo:")
    if st.button("Configurar Perfil e Acessar ➔", use_container_width=True):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.session_state.nome_tecnico = nome_input
            st.success("Tudo pronto! Entrando...")
            time.sleep(1.2)
            st.rerun()
    st.stop()

nome_usuario = st.session_state.nome_tecnico

# --- TELA PRINCIPAL ---
st.title(f"📊 Painel: {nome_usuario}")

dados_brutos = local_storage.getItem("pontos_tecnico") or []
dados_validados = []
for item in dados_brutos:
    if isinstance(item, dict):
        pts = item.get("Pontos") if item.get("Pontos") is not None else item.get("Points", 0.0)
        dados_validados.append({
            "ID": item.get("ID", str(time.time())),
            "Data": item.get("Data", "00/00/0000"),
            "Atividade": item.get("Atividade", "Registro"),
            "Pontos": float(pts)
        })

# Registro
with st.expander("➕ LANÇAR NOVO SERVIÇO", expanded=True):
    servico = st.selectbox("Selecione o serviço finalizado:", list(TABELA_PESOS.keys()))
    if st.button("SALVAR REGISTRO", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Atividade": servico,
            "Pontos": TABELA_PESOS[servico]
        }
        dados_validados.append(novo)
        local_storage.setItem("pontos_tecnico", dados_validados)
        st.success("🎯 Salvo!")
        time.sleep(0.7)
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
    c1, c2, c3 = st.columns(3)
    c1.metric("Hoje", f"{pts_hoje:.2f} pts", delta=f"{pts_hoje - 3.2:.2f} vs Meta")
    c2.metric("Mês", f"{produtividade:.1f}%")
    c3.metric("Comissão", f"R$ {comissao:.2f}")

    st.write(f"**Meta Mensal ({total_pts_mes:.1f} de {meta_mensal:.1f} pts)**")
    st.progress(min(produtividade / 100, 1.0))

    # --- BOTÃO PARA BAIXAR HISTÓRICO ---
    st.subheader("📥 Exportar Dados")
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📄 BAIXAR HISTÓRICO EM EXCEL (CSV)",
        data=csv,
        file_name=f"produtividade_{nome_usuario}_{datetime.now().strftime('%m_%Y')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()

    # --- BARRA LATERAL ---
    st.sidebar.title("⚙️ Opções")
    if st.sidebar.button("👤 TROCAR USUÁRIO / SAIR"):
        local_storage.setItem("nome_tecnico", "")
        st.session_state.nome_tecnico = ""
        time.sleep(1.0)
        st.rerun()

    if "confirmar_limpeza" not in st.session_state:
        st.session_state.confirmar_limpeza = False

    if not st.session_state.confirmar_limpeza:
        if st.sidebar.button("🗑️ Limpar Mês"):
            st.session_state.confirmar_limpeza = True
            st.rerun()
    else:
        if st.sidebar.button("✅ SIM, LIMPAR TUDO"):
            local_storage.setItem("pontos_tecnico", [])
            time.sleep(1.0)
            st.session_state.confirmar_limpeza = False
            st.rerun()
        if st.sidebar.button("❌ CANCELAR"):
            st.session_state.confirmar_limpeza = False
            st.rerun()

    # Histórico Visual
    st.subheader("📋 Lançamentos Realizados")
    for i, item in enumerate(reversed(dados_validados)):
        with st.container():
            col_txt, col_del = st.columns([6, 1])
            col_txt.write(f"📅 {item['Data']} | **{item['Atividade']}** ({item['Pontos']} pts)")
            if col_del.button("🗑️", key=f"del_{item['ID']}"):
                idx = len(dados_validados) - 1 - i
                dados_validados.pop(idx)
                local_storage.setItem("pontos_tecnico", dados_validados)
                st.toast("Removendo...")
                time.sleep(0.7)
                st.rerun()
else:
    st.info("Aguardando lançamentos.")
    if st.sidebar.button("👤 TROCAR USUÁRIO / SAIR"):
        local_storage.setItem("nome_tecnico", "")
        st.session_state.nome_tecnico = ""
        time.sleep(1.0)
        st.rerun()
