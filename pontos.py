import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage

# 1. Configuração da página (Deve ser a primeira coisa)
st.set_page_config(page_title="Controle de Produção", page_icon="📈")

# 2. Inicializa o LocalStorage
local_storage = LocalStorage()

# 3. Tabela oficial de pesos
TABELA_PESOS = {
    "CAPEX de Retirada": 0.38, "INSTALAÇÃO": 1.00, "Mesh": 0.40,
    "MIGRAÇÃO DE PLANO": 0.50, "MIGRAÇÃO DE TECNOLOGIA": 1.00,
    "MUDANÇA DE ENDEREÇO": 1.00, "Outros": 0.00, "Repetidor": 0.40,
    "RETIRADA": 0.38, "Retirada de Repetidor": 0.38, "Retirada MESH": 0.38,
    "Retirada Roku": 0.38, "Roku": 0.40, "SOLICITAÇÃO DE SERVIÇO": 0.60, "SUPORTE": 0.70
}

# FUNÇÃO PARA CONTAR DIAS ÚTEIS (EXCLUINDO DOMINGOS)
def contar_dias_sem_domingo(inicio, fim):
    dias = 0
    atual = inicio
    while atual <= fim:
        if atual.weekday() != 6:  # 6 = Domingo
            dias += 1
        atual += timedelta(days=1)
    return dias

st.title("📈 Controle de Produção")

# --- AJUSTE PARA NÃO SUMIR NO F5 ---
# Tenta recuperar os dados. Se retornar None, mantemos uma lista vazia, 
# mas garantimos que o componente teve tempo de carregar.
dados_salvos = local_storage.getItem("pontos_tecnico")

# Se o sistema ainda está carregando o storage, paramos aqui para evitar sobrepor com lista vazia
if dados_salvos is None:
    # Tenta uma segunda vez após um micro-delay interno do componente
    dados_salvos = local_storage.getItem("pontos_tecnico") or []

# Formulário
with st.expander("➕ Registrar Nova Atividade", expanded=True):
    atividade_sel = st.selectbox("Selecione o serviço:", list(TABELA_PESOS.keys()))
    if st.button("Salvar Registro", use_container_width=True):
        novo = {
            "ID": datetime.now().strftime("%H%M%S%f"),
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Atividade": atividade_sel,
            "Points": TABELA_PESOS[atividade_sel]
        }
        # Adiciona ao que já existe
        lista_atualizada = dados_salvos.copy()
        lista_atualizada.append(novo)
        local_storage.setItem("pontos_tecnico", lista_atualizada)
        st.success("✅ Salvo!")
        st.rerun()

st.divider()

if dados_salvos:
    df = pd.DataFrame(dados_salvos)
    # Garante que a coluna de pontos seja numérica
    df['Points'] = pd.to_numeric(df['Points'])
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    
    total_acumulado = df['Points'].sum()
    data_inicio = df['Data_dt'].min()
    data_hoje = datetime.now()
    
    dias_corridos_uteis = contar_dias_sem_domingo(data_inicio, data_hoje)
    divisor = dias_corridos_uteis if dias_corridos_uteis > 0 else 1
    media_diaria = total_acumulado / divisor

    # Status de Performance
    if media_diaria >= 3.2:
        st.success(f"✅ **MÉDIA EXCELENTE: {media_diaria:.2f}**")
    elif media_diaria >= 2.8:
        st.warning(f"⚡ **QUASE LÁ: {media_diaria:.2f}**")
    else:
        st.error(f"🚨 **ALERTA: {media_diaria:.2f}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Acumulado", f"{total_acumulado:.2f}")
    col2.metric("Média Real", f"{media_diaria:.2f}", delta=round(media_diaria - 3.2, 2))
    col3.metric("Dias Úteis", f"{dias_corridos_uteis}")

    st.divider()
    
    # Histórico
    st.subheader("📋 Histórico")
    for i, item in enumerate(reversed(dados_salvos)):
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.write(f"📅 {item['Data']} | **{item['Atividade']}** | {item.get('Points', 0)} pts")
            if c2.button("🗑️", key=f"del_{item['ID']}"):
                idx_real = len(dados_salvos) - 1 - i
                dados_salvos.pop(idx_real)
                local_storage.setItem("pontos_tecnico", dados_salvos)
                st.rerun()

    if st.checkbox("Habilitar limpeza"):
        if st.button("🔴 ZERAR TUDO"):
            local_storage.deleteAll()
            st.rerun()
else:
    st.info("Nenhum dado encontrado. Se você acabou de salvar, aguarde um segundo ou verifique se os cookies do navegador estão ativos.")
