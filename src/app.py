import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import anthropic
import streamlit as st
from agente import AgenteFinanceiro
from config import AGENT_NAME


# ── Configuração da página ────────────────────────────────────────────────────

st.set_page_config(
    page_title=f"{AGENT_NAME} · Assistente Financeiro",
    page_icon="💰",
    layout="centered",
)

# ── Inicialização do agente (uma vez por sessão) ──────────────────────────────

if "agente" not in st.session_state:
    st.session_state.agente = AgenteFinanceiro()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

agente: AgenteFinanceiro = st.session_state.agente

# ── Sidebar com perfil do cliente ────────────────────────────────────────────

with st.sidebar:
    st.title("👤 Perfil do Cliente")
    perfil = agente.perfil

    st.markdown(f"**Nome:** {perfil.get('nome')}")
    st.markdown(f"**Perfil:** {perfil.get('tipo')}")
    st.markdown(f"**Objetivo:** {perfil.get('objetivo_principal')}")
    st.markdown(f"**Horizonte:** {perfil.get('horizonte')}")
    st.markdown(f"**Renda mensal:** R$ {perfil.get('renda_mensal'):,.2f}")

    st.divider()

    if st.button("🔄 Nova conversa", use_container_width=True):
        agente.resetar()
        st.session_state.mensagens = []
        st.rerun()

# ── Cabeçalho ─────────────────────────────────────────────────────────────────

st.title(f"💬 {AGENT_NAME}")
st.caption("Sua assistente de planejamento financeiro pessoal")
st.divider()

# ── Histórico de mensagens ────────────────────────────────────────────────────

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input do usuário ──────────────────────────────────────────────────────────

if prompt := st.chat_input("Digite sua mensagem..."):

    # Exibe mensagem do usuário
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera e exibe resposta do agente
    with st.chat_message("assistant"):
        with st.spinner(f"{AGENT_NAME} está analisando..."):
            resposta = agente.chat(prompt)
        st.markdown(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})