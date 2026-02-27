import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage
import time

# 1. Configuração da página
st.set_page_config(page_title="Gestão de Produtividade", page_icon="💰", layout="wide")
local_storage = LocalStorage()

# 2. Tabela de Pesos e Comissão (Fase 2)
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
        if temp_dia.weekday() != 6: # Exclui Domingo
            dias_uteis += 1
        temp_dia += timedelta(days=1)
    return dias_uteis

# --- IDENTIFICAÇÃO DO USUÁRIO ---
nome_usuario = local_storage.getItem("nome_tecnico")
if not nome_usuario:
    st.title("🚀 Sistema de Produtividade")
    nome_input = st.text_input("Digite seu nome completo para iniciar:")
    if st.button("Acessar"):
        if nome_input:
            local_storage.setItem("nome_tecnico", nome_input)
            st.rerun()
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title(f"Painel de Produtividade: {nome_usuario.split()[0]}")
st.error("🚨 **REGRA DE OURO:** Lançou na porta, garantiu a pontuação. Não deixe para depois!")

dados_brutos = local_storage.getItem("pontos_tecnico") or []

# --- LANÇAMENTO DE ATIVIDADES ---
with st.expander("➕ REGISTRAR SERVIÇO AGORA", expanded=True):
    servico = st.selectbox("O que você finalizou?", list(TABELA_PESOS.keys()))
    if st.button("SALVAR REGISTRO", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": servico,
            "Pontos": TABELA_PESOS[servico]
        }
        lista_atualizada = dados_brutos + [novo]
        local_storage.setItem("pontos_tecnico", lista_atualizada)
        st.success("✅ Registrado com sucesso!")
        time.sleep(0.5)
        st.rerun()

# --- CÁLCULOS E EXIBIÇÃO ---
if dados_brutos:
    df = pd.DataFrame(dados_brutos)
    total_pts = df['Pontos'].sum()
    
    dias_uteis_mes = contar_dias_uteis_mes_atual()
    meta_mes_pts = dias_uteis_mes * 3.2
    percentual_atingido = (total_pts / meta_mes_pts) * 100
    valor_comissao = calcular_valor_comissao(percentual_atingido)

    st.divider()
    
    # Área de Comissão Atualizada
    st.subheader("💰 Estimativa de Comissão")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Pontos Acumulados", f"{total_pts:.2f} pts")
    c2.metric("Produtividade Atual", f"{percentual_atingido:.1f}%")
    
    if percentual_atingido >= 75:
        c3.metric("Bônus Previsto", f"R$ {valor_comissao:.2f}", delta="Faixa Atingida", delta_color="normal")
    else:
        c3.metric("Bônus Previsto", "R$ 0,00", delta="Abaixo de 75%", delta_color="inverse")

    st.info(f"💡 Meta do mês: **{meta_mes_pts:.2f} pontos** baseada em {dias_uteis_mes} dias úteis.")

    # Botão de Exportação
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 BAIXAR CONTRAPROVA PARA REGIONAL", csv, f"producao_{nome_usuario}.csv", "text/csv", use_container_width=True)

    # --- HISTÓRICO COM BOTÃO DE APAGAR ---
    st.subheader("📋 Histórico de Lançamentos")
    for i, item in enumerate(reversed(dados_brutos)):
        with st.container():
            col_info, col_btn = st.columns([6, 1])
            col_info.write(f"📅 {item['Data']} às {item['Hora']} - **{item['Atividade']}** ({item['Pontos']} pts)")
            # O botão de apagar voltou aqui:
            if col_btn.button("🗑️", key=f"del_{item['ID']}"):
                indice_original = len(dados_brutos) - 1 - i
                dados_brutos.pop(indice_original)
                local_storage.setItem("pontos_tecnico", dados_brutos)
                st.rerun()
else:
    st.warning("Nenhum serviço registrado neste mês. Comece a lançar para ver sua estimativa de comissão!")
